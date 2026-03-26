import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm, UserFarm
from app.models.role import Role
from app.schemas.farm import FarmCreate, FarmUpdate
from app.services.audit_service import add_audit_log


def create_farm(db: Session, farm_data: FarmCreate, owner_id: uuid.UUID) -> Farm:
    """Crea una nueva finca y la persiste en la BD."""
    # Verificar que el identificador no esté duplicado
    existing = db.execute(
        select(Farm).where(Farm.farm_identifier == farm_data.farm_identifier)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una finca con ese identificador",
        )

    farm = Farm(
        owner_id=owner_id,
        name=farm_data.name,
        address=farm_data.address,
        department_id=farm_data.department_id,
        city_municipality=farm_data.city_municipality,
        total_area=farm_data.total_area,
        area_unit=farm_data.area_unit,
        purpose_id=farm_data.purpose_id,
        farm_identifier=farm_data.farm_identifier,
        phone=farm_data.phone,
    )
    db.add(farm)
    db.flush()

    # Asignar rol Administrador al creador de la finca
    admin_role = db.execute(
        select(Role).where(Role.name == "Administrador")
    ).scalar_one_or_none()
    if admin_role:
        user_farm = UserFarm(
            user_id=owner_id,
            farm_id=farm.id,
            role_id=admin_role.id,
            assigned_by=owner_id,
        )
        db.add(user_farm)

    db.commit()
    db.refresh(farm)
    add_audit_log(
        db,
        user_id=str(owner_id),
        action="create",
        entity="farm",
        entity_id=str(farm.id),
        details={"name": farm.name},
    )
    db.commit()
    return farm


def get_farms_by_owner(db: Session, owner_id: uuid.UUID) -> list[Farm]:
    """Retorna todas las fincas activas del usuario."""
    stmt = (
        select(Farm)
        .where(Farm.owner_id == owner_id, Farm.is_active.is_(True))
        .order_by(Farm.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_farm_by_id(db: Session, farm_id: uuid.UUID, owner_id: uuid.UUID) -> Farm:
    """Retorna una finca por ID, verificando que pertenezca al usuario."""
    stmt = select(Farm).where(Farm.id == farm_id, Farm.owner_id == owner_id)
    farm = db.execute(stmt).scalar_one_or_none()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finca no encontrada",
        )
    return farm


def update_farm(db: Session, farm_id: uuid.UUID, owner_id: uuid.UUID, data: FarmUpdate) -> Farm:
    farm = get_farm_by_id(db, farm_id, owner_id)

    dup = db.execute(
        select(Farm).where(Farm.farm_identifier == data.farm_identifier, Farm.id != farm_id)
    ).scalar_one_or_none()
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una finca con ese identificador",
        )

    farm.name = data.name
    farm.address = data.address
    farm.department_id = data.department_id
    farm.city_municipality = data.city_municipality
    farm.total_area = data.total_area
    farm.area_unit = data.area_unit
    farm.purpose_id = data.purpose_id
    farm.farm_identifier = data.farm_identifier
    farm.phone = data.phone
    db.commit()
    db.refresh(farm)
    add_audit_log(
        db,
        user_id=str(owner_id),
        action="update",
        entity="farm",
        entity_id=str(farm.id),
        details={"name": farm.name},
    )
    db.commit()
    return farm


def delete_farm(db: Session, farm_id: uuid.UUID, owner_id: uuid.UUID) -> None:
    farm = get_farm_by_id(db, farm_id, owner_id)
    farm.is_active = False
    add_audit_log(
        db,
        user_id=str(owner_id),
        action="delete",
        entity="farm",
        entity_id=str(farm.id),
        details={"name": farm.name},
    )
    db.commit()


def create_farms_bulk(db: Session, items: list[FarmCreate], owner_id: uuid.UUID) -> list[Farm]:
    created: list[Farm] = []
    for item in items:
        created.append(create_farm(db, item, owner_id))
    return created
