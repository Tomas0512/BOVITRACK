# 🐛 Reporte de bugs — BoviTrack

**Fecha:** 31 de agosto de 2026
**Rama:** `main` (commit base sin modificar)
**Entorno:** Docker Compose (`db` + `be` + `fe` + `mailpit`), PostgreSQL 17, FastAPI, Python 3.12
**Cómo se encontraron:** durante una carga masiva de datos de prueba contra la API real (no INSERT directos), poblando las 33 tablas de negocio con un hato completo: 18 bovinos, 140 registros de ordeño, 15 eventos reproductivos, 7 tratamientos, inventario, economía y tareas.

---

## Resumen

| # | Severidad | Módulo | Bug | Estado |
|---|-----------|--------|-----|--------|
| 1 | 🔴 Crítica | Bovinos | `tag_number` no existe en el modelo → 500 en create/update/delete | ✅ Corregido |
| 2 | 🔴 Crítica | Producción | `liters_produced` no existe en el modelo → 500 al registrar ordeño | ✅ Corregido |
| 3 | 🟠 Alta | Alertas | Preferencias de notificación nunca se persisten (falta `commit`) | ✅ Corregido |
| 4 | 🟠 Alta | Documentos | `DocumentResponse` sin `from_attributes` → 500 al subir archivo | ✅ Corregido |
| 5 | 🔴 Crítica | Terneros (FE) | `calves.ts` duplica el prefijo `/api/v1` → los 6 endpoints dan 404 | ✅ Corregido |
| 6 | 🔴 Crítica | Terneros (BE) | `/{bovine_id}` declarada antes de `/summary` → 422 | ✅ Corregido |
| 7 | 🟠 Alta | Terneros (BE) | `CalfGrowthMetricsResponse.bovine` tipado `dict` recibe un modelo → 500 | ✅ Corregido |
| 8 | 🟠 Alta | Frontend | El mensaje de error del backend se pierde y se muestra uno genérico | ✅ Corregido (1 de 9) |
| 9 | 🟠 Alta | Empleados | La columna «Estado» confunde el vínculo con la finca y el estado de la cuenta | ✅ Corregido |
| 10 | 🔴 Crítica | Invitaciones | Invitar a un usuario **ya registrado** responde 201 pero no lo vincula (falta `commit`) | ✅ Corregido |
| 11 | 🔴 Crítica | Potreros | Los potreros no guardaban a qué lote pertenecen: la jerarquía estaba rota | ✅ Corregido |
| 12 | 🟡 Media | Inventario | Los consumos no generan movimiento de stock (kardex incompleto) | ⚠️ Sin tocar |
| 13 | 🟡 Media | Catálogos | Tabla `city` vacía → el selector de municipio no tiene opciones | ⚠️ Reportado |
| 14 | 🔵 Baja | Terneros | `class ConfigDict:` mal escrito en 3 sitios (solo afecta ejemplos de Swagger) | ⚠️ Sin tocar |
| 15 | 🔵 Baja | Modelo de datos | 4 tablas modeladas que ningún servicio escribe | ⚠️ Reportado |

Los bugs 1 a 4 **bloqueaban por completo** la carga de datos: sin corregirlos no es posible registrar un bovino, un ordeño, un documento ni guardar preferencias.

Los bugs 5 a 7 dejaban **el módulo de terneros entero inutilizable**: ninguna de sus pantallas cargaba.

---

## 🔴 Bug #1 — Registro de bovinos: atributo inexistente `tag_number`

**Archivo:** `be/app/services/bovine_service.py` — líneas 35, 87 y 101
**Afecta:** `POST`, `PUT` y `DELETE /api/v1/farms/{farm_id}/bovines/...`
**Severidad:** Crítica — el módulo central de la aplicación está inoperante desde la API.

### Síntoma

Toda creación de bovino devuelve `500 Internal Server Error`:

```
AttributeError: 'Bovine' object has no attribute 'tag_number'
  File "/app/app/services/bovine_service.py", line 35, in create_bovine
```

### Causa

La llamada de auditoría lee `bovine.tag_number`, pero el modelo `Bovine`
(`be/app/models/bovine.py:23`) define la columna como `identification_number`.
No existe ningún atributo, propiedad ni alias llamado `tag_number`.

### ⚠️ Por qué es más grave de lo que parece

El fallo ocurre **después** de `db.commit()`:

```python
db.add(bovine)
db.commit()          # ← el animal YA quedó guardado
db.refresh(bovine)
add_audit_log(..., details={"tag": bovine.tag_number})   # ← revienta aquí
db.commit()
```

Consecuencias:

1. El animal **sí se guarda** en la base de datos, pero el cliente recibe un 500 y asume que falló.
2. El registro de auditoría **nunca se escribe** → se pierde la trazabilidad, que es un requisito del sistema.
3. El frontend no recibe el `id` del bovino creado, así que cualquier flujo encadenado (asignar lote, registrar pesaje) queda roto.
4. Un usuario que reintente creará **animales duplicados** sin darse cuenta.

Durante las pruebas quedaron 14 bovinos huérfanos en la base tras 14 respuestas de error.

### Reproducción

```bash
curl -X POST http://localhost:8000/api/v1/farms/{farm_id}/bovines \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"identification_number":"TEST-001","sex":"hembra","birth_date":"2024-01-15",
       "entry_type":"compra","entry_date":"2024-02-01"}'
# → 500 Internal Server Error, pero el registro queda en la tabla `bovine`
```

### Corrección aplicada

```diff
-details={"tag": bovine.tag_number}
+details={"tag": bovine.identification_number}
```

Aplicado en las tres funciones: `create_bovine`, `update_bovine` y `delete_bovine`.

### Recomendación adicional

Mover `add_audit_log` **antes** del `commit`, dentro de la misma transacción. Así, si la auditoría falla, la operación completa hace rollback y no quedan registros huérfanos sin trazabilidad.

---

## 🔴 Bug #2 — Registro de ordeño: atributo inexistente `liters_produced`

**Archivo:** `be/app/services/milk_production_service.py` — línea 34
**Afecta:** `POST /api/v1/farms/{farm_id}/milk-production`
**Severidad:** Crítica — el módulo de producción lechera es inoperante desde la API.

### Síntoma

```
AttributeError: 'MilkProduction' object has no attribute 'liters_produced'
  File "/app/app/services/milk_production_service.py", line 34, in create_record
```

### Causa

Idéntica al Bug #1. El modelo `MilkProduction` define `quantity_liters`; el servicio lee `liters_produced`. Columnas reales del modelo:

```
id, farm_id, bovine_id, land_plot_id, milking_date, quantity_liters,
milking_type, milking_session, observations, registered_by, created_at
```

Mismo patrón peligroso: el registro se guarda antes del fallo. En las pruebas quedaron 140 registros de ordeño huérfanos con 140 respuestas 500.

### Corrección aplicada

```diff
-details={"liters": str(record.liters_produced)}
+details={"liters": str(record.quantity_liters)}
```

### 🔍 Verificación de que no hay más casos

Se cruzaron **todos** los atributos usados dentro de llamadas a `add_audit_log` en `be/app/services/*.py` contra las columnas reales de los 33 modelos SQLAlchemy. Resultado: solo estos dos casos. El resto de los servicios es correcto.

> **Causa raíz sugerida:** ninguno de los dos errores lo habría detectado un test unitario del schema — solo un test de integración que ejecute el endpoint completo. Vale la pena añadir un smoke test por endpoint de escritura.

---

## 🟠 Bug #3 — Las preferencias de notificación nunca se guardan

**Archivo:** `be/app/services/notification_service.py` — líneas 83 y 126
**Afecta:** `PUT /api/v1/farms/{farm_id}/alerts/preferences`
**Severidad:** Alta — fallo **silencioso**, el más difícil de detectar de todos.

### Síntoma

El endpoint responde `200 OK` con el objeto actualizado y correcto. El frontend muestra "guardado". Pero al recargar, la configuración vuelve a los valores por defecto, y la tabla `user_notification_pref` permanece **vacía**.

No hay ningún error en los logs. Nada indica que algo falló.

### Causa

Tanto `get_or_create_prefs` como `update_prefs` terminan en `db.flush()` sin `db.commit()`, y el router (`be/app/routers/alerts.py:143`) tampoco commitea:

```python
    if notify_birth is not None:
        pref.notify_birth = notify_birth

    db.flush()      # ← escribe en la transacción, pero nunca la confirma
    return pref
```

`flush()` envía el SQL a PostgreSQL pero **no confirma la transacción**. Al cerrar la sesión, la dependencia `get_db` hace rollback y todo se descarta. El objeto devuelto en la respuesta ya tiene los valores nuevos en memoria, por eso el 200 se ve perfecto.

Esto rompe una funcionalidad anunciada en el README: *"notificaciones configurables por usuario (canal correo/in-app, eventos y frecuencia)"*.

### Corrección aplicada

```diff
-    db.flush()
+    db.commit()
+    db.refresh(pref)
     return pref
```

En las dos funciones.

### Verificación

Se configuraron los 4 usuarios con preferencias distintas y se disparó el motor de notificaciones con condiciones reales (2 insumos bajo stock mínimo + 1 plan sanitario vencido + 1 próximo a vencer):

| Usuario | Canal | Frecuencia | `notify_low_stock` | Notificaciones recibidas |
|---|---|---|---|---|
| Luis Barbosa (Administrador) | ambos | daily | ✅ | 4 |
| Marta Quintero (Capataz) | in_app | real_time | ✅ | 4 |
| **Andrés Villamil (Veterinario)** | email | daily | ❌ | **2** |
| Jhon Ramírez (Empleado) | in_app | weekly | ✅ | 4 |

Andrés recibe solo las 2 sanitarias porque tiene el stock bajo desactivado. Las preferencias ahora **persisten y se respetan**.

---

## 🟠 Bug #4 — Subida de documentos: `class ConfigDict:` en vez de `model_config`

**Archivo:** `be/app/schemas/document.py` — líneas 196-197
**Afecta:** `POST /api/v1/farms/{farm_id}/documents`
**Severidad:** Alta

### Síntoma

```
pydantic_core.ValidationError: 1 validation error for DocumentResponse
Input should be a valid dictionary or instance of DocumentResponse
[type=model_type, input_value=Document(id=30b79fa4-be21...), input_type=Document]
  File "/app/app/routers/documents.py", line 113, in upload_document
    return DocumentResponse.model_validate(document)
```

El archivo se sube y se guarda correctamente, pero la respuesta falla con 500. Mismo patrón que #1 y #2: datos guardados, error reportado.

### Causa

```python
    class ConfigDict:          # ← una clase anidada LLAMADA "ConfigDict"
        from_attributes = True
```

En Pydantic v1 la configuración se declaraba como `class Config:`. En **v2** —la versión que usa este proyecto— debe ser `model_config = ConfigDict(...)`. Una clase anidada con el nombre `ConfigDict` es simplemente un atributo más que Pydantic **ignora por completo**, así que `from_attributes` nunca se activa y `model_validate()` rechaza el objeto ORM.

El resto del proyecto lo hace bien (ej. `be/app/schemas/bovine.py:115`), así que es una inconsistencia puntual.

### Corrección aplicada

```diff
-    class ConfigDict:
-        from_attributes = True
+    model_config = ConfigDict(from_attributes=True)
```

Más el import correspondiente en la línea 21.

---

## 🔴 Bug #5 — Módulo de terneros: prefijo `/api/v1` duplicado

**Archivo:** `fe/src/api/calves.ts` — líneas 135, 157, 183, 204, 259 y 298
**Afecta:** los **6** endpoints del módulo de terneros
**Severidad:** Crítica — ninguna pantalla de terneros carga.

### Síntoma

En la ficha de la finca aparece *"Error al procesar terneros. Intenta de nuevo."* y en el log del backend:

```
GET /api/v1/api/v1/farms/{farm_id}/calves?max_age_days=365&min_age_days=0  → 404
GET /api/v1/api/v1/farms/{farm_id}/calves/summary                          → 404
```

Nótese el `/api/v1/api/v1/` duplicado.

### Causa

La `baseURL` de axios ya incluye el prefijo (`fe/src/api/axios.ts:4`, alimentado por `VITE_API_URL=/api/v1`). `calves.ts` es el **único** cliente del proyecto que además lo escribe a mano en cada ruta:

```ts
const response = await api.get(`/api/v1/farms/${farmId}/calves`, ...);
```

Los otros 20 clientes de `fe/src/api/` usan rutas relativas correctamente.

### Corrección aplicada

```diff
-`/api/v1/farms/${farmId}/calves`
+`/farms/${farmId}/calves`
```

En las 6 ocurrencias.

---

## 🔴 Bug #6 — Orden de rutas: `/calves/summary` es inalcanzable

**Archivo:** `be/app/routers/calves.py`
**Afecta:** `GET /api/v1/farms/{farm_id}/calves/summary`
**Severidad:** Crítica

### Síntoma

```json
{"detail":[{"type":"uuid_parsing","loc":["path","bovine_id"],
  "msg":"Input should be a valid UUID, invalid character... found `s` at 1",
  "input":"summary"}]}
```

### Causa

FastAPI resuelve las rutas **en orden de declaración**. En el archivo original:

| Línea | Ruta |
|---|---|
| 127 | `/{bovine_id}` |
| 176 | `/{bovine_id}/weights` |
| **215** | **`/summary`** |

Como `/{bovine_id}` se declara primero, la petición a `/calves/summary` entra por ahí y FastAPI intenta convertir la cadena `"summary"` en un UUID. El endpoint `/summary` **nunca se alcanza**.

### Corrección aplicada

Se movió el bloque completo de `/summary` (38 líneas) para que se declare **antes** de `/{bovine_id}`. Queda en la línea 128, y `/{bovine_id}` pasa a la 168.

> **Regla general:** en FastAPI las rutas literales siempre van antes que las paramétricas del mismo nivel. Conviene revisar el resto de routers por si se repite.

---

## 🟠 Bug #7 — Detalle del ternero: tipo `dict` recibe un modelo Pydantic

**Archivos:** `be/app/routers/calves.py:211` y `be/app/schemas/calf.py:252`
**Afecta:** `GET /api/v1/farms/{farm_id}/calves/{bovine_id}`
**Severidad:** Alta

### Síntoma

```
ValidationError: 1 validation error for CalfGrowthMetricsResponse
bovine
  Input should be a valid dictionary [type=dict_type,
  input_value=BovineResponse(id=UUID('a...)), input_type=BovineResponse]
```

### Causa

El schema declara el campo como diccionario:

```python
bovine: dict = Field(..., description="Datos del ternero")
```

pero el router le pasa una instancia de `BovineResponse`:

```python
bovine=BovineResponse.model_validate(bovine),      # ← modelo, no dict
metrics=metrics.to_dict(),                          # ← este sí es dict
```

La línea de al lado (`metrics`) sí serializa a diccionario; la de `bovine` se quedó a medias.

### Corrección aplicada

```diff
-bovine=BovineResponse.model_validate(bovine),
+bovine=BovineResponse.model_validate(bovine).model_dump(),
```

Alternativa más limpia (no aplicada, requiere revisar imports circulares): tipar el campo como `bovine: BovineResponse`, que es lo que dice el propio docstring del schema.

---

## 🟠 Bug #8 — El mensaje de error del backend se pierde en el frontend

**Archivo principal:** `fe/src/components/employees/EmployeeList.tsx:48-54`
**Severidad:** Alta — el usuario ve fallos sin explicación.

### Síntoma

Al pulsar **Desactivar** sobre el único administrador de la finca, la interfaz muestra:

> ❌ No se pudo actualizar el empleado

Cuando el backend en realidad respondió con un mensaje perfectamente claro:

> ✅ *"No se puede desvincular al último administrador activo de la finca. Asigne otro administrador primero."*

El backend funciona **correctamente** (devuelve 400 con esa explicación); el problema es solo de presentación. El usuario no tiene forma de saber qué hizo mal ni cómo resolverlo.

### Causa

El interceptor de respuestas de axios (`fe/src/api/axios.ts:18-46`) ya extrae el `detail` y rechaza con un `Error` plano:

```ts
if (data.detail && typeof data.detail === "string") {
  return Promise.reject(new Error(data.detail));   // ← el mensaje va en err.message
}
```

Pero el componente lo busca donde ya no está:

```ts
const axiosErr = err as { response?: { data?: { detail?: string } } };
return axiosErr.response?.data?.detail ?? "";      // ← siempre "" tras el interceptor
```

Como devuelve cadena vacía, siempre cae en el mensaje genérico del `||`.

### Corrección aplicada

```diff
 const getApiError = (err: unknown): string => {
+  // El interceptor de api/axios.ts ya extrae `detail` y rechaza con un Error,
+  // así que el mensaje viene en err.message, no en err.response.data.detail.
+  if (err instanceof Error) return err.message;
   if (err && typeof err === "object") {
```

Verificado en el navegador: ahora se muestra el mensaje real del backend, y desactivar/activar a un empleado normal sigue funcionando.

### ⚠️ El mismo defecto está en 8 archivos más

Solo se corrigió `EmployeeList.tsx` (el caso reportado). Pendientes:

```
fe/src/components/bovines/BovineFormModal.tsx:93
fe/src/components/employees/AssignEmployeeModal.tsx:42
fe/src/components/food/FoodFormModal.tsx:95
fe/src/components/food/PurchaseFormModal.tsx:63
fe/src/components/land_plots/LandPlotFormModal.tsx:63
fe/src/components/paddocks/PaddockFormModal.tsx:66
fe/src/pages/RequestReactivationPage.tsx:24
fe/src/pages/ResetPasswordPage.tsx:121
```

Otros 12 componentes ya usan la forma correcta (`err instanceof Error ? err.message : ...`), así que la convención existe — solo hay que unificarla. Lo ideal sería extraer `getApiError` a un helper compartido en `fe/src/api/` en lugar de repetirlo en cada componente.

---

## 🟠 Bug #9 — La columna «Estado» confunde dos cosas distintas

**Archivos:** `fe/src/components/employees/EmployeeList.tsx`, `fe/src/api/employees.ts`, `be/app/schemas/employee.py`, `be/app/services/employee_service.py`
**Severidad:** Alta — el administrador ve información engañosa sobre quién puede entrar al sistema.

### Contexto: la app tiene DOS desactivaciones distintas

| Campo | Qué significa | ¿Bloquea el login? |
|---|---|---|
| `user_farm.is_active` | Vínculo con **esta** finca. Es lo que cambia el botón «Desactivar» de la lista de empleados. | ❌ **No** |
| `users.is_active` | Estado de la **cuenta**. Lo cambia `DELETE /users/me` o la aprobación de una reactivación. | ✅ Sí |

### Prueba realizada

Sujeto: Jhon Ramírez (Empleado).

| Paso | Acción | Login | Acceso a la finca |
|---|---|---|---|
| 0 | Estado inicial | ✅ 200 entra | ✅ 200 |
| 1 | «Desactivar» en la lista de empleados | ⚠️ **200 — sigue entrando** | ⛔ 403 |
| 2 | «Activar» en la lista | ✅ 200 entra | ✅ 200 |
| 3 | Desactivar la cuenta (`DELETE /users/me`) | ⛔ **403** *"Cuenta desactivada. Contacte al administrador."* | — |
| 4 | Reactivar (solicitud + aprobación del admin) | ✅ 200 entra | ✅ 200 |

Un empleado desactivado **en la finca** sí queda sin acceso útil: `GET /farms` le devuelve **0 fincas**, y el detalle, los bovinos y las tareas responden **403**. Entra al sistema, pero no ve nada. El comportamiento es defendible (una persona puede trabajar en varias fincas y perder el acceso a una sola), pero la interfaz no lo comunicaba.

### El problema real

La columna «Estado» mostraba únicamente `user_farm.is_active` e **ignoraba por completo** el estado de la cuenta. Caso concreto detectado en los datos de prueba:

> **Diana Carvajal** aparecía como **«Activo»** en la lista, pero su cuenta estaba desactivada y al intentar entrar recibía `403`.

Para un administrador esto es engañoso: ve a alguien como activo cuando en realidad no puede entrar, y no tiene forma de enterarse desde esa pantalla.

### Corrección aplicada

**Backend** — se expone el estado de la cuenta junto al del vínculo:

```diff
 # be/app/schemas/employee.py
     is_active: bool
+    # Estado de la CUENTA del usuario (users.is_active), distinto de is_active,
+    # que solo indica si sigue vinculado a esta finca (user_farm.is_active).
+    account_active: bool = True
```

```diff
 # be/app/services/employee_service.py — _build_response()
     is_active=uf.is_active,
+    account_active=uf.user.is_active,
```

**Frontend** — la columna pasa a tener tres estados, y la cuenta desactivada tiene prioridad:

| Situación | Etiqueta | Color |
|---|---|---|
| Cuenta desactivada | **Cuenta desactivada** | 🔴 rojo |
| Activo en la finca | **Activo** | 🟢 verde |
| Sin acceso a la finca | **Inactivo en la finca** | ⚪ gris |

Se añadieron además:

- **Tooltips** en cada estado explicando qué implica.
- Un **tooltip en el botón «Desactivar»**: *"Le quita el acceso a esta finca. No cierra su cuenta: podrá seguir iniciando sesión."*
- Un **contador** en la cabecera que avisa cuántas cuentas están cerradas: *"6 activos · 0 inactivos en la finca · 1 con la cuenta desactivada"*.

### Verificación

Comprobado en el navegador, los tres estados se distinguen correctamente:

```
Wilson Ardila    -> Activo
Diana Carvajal   -> Cuenta desactivada
Jhon Ramirez     -> Inactivo en la finca   (tras pulsar «Desactivar»)
Jhon Ramirez     -> Activo                 (tras pulsar «Activar»)
```

Cabecera: `5 activos · 1 inactivo en la finca · 1 con la cuenta desactivada`

### Acción nueva: «Cerrar cuenta» (implementada)

Se optó por **no** cambiar lo que hace «Desactivar» —habría dejado que un administrador de una finca cerrara el acceso a las demás fincas de esa persona sin quererlo— y añadir en su lugar una acción separada y explícita.

**Endpoint nuevo:** `PUT /api/v1/farms/{farm_id}/employees/{user_id}/account`

```json
{ "is_active": false, "reason": "Ya no trabaja en la finca" }
```

**Salvaguardas:**

| Regla | Respuesta |
|---|---|
| Solo un **Administrador de la finca** puede usarlo | `403` — validado por RBAC (`usuarios.can_delete`) y además por rol explícito |
| Nadie puede cerrar **su propia** cuenta por aquí | `400` — existe `DELETE /users/me` para eso |
| No se puede cerrar la cuenta del **último administrador activo** | `400` — reutiliza `_last_admin_check` |
| Al cerrar, se incrementa `token_version` | Las sesiones abiertas mueren al instante |
| Queda registrado en auditoría | `deactivate_account` / `activate_account` sobre la entidad `user` |

**Aviso de alcance:** `EmployeeResponse` incluye ahora `other_farms_count` (nº de otras fincas activas de esa persona). Si es mayor que cero, el diálogo de confirmación avisa: *"también trabaja en N finca(s) más y perderá el acceso a todas"*.

**En la interfaz:** botón ámbar «Cerrar cuenta» / «Reabrir cuenta», visible **solo** para administradores y nunca sobre uno mismo, con confirmación previa:

> ¿Cerrar la cuenta de Jhon Ramirez?
>
> No podrá volver a iniciar sesión en BoviTrack y se cerrarán sus sesiones abiertas. Sigue vinculado a la finca y sus registros se conservan.

### Verificación de la acción nueva

| Caso | Resultado |
|---|---|
| Admin cierra la cuenta de Jhon | ✅ 200, `account_active = false` |
| Jhon intenta entrar | ⛔ **403** *"Cuenta desactivada. Contacte al administrador."* |
| Admin reabre la cuenta | ✅ 200 |
| Jhon vuelve a entrar | ✅ 200 |
| Admin intenta cerrar su propia cuenta | ⛔ 400 con el motivo |
| Capataz intenta cerrar una cuenta | ⛔ 403 |
| Veterinario intenta cerrar una cuenta | ⛔ 403 |
| Capataz ve el botón en la interfaz | ❌ no se le muestra |
| Ciclo completo desde el navegador | ✅ cerrar → login 403 → reabrir → login 200 |

### Prueba de aislamiento entre fincas

Se crearon dos fincas más y se vinculó a **Jhon Ramírez** a las tres, con roles distintos:

| Finca | Municipio | Rol de Jhon |
|---|---|---|
| A — Finca El Recreo | Barrancabermeja | Empleado |
| B — Hacienda La Palma | Sabana de Torres | Capataz |
| C — Finca Los Naranjos | Puerto Wilches | Empleado |

**Se desactiva a Jhon SOLO en la finca A:**

| | Login | Fincas visibles | A | B | C |
|---|---|---|---|---|---|
| Estado inicial | ✅ 200 | 3 | ✅ 200 | ✅ 200 | ✅ 200 |
| **Desactivado en A** | ✅ 200 | **2** (B y C) | ⛔ **403** | ✅ **200** | ✅ **200** |
| Reactivado en A | ✅ 200 | 3 | ✅ 200 | ✅ 200 | ✅ 200 |

**El aislamiento funciona:** desactivarlo en A no le afecta en B ni en C. La finca A desaparece de su lista y devuelve 403; las otras dos siguen operativas con sus roles intactos.

**Contraste — se cierra la CUENTA desde la finca B:**

| | Login | A | B | C |
|---|---|---|---|---|
| Cuenta cerrada | ⛔ **403** *"Cuenta desactivada"* | — | — | — |
| Cuenta reabierta | ✅ 200 | ✅ 200 | ✅ 200 | ✅ 200 |

Queda demostrada la diferencia entre las dos acciones: «Desactivar» tiene alcance **de una finca**, «Cerrar cuenta» tiene alcance **global**.

**Aviso de alcance con datos reales.** Con Jhon en 3 fincas, `other_farms_count` se calcula bien desde cada una (2 desde A, 1 desde B y C), y el diálogo de confirmación en el navegador muestra:

> ¿Cerrar la cuenta de Jhon Ramirez?
>
> No podrá volver a iniciar sesión en BoviTrack y se cerrarán sus sesiones abiertas. Sigue vinculado a la finca y sus registros se conservan.
>
> **ATENCIÓN: también trabaja en 2 finca(s) más y perderá el acceso a todas.**

---

## 🔴 Bug #10 — Invitar a un usuario ya registrado no lo vincula a la finca

**Archivo:** `be/app/services/invitation_service.py` — función `register_invited_user`
**Afecta:** `POST /api/v1/auth/register-invited` cuando el invitado **ya tiene cuenta**
**Severidad:** Crítica — fallo **silencioso**. Es la vía normal para sumar a un empleado existente a una segunda finca.

### Cómo apareció

Al montar la prueba de aislamiento entre fincas: se creó la finca B, se invitó a Jhon (que ya tenía cuenta) y se aceptó la invitación. Ambas llamadas respondieron **201**… pero Jhon seguía viendo una sola finca.

```
invitacion 201 / aceptacion 201     ← ambas "exitosas"
fincas visibles (1): Finca El Recreo    ← pero no quedó vinculado
```

En la base: `farm_invitation.used = false` y ninguna fila nueva en `user_farm`.

### Causa

Mismo patrón que el Bug #3. La rama de usuario existente asigna y **retorna sin `commit`**:

```python
existing = db.execute(select(User).where(User.email == invitation.email)).scalar_one_or_none()
if existing:
    _assign_to_farm(db, existing, invitation)   # solo hace db.add() + invitation.used = True
    return existing                              # ← sin db.commit()
```

El `db.commit()` está más abajo (línea 168), solo en el camino del usuario **nuevo**. Como `_assign_to_farm` únicamente hace `db.add()`, al cerrar la sesión `get_db` hace rollback y se pierde todo: la vinculación y el consumo de la invitación.

Efecto secundario: la invitación queda `used = false`, así que el token sigue vivo y reutilizable.

### Corrección aplicada

```diff
 if existing:
-    # Si ya existe, solo asignarlo a la finca
+    # Si ya existe, solo asignarlo a la finca.
     _assign_to_farm(db, existing, invitation)
+    add_audit_log(
+        db, user_id=str(existing.id), farm_id=str(invitation.farm_id),
+        action="join_farm_by_invitation", entity="user", entity_id=str(existing.id),
+        details={"email": existing.email, "farm_id": str(invitation.farm_id)},
+    )
+    db.commit()
+    db.refresh(existing)
     return existing
```

Se añadió también el registro de auditoría, que faltaba en esta rama (el camino del usuario nuevo sí lo tenía).

### Verificación

Tras el arreglo, la misma prueba vincula correctamente a Jhon a las dos fincas nuevas (ver Bug #9 → *Prueba de aislamiento entre fincas*).

> **Nota:** `employee_service.assign_employee()` existe y hace justo esto, pero **no está expuesto como endpoint** — no hay `POST /farms/{id}/employees`. Es código muerto. La única vía para sumar a alguien a una finca es la invitación por correo, incluso si la persona ya tiene cuenta.

---

## 🔴 Bug #11 — Los potreros no guardaban a qué lote pertenecen

**Archivos:** `be/app/models/paddock.py`, `be/app/schemas/paddock.py`, `be/app/services/paddock_service.py`, `be/app/routers/paddocks.py`, `fe/src/api/paddocks.ts`, `fe/src/components/paddocks/*`
**Severidad:** Crítica — la jerarquía del módulo de terrenos estaba rota en la base de datos.

### Síntoma

En la pantalla de la finca, los potreros aparecían como una lista plana, sin ninguna relación con los lotes. No había forma de saber qué potrero pertenece a qué lote.

### Causa

La jerarquía prevista es **finca > lote > potrero**, y el código lo daba por hecho en varios sitios:

- `paddock_service.create_paddock` **exigía** que la finca tuviera al menos un lote activo, devolviendo 422 si no.
- La interfaz mostraba *"Registre al menos un lote antes de crear potreros"* y deshabilitaba el botón.
- `paddock_herd` (historial de ocupación) relaciona `paddock_id` **y** `land_plot_id`.

Pero la tabla `paddock` **solo tenía `farm_id`**. Nunca existió una columna `land_plot_id`:

```python
# create_paddock — la validación no servía para nada
has_plot = db.execute(select(LandPlot.id).where(...)).scalar_one_or_none()
if has_plot is None:
    raise HTTPException(422, "Debe registrar al menos un lote antes de crear un potrero.")

paddock = Paddock(farm_id=farm_id, **data.model_dump())   # ← el lote no se guarda
```

Es decir: se comprobaba que **existiera algún** lote y acto seguido se creaba el potrero colgando de la finca, sin vincularlo a ninguno. Una validación sin consecuencia. Con varios lotes, el potrero quedaba asociado a *ninguno* en particular.

### Corrección aplicada

**1. Migración `p1q2r3s4t5u6`** — añade `paddock.land_plot_id` como FK obligatoria:

- Crea la columna como nullable.
- **Backfill inteligente:** rellena desde `paddock_herd`, que ya sabía la relación real (toma la ocupación más reciente de cada potrero).
- Los que queden sueltos van al primer lote activo de su finca.
- Recién entonces la marca `NOT NULL`, con FK `ON DELETE CASCADE` e índice.

En los datos existentes el backfill acertó los 5 potreros con su lote real, sin pérdidas.

**2. Modelo** — `land_plot_id` + relación + propiedad `land_plot_name`.

**3. Servicio** — se reemplazó la validación vacía por una real:

```python
def _validate_land_plot(db, farm_id, land_plot_id):
    """El lote debe existir, estar activo y pertenecer a ESTA finca."""
```

Se aplica al crear y también al actualizar (mover un potrero de lote es válido, pero solo dentro de la finca). `list_paddocks` acepta `land_plot_id` como filtro y ordena por lote y nombre.

**4. API** — `PaddockCreate` exige `land_plot_id`; `PaddockResponse` devuelve `land_plot_id` y `land_plot_name`; `GET /paddocks` acepta `?land_plot_id=`.

**5. Interfaz** — selector *"Lote al que pertenece"* como primer campo del formulario (se preselecciona solo si hay un único lote), y la lista de potreros **agrupada por lote** con subtotal de área.

### Verificación

| Caso | Resultado |
|---|---|
| Listado agrupado por lote | ✅ 200, cada potrero con su `land_plot_name` |
| Filtro `?land_plot_id=` | ✅ devuelve solo los 2 potreros de La Ceiba |
| Crear con lote válido | ✅ 201, `land_plot_name` correcto |
| Crear con lote inexistente | ⛔ 422 *"El lote indicado no existe o no pertenece a esta finca"* |
| Crear con lote de **otra finca** | ⛔ 422 |
| Crear sin indicar lote | ⛔ 422 |
| Vista en el navegador | ✅ 3 grupos: El Guayabo (2 · 14,5 ha), La Ceiba (2 · 14,0 ha), La Reserva (1 · 4,6 ha) |
| Selector en el formulario | ✅ lista los 4 lotes de la finca |

---

## 🟡 Hallazgo #12 — Los consumos de alimento no generan movimiento de stock

**Archivo:** `be/app/services/food_service.py:164`
**Severidad:** Media — puede ser intencional, pero deja el kardex incompleto.

Solo las **compras** y los **ajustes** crean filas en `stock_movement`. Los consumos (`POST /food/consumptions`) descuentan el stock pero no dejan rastro en la tabla de movimientos.

Datos observados tras la carga:

| Origen | Operaciones | Filas en `stock_movement` |
|---|---|---|
| Compras | 5 | 5 |
| Ajustes | 1 | 1 |
| **Consumos** | **14** | **0** |

Resultado: `GET /food/movements` no permite reconstruir el saldo de un insumo, porque faltan todas las salidas. Si es deliberado (los consumos viven en su propia tabla `consumption`), convendría que el endpoint de movimientos haga `UNION` de ambas fuentes.

---

## 🟡 Hallazgo #13 — La tabla `city` viene vacía en las migraciones

**Severidad:** Media — afecta directamente el formulario de creación de finca.

Las migraciones cargan los 33 departamentos, pero **0 municipios**:

```sql
select (select count(*) from department) dept, (select count(*) from city) city;
--  dept | city
--    33 |    0
```

`GET /api/v1/farms/departments/{id}/cities` devuelve siempre una lista vacía, así que el selector de municipio del frontend aparece **sin opciones**. La finca se puede crear igual porque `city_municipality` es texto libre, pero el desplegable no sirve.

Durante estas pruebas se cargaron **190 municipios reales** de los 33 departamentos, con el código DANE únicamente en las 32 capitales (que siguen la regla verificable `<código_depto>001`). El resto quedó en `NULL` deliberadamente, para no inventar identificadores oficiales.

**Recomendación:** cargar el catálogo completo (~1.100 municipios con su código DANE) desde el dataset oficial del DANE en una migración de datos, no a mano.

---

## 🔵 Hallazgo #14 — `class ConfigDict:` también en `calf.py`

**Archivo:** `be/app/schemas/calf.py` — líneas 95, 181 y 284
**Severidad:** Baja — cosmético.

Mismo error de sintaxis que el Bug #4, pero en estos tres casos el bloque solo contiene `json_schema_extra` (ejemplos que se muestran en la documentación de Swagger), no `from_attributes`. El efecto es que **los ejemplos nunca aparecen en `/docs`**; no hay fallo funcional.

**No se corrigió** para no ampliar el alcance del cambio. La corrección es mecánica:

```python
model_config = ConfigDict(json_schema_extra={"example": {...}})
```

---

## 🔵 Hallazgo #15 — Tablas modeladas que ningún servicio escribe

Cuatro tablas existen en el modelo y en las migraciones, pero **ningún router ni servicio inserta en ellas**:

| Tabla | Propósito aparente | Estado |
|---|---|---|
| `bovine_identification` | Chapeta / tatuaje / DIIO por animal | Sin endpoint |
| `paddock_herd` | Aforo y ocupación de potreros | Sin endpoint |
| `bovine_audit` | Historial de cambios por animal | Sin endpoint |
| `city` | Catálogo de municipios | Sin datos (ver #6) |

`bovine_audit` llama la atención: existe un sistema de auditoría genérico (`audit_log`, que sí funciona y acumuló 317 registros), pero esta tabla específica por animal quedó sin implementar. Puede ser trabajo pendiente o un modelo que sobra — conviene decidir cuál de las dos.

En estas pruebas se poblaron por SQL directo, ya que no hay otra vía.

---

## Cambios aplicados

Doce archivos modificados, **353 líneas añadidas y 71 eliminadas**. Los cambios están en el working tree, **sin commitear**:

```
be/app/routers/calves.py                     |  80 ++++++-------  (reordenar rutas)
be/app/routers/employees.py                  |  68 +++++++++++++  (endpoint de cuenta)
be/app/schemas/document.py                   |   5 +-
be/app/schemas/employee.py                   |  19 +++++
be/app/services/bovine_service.py            |   6 +-
be/app/services/employee_service.py          |  81 ++++++++++++--
be/app/services/invitation_service.py        |  15 +++-
be/app/services/milk_production_service.py   |   2 +-
be/app/services/notification_service.py      |   6 +-
fe/src/api/calves.ts                         |  12 +--
fe/src/api/employees.ts                      |  23 ++++
fe/src/components/employees/EmployeeList.tsx | 107 +++++++++++++++---
```

> El diff grande de `calves.py` es engañoso: son 38 líneas movidas de sitio, no reescritas. El cambio real de lógica es una sola línea (`.model_dump()`).

Para revisarlos:

```bash
git diff
```

Para descartarlos:

```bash
git checkout -- be/ fe/
```

Tras tocar el frontend hay que reconstruir la imagen (nginx sirve un build estático):

```bash
docker compose up -d --build fe
```

### Verificación posterior

- ✅ `import app.main` sin errores
- ✅ Contenedor `be` en estado `healthy`
- ✅ Las 33 tablas de negocio quedaron con datos (ninguna vacía)
- ✅ 18 bovinos, 140 ordeños y 4 documentos creados **vía API**, todos con respuesta 201
- ✅ Auditoría funcionando: 317 registros en `audit_log`
- ✅ Preferencias de notificación persistidas y respetadas por el motor de alertas
- ✅ Los 4 endpoints de terneros responden 200 (lista, resumen, detalle, pesajes)
- ✅ Verificado en el navegador: la ficha de la finca carga **sin ningún mensaje de error**
- ✅ Desactivar y reactivar un empleado funciona; bloquear al último administrador muestra ahora el motivo real
- ✅ Probado el ciclo completo de desactivación/reactivación: la cuenta desactivada bloquea el login (403) y tras aprobar la reactivación vuelve a entrar (200)
- ✅ Los tres estados de la columna «Estado» se distinguen correctamente en el navegador
- ✅ Probado el aislamiento entre 3 fincas: desactivar en una no afecta a las otras; cerrar la cuenta bloquea todas

> **Nota:** no se pudo ejecutar `ruff check` — el linter no está instalado en la imagen del contenedor `be` (no figura en `requirements.txt`). Conviene añadirlo a las dependencias de desarrollo para poder validar el estilo dentro del entorno Docker.

---

## Recomendaciones

1. **Tests de integración por endpoint de escritura.** Los bugs #1, #2 y #4 son de una sola palabra y ninguno lo detecta un test de schema — hace falta ejecutar el endpoint completo contra la base. Un smoke test de un POST por módulo los habría atrapado todos.
2. **Auditar dentro de la transacción.** Mover `add_audit_log` antes del `commit` evita el patrón "guardado pero reportado como error" que comparten #1, #2 y #4.
3. **Revisar todo `flush()` sin `commit()`.** El bug #3 es silencioso y solo se detecta consultando la base directamente. Vale la pena una pasada por los servicios buscando el mismo patrón.
4. **Unificar la configuración de Pydantic v2.** Un chequeo de lint que prohíba `class Config:` y `class ConfigDict:` dentro de modelos evita que #4 y #7 se repitan.
5. **Migración de datos para los catálogos.** `city` debería poblarse desde el dataset oficial del DANE, igual que ya se hace con `department`.
