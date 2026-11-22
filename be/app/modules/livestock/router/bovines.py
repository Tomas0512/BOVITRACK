"""
Módulo: routers/bovines.py
¿Qué? Router de FastAPI para el CRUD de bovinos dentro de una finca.
¿Para qué? Exponer endpoints REST para crear, listar, consultar, actualizar
           y retirar bovinos desde el frontend o Swagger.
¿Impacto? Cada endpoint está protegido por get_current_user (JWT).
          Las rutas son anidadas bajo /farms/{farm_id}/bovines para
          asegurar que cada operación se haga dentro de la finca correcta.
"""

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status


from app.modules.livestock.dependencies import get_bovine_service, get_current_user, require_permission
from app.modules.livestock.schemas import BovineCreate, BovineResponse, BovineUpdate
from app.modules.livestock.service import BovineService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/bovines", tags=["Bovinos"])


@router.post("", response_model=BovineResponse, status_code=status.HTTP_201_CREATED, summary="Registrar bovino", dependencies=[Depends(require_permission("bovinos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: BovineCreate,
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Registra un nuevo bovino en la finca.
    ¿Para qué? El registered_by se asigna automáticamente al usuario autenticado.
    ¿Impacto? Retorna 201 Created con el bovino completo.
    """
    bovine = service.create_bovine(farm_id, data, current_user.id)
    return BovineResponse.model_validate(bovine)


@router.post(
    "/import",
    summary="Importar bovinos en lote (CSV)",
    description="Carga masiva de bovinos desde un archivo CSV. Columnas obligatorias: "
    "identification_number, sex, birth_date, entry_type, entry_date. Opcionales: name, breed, "
    "color, birth_weight, current_weight, purpose, land_plot, paddock.",
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
)
def import_csv(
    farm_id: uuid.UUID,
    file: UploadFile = File(..., description="Archivo CSV (UTF-8)"),
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """¿Qué? Lee un CSV, valida cada fila e importa los bovinos válidos.
    ¿Para qué? Cubrir el requisito de cargas masivas desde el desarrollo web.
    ¿Impacto? Retorna el resumen: importados, fallidos y errores por fila.
    """
    content = file.file.read().decode("utf-8-sig", errors="replace")
    # Interpretar el CSV y resolver lotes/potreros por nombre es negocio: lo hace el servicio.
    return service.import_csv(farm_id, content, current_user.id)


@router.get("", response_model=list[BovineResponse], summary="Listar bovinos de la finca", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    sex: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    purpose: str | None = Query(None),
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[BovineResponse]:
    """¿Qué? Lista los bovinos activos con filtros opcionales por query string.
    ¿Para qué? Permitir al frontend filtrar por sexo, estado o propósito.
    ¿Impacto? El alias 'status' evita conflicto con la palabra reservada de Python.
    """
    _ = current_user
    bovines = service.list_bovines(farm_id, sex=sex, status_filter=status_filter, purpose=purpose)
    return [BovineResponse.model_validate(b) for b in bovines]


@router.get("/breeds", response_model=list[str], summary="Listar razas existentes", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def list_breeds_route(
    farm_id: uuid.UUID,
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[str]:
    """¿Qué? Retorna las razas ya registradas en la finca (sin duplicados).
    ¿Para qué? Mostrarlas en el desplegable de razas del formulario.
    ¿Impacto? Un endpoint ligero que evita traer todos los bovinos al frontend.
    """
    _ = current_user
    return service.list_breeds(farm_id)


@router.get("/{bovine_id}", response_model=BovineResponse, summary="Obtener bovino por ID", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Retorna el detalle de un bovino específico.
    ¿Para qué? Ver ficha completa del animal, incluyendo genealogía y estado.
    ¿Impacto? Retorna 404 si el bovino no existe o no pertenece a la finca.
    """
    _ = current_user
    bovine = service.get_bovine(farm_id, bovine_id)
    return BovineResponse.model_validate(bovine)


@router.put("/{bovine_id}", response_model=BovineResponse, summary="Actualizar bovino", dependencies=[Depends(require_permission("bovinos", "can_update"))])
def update(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    data: BovineUpdate,
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Actualiza parcialmente un bovino (solo los campos enviados).
    ¿Para qué? Modificar peso, potrero, observaciones sin reenviar todo.
    ¿Impacto? Retorna 404 si el bovino no existe.
    """
    _ = current_user
    bovine = service.update_bovine(farm_id, bovine_id, data, current_user.id)
    return BovineResponse.model_validate(bovine)


@router.delete("/{bovine_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Retirar bovino (soft delete)", dependencies=[Depends(require_permission("bovinos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    service: BovineService = Depends(get_bovine_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un bovino y lo marca como 'retirado'.
    ¿Para qué? Mantener historial sin eliminar físicamente.
    ¿Impacto? Retorna 204 No Content. El bovino ya no aparece en listados.
    """
    _ = current_user
    service.delete_bovine(farm_id, bovine_id, current_user.id)
