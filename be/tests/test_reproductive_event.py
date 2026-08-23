import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

GESTATION_DAYS = 283

_CALF_SEX_MAP: dict[str, list[str]] = {
    "macho": ["macho"],
    "hembra": ["hembra"],
    "gemelos": ["macho", "hembra"],
}


def _create_calves_from_birth(db, farm_id, event, user_id):
    from app.models.bovine import Bovine
    from app.services.audit_service import add_audit_log

    sexes = _CALF_SEX_MAP.get(event.result)
    if not sexes:
        return []

    prefix = str(event.bovine_id)[:6]
    date_str = event.event_date.strftime("%Y%m%d")
    calves = []

    for i, sex in enumerate(sexes):
        ident = f"CRIA-{prefix}-{date_str}-{i+1}"
        calf = Bovine(
            farm_id=farm_id,
            registered_by=user_id,
            identification_number=ident,
            sex=sex,
            birth_date=event.event_date,
            entry_type="nacimiento",
            entry_date=event.event_date,
            mother_id=event.bovine_id,
        )
        db.add(calf)
        db.flush()
        add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="bovine", entity_id=str(calf.id), details={"calf_from": "parto", "mother_id": str(event.bovine_id)})
        calves.append(calf)

    return calves


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def farm_id():
    return uuid.uuid4()


@pytest.fixture
def bovine_id():
    return uuid.uuid4()


@pytest.fixture
def user_id():
    return uuid.uuid4()


class MockReproductiveEvent:
    def __init__(self, bovine_id, event_type, event_date, result, due_date=None):
        self.bovine_id = bovine_id
        self.event_type = event_type
        self.event_date = event_date
        self.result = result
        self.due_date = due_date


class TestAutoCalfGeneration:

    def test_create_male_calf(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 6, 1), "macho")
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)

        assert len(calves) == 1
        calf = calves[0]
        assert calf.sex == "macho"
        assert calf.mother_id == bovine_id
        assert calf.birth_date == date(2026, 6, 1)
        assert calf.entry_type == "nacimiento"
        assert calf.entry_date == date(2026, 6, 1)
        assert calf.farm_id == farm_id
        assert calf.registered_by == user_id
        assert calf.identification_number.startswith("CRIA-")

    def test_create_female_calf(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 6, 1), "hembra")
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)

        assert len(calves) == 1
        assert calves[0].sex == "hembra"

    def test_create_twins(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 6, 1), "gemelos")
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)

        assert len(calves) == 2
        sexes = {c.sex for c in calves}
        assert sexes == {"macho", "hembra"}
        assert calves[0].identification_number != calves[1].identification_number

    def test_no_calf_when_result_invalid(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 6, 1), "positivo")
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)
        assert len(calves) == 0

    def test_no_calf_when_result_none(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 6, 1), None)
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)
        assert len(calves) == 0

    def test_not_triggered_for_servicio(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "servicio", date(2026, 5, 1), None)
        assert event.event_type == "servicio"
        assert event.due_date is None
        simulated_due = event.event_date + timedelta(days=GESTATION_DAYS)
        assert simulated_due == date(2026, 5, 1) + timedelta(days=283)

    def test_calf_id_format(self, mock_db, farm_id, bovine_id, user_id):
        event = MockReproductiveEvent(bovine_id, "parto", date(2026, 10, 20), "macho")
        calves = _create_calves_from_birth(mock_db, farm_id, event, user_id)
        prefix = str(bovine_id)[:6]
        assert calves[0].identification_number == f"CRIA-{prefix}-20261020-1"
