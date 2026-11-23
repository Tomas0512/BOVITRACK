"""
╔════════════════════════════════════════════════════════════════════════════╗
║ ROUTER: routers/calves.py                                                 ║
║ PROPÓSITO: Endpoints HTTP para gestión de terneros (HU007)                ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Rutas (endpoints) HTTP que exponen la funcionalidad de terneros:        ║
║   - GET /api/v1/farms/{farm_id}/calves → Listar terneros                 ║
║   - GET /api/v1/farms/{farm_id}/calves/{bovine_id} → Detalle             ║
║   - GET /api/v1/farms/{farm_id}/calves/{bovine_id}/weights → Historial   ║
║   - POST /api/v1/farms/{farm_id}/calves/{bovine_id}/weights → Registrar  ║
║   - GET /api/v1/farms/{farm_id}/calves/summary → Resumen global          ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   Que el frontend (React) pueda hacer peticiones HTTP para:               ║
║   - Mostrar lista de terneros (CalfList.tsx)                              ║
║   - Graficar curva de crecimiento (GrowthChart.tsx)                       ║
║   - Registrar pesajes nuevos                                              ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   Cada endpoint se protege con:                                            ║
║   - Autenticación JWT (get_current_user)                                  ║
║   - Validación de acceso a finca (require_permission)                     ║
║   - Validación de datos (Pydantic)                                        ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import date

from fastapi import APIRouter, Body, Depends, Path, Query, Request, status

from app.modules.livestock.dependencies import get_calf_service, get_current_user, require_permission
from app.modules.livestock.schemas import BovineResponse
from app.modules.livestock.schemas.calf import (
    CalfGrowthMetricsResponse,
    CalfListResponse,
    CalfSummaryResponse,
    WeightRecordCreate,
    WeightRecordResponse,
)
from app.modules.livestock.service import CalfService
from app.core.limiter import limiter
from app.shared.ports import CurrentUser

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURACIÓN DEL ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/calves",
    tags=["Terneros (HU007)"],
)

# ═══════════════════════════════════════════════════════════════════════════
# 📋 ENDPOINTS DE LECTURA
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "",
    response_model=list[CalfListResponse],
    summary="Listar terneros de una finca",
    description="""
    ¿Qué? Lista todos los terneros de una finca con filtros por edad y estado.

    ¿Parámetros?
      farm_id: UUID de la finca
      max_age_days: Edad máxima en días (default 365)
      min_age_days: Edad mínima en días (default 0)
      status: Filtro por estado (opcional)

    ¿Retorna?
      Array de terneros con datos básicos

    ¿Correspondencia HU?
      HU007 Task 7.1: Endpoint/vista de terneros por edad/estado
    """,
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
@limiter.limit("10/minute")
def list_calves(
    request: Request,
    farm_id: uuid.UUID = Path(..., description="ID de la finca"),
    max_age_days: int = Query(365, ge=0, le=1825, description="Edad máxima en días"),
    min_age_days: int = Query(0, ge=0, le=365, description="Edad mínima en días"),
    status: str | None = Query(None, description="Filtro por estado"),
    service: CalfService = Depends(get_calf_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[CalfListResponse]:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se reciben los parámetros de la URL y query
    2. Se valida que el usuario tiene acceso a la finca (via require_permission)
    3. Se llama al servicio para obtener los terneros
    4. Se convierten a response models (Pydantic)
    5. Se retornan como JSON al frontend
    """

    # Obtener terneros del servicio
    calves = service.list_calves(
        farm_id,
        max_age_days=max_age_days,
        min_age_days=min_age_days,
        status_filter=status,
    )

    # Convertir a response models (serialización)
    return [
        CalfListResponse(
            id=calf.id,
            identification_number=calf.identification_number,
            name=calf.name,
            sex=calf.sex,
            birth_date=calf.birth_date,
            current_weight_kg=float(calf.current_weight or 0),
            age_days=(date.today() - calf.birth_date).days,
        )
        for calf in calves
    ]


@router.get(
    "/summary",
    response_model=CalfSummaryResponse,
    summary="Resumen global de terneros en la finca",
    description="""
    ¿Qué? Obtiene métricas resumidas de todos los terneros de una finca.

    ¿Retorna?
      {
        total_calves: int,
        calves_0_30_days: int,
        calves_31_90_days: int,
        calves_91_365_days: int,
        average_weight_kg: float,
        average_daily_gain: float
      }

    ¿Correspondencia HU?
      HU007 Task 7.3: Componente CalfList con indicadores de crecimiento
    """,
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
@limiter.limit("20/minute")
def get_calf_summary(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    service: CalfService = Depends(get_calf_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> CalfSummaryResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se obtiene el resumen del servicio
    2. Se retorna directamente como JSON
    """

    summary = service.get_calf_summary_by_farm(farm_id)

    return CalfSummaryResponse(**summary)


@router.get(
    "/{bovine_id}",
    response_model=CalfGrowthMetricsResponse,
    summary="Detalle de un ternero con métricas de crecimiento",
    description="""
    ¿Qué? Obtiene un ternero específico con todas sus métricas de crecimiento.

    ¿Retorna?
      {
        bovine: BovineResponse,
        metrics: {
          current_weight_kg,
          birth_weight_kg,
          days_old,
          daily_gain_kg,
          expected_weight_kg,
          growth_percentage,
          feeding_plan
        }
      }

    ¿Correspondencia HU?
      HU007 Task 7.5: Integración con ficha general del bovino
    """,
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
@limiter.limit("20/minute")
def get_calf_details(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    bovine_id: uuid.UUID = Path(...),
    service: CalfService = Depends(get_calf_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> CalfGrowthMetricsResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se obtiene el ternero y sus métricas del servicio
    2. Se valida que es un ternero (< 365 días)
    3. Se retorna tanto los datos del bovino como las métricas
    """

    bovine, metrics = service.get_calf_details(farm_id, bovine_id)

    return CalfGrowthMetricsResponse(
        bovine=BovineResponse.model_validate(bovine).model_dump(),
        metrics=metrics.to_dict(),
    )


@router.get(
    "/{bovine_id}/weights",
    response_model=list[WeightRecordResponse],
    summary="Historial de pesajes de un ternero",
    description="""
    ¿Qué? Obtiene todos los pesajes registrados de un ternero.

    ¿Parámetros?
      days_back: Cuántos días hacia atrás recuperar (default 365)

    ¿Retorna?
      Array de pesajes ordenados cronológicamente (más antiguo primero)

    ¿Correspondencia HU?
      HU007 Task 7.4: Curva de crecimiento del ternero (datos para gráfica)
    """,
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
@limiter.limit("20/minute")
def get_calf_weight_history(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    bovine_id: uuid.UUID = Path(...),
    days_back: int = Query(365, ge=1, le=1825),
    service: CalfService = Depends(get_calf_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[WeightRecordResponse]:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se obtiene el historial de pesajes del servicio
    2. Se convierte cada pesaje a un diccionario
    3. Se retorna como JSON para que el frontend lo grafique
    """

    history = service.get_calf_weight_history(farm_id, bovine_id, days_back)

    return [WeightRecordResponse(**record) for record in history]




# ═══════════════════════════════════════════════════════════════════════════
# ➕ ENDPOINTS DE ESCRITURA
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "/{bovine_id}/weights",
    response_model=WeightRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar pesaje de un ternero",
    description="""
    ¿Qué? Registra un nuevo pesaje para un ternero.

    ¿Cuerpo?
      {
        "weight_kg": 45.5,
        "measured_date": "2026-06-15",
        "body_condition": 3,
        "observations": "Ternero en buen estado"
      }

    ¿Validaciones?
      - weight_kg debe ser > 0
      - measured_date no puede ser en el futuro
      - body_condition debe estar entre 1 y 5

    ¿Qué calcula automáticamente?
      - daily_gain (ganancia diaria vs pesaje anterior)
      - Actualiza bovine.current_weight

    ¿Correspondencia HU?
      HU007 Task 7.2: Registro de crecimiento (peso)
    """,
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
)
@limiter.limit("5/minute")
def record_calf_weight(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    bovine_id: uuid.UUID = Path(...),
    weight_data: WeightRecordCreate = Body(...),
    service: CalfService = Depends(get_calf_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> WeightRecordResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se recibe y valida el cuerpo de la petición (Pydantic)
    2. Se llama al servicio para guardar el pesaje
    3. El servicio calcula la ganancia diaria automáticamente
    4. Se registra en auditoría
    5. Se retorna el pesaje guardado como JSON

    ¿IMPACTO CRÍTICO?
      - Actualiza bovine.current_weight automáticamente
      - Calcula daily_gain basado en el anterior pesaje
      - Registra quién y cuándo se hizo el pesaje
    """

    # Llamar al servicio para guardar el pesaje
    weight_record = service.record_calf_weight(
        farm_id=farm_id,
        bovine_id=bovine_id,
        weight_kg=weight_data.weight_kg,
        measured_date=weight_data.measured_date,
        body_condition=weight_data.body_condition,
        observations=weight_data.observations,
        user_id=current_user.id,
    )

    # Convertir a response model
    return WeightRecordResponse(
        id=weight_record.id,
        date=weight_record.measured_at.isoformat(),
        weight_kg=float(weight_record.weight_kg),
        daily_gain_kg=float(weight_record.daily_gain) if weight_record.daily_gain else None,
    )
