-- SCRIPT DE VERIFICACIÓN DE PRUEBAS DE BASE DE DATOS
-- SENA ADSO - Programa 228118
-- Fecha de Generación: 27/8/2026

-- Caso de Prueba #1: CP01 — Registrar alimento en inventario
-- Acción App/API: POST /farms/{farm}/food — Melaza de Caña, 300 L
-- Resultado Esperado: 1 fila con current_stock=300.00 e is_active=t | OBTENIDO: HTTP 201 → BD: Melaza de Caña QA-083E52|300.00|t
SELECT name,current_stock,is_active FROM food WHERE name='Melaza de Caña QA-083E52';

-- Caso de Prueba #2: CP02 — Actualizar datos del alimento
-- Acción App/API: PUT /farms/{farm}/food/{id} — min_stock_alert=75
-- Resultado Esperado: min_stock_alert=75.00, supplier nuevo, updated_at>created_at | OBTENIDO: HTTP 200 → BD: 75.00|Ingenio Riopaila|t
SELECT min_stock_alert,supplier,(updated_at>created_at) FROM food WHERE id='d7f34ca0-b636-4e84-9e63-9ff6f89886ab';

-- Caso de Prueba #3: CP03 — Registrar compra de insumo (aumenta stock)
-- Acción App/API: POST /food/purchases — 250 kg @ $2.600
-- Resultado Esperado: stock_before=2548.47, stock_after=2798.47, total_cost=650000.00, coherente=t | OBTENIDO: HTTP 201 → BD: 2548.47|2798.47|250.00|650000.00|t
SELECT stock_before,stock_after,quantity,total_cost,(stock_after-stock_before=quantity) FROM stock_movement WHERE notes='Factura FV-083E52';

-- Caso de Prueba #4: CP04 — Registrar consumo de alimento
-- Acción App/API: POST /food/consumptions — 30 kg al Lote Norte
-- Resultado Esperado: stock=2768.47 y 1 fila en consumption | OBTENIDO: HTTP 201 → BD: 2768.47|1
SELECT (SELECT current_stock FROM food WHERE id='38879bcb-06f0-4584-ad56-198e314781a8'),(SELECT count(*) FROM consumption WHERE observations='CP04-083E52');

-- Caso de Prueba #5: CP05 — Consumo superior al stock disponible
-- Acción App/API: POST /food/consumptions — 99.999 L
-- Resultado Esperado: HTTP 400 «Stock insuficiente»; stock intacto (300.00) y 0 filas | OBTENIDO: HTTP 400 → BD: 300.00|0
SELECT (SELECT current_stock FROM food WHERE id='d7f34ca0-b636-4e84-9e63-9ff6f89886ab'),(SELECT count(*) FROM consumption WHERE observations='CP05-083E52');

-- Caso de Prueba #6: CP06 — Consumo con cantidad negativa
-- Acción App/API: POST /food/consumptions — quantity = -50
-- Resultado Esperado: HTTP 4xx; stock intacto (300.00) y 0 filas (no debe inflar inventario) | OBTENIDO: HTTP 422 → BD: 300.00|0
SELECT (SELECT current_stock FROM food WHERE id='d7f34ca0-b636-4e84-9e63-9ff6f89886ab'),(SELECT count(*) FROM consumption WHERE observations='CP06-083E52');

-- Caso de Prueba #7: CP07 — Ajuste manual que dejaría stock negativo
-- Acción App/API: POST /food/adjust-stock — quantity = -99999
-- Resultado Esperado: HTTP 400; stock sin cambios (300.00) | OBTENIDO: HTTP 400 → BD: 300.00
SELECT current_stock FROM food WHERE id='d7f34ca0-b636-4e84-9e63-9ff6f89886ab';

-- Caso de Prueba #8: CP08 — Consumo con alimento inexistente (integridad referencial)
-- Acción App/API: POST /food/consumptions — food_id aleatorio
-- Resultado Esperado: HTTP 404 y 0 filas insertadas | OBTENIDO: HTTP 404 → BD: 0
SELECT count(*) FROM consumption WHERE food_id='76205cba-42a3-4e12-bf1c-f5a1e17ca2fc';

-- Caso de Prueba #9: CP09 — Eliminar alimento (borrado lógico)
-- Acción App/API: DELETE /farms/{farm}/food/{id}
-- Resultado Esperado: La fila permanece (count=1) con is_active=f | OBTENIDO: HTTP 204 → BD: 1|f
SELECT count(*),bool_and(is_active) FROM food WHERE id='d7f34ca0-b636-4e84-9e63-9ff6f89886ab';

-- Caso de Prueba #10: CP10 — Alerta de stock bajo (API vs consulta SQL)
-- Acción App/API: GET /food/low-stock
-- Resultado Esperado: El número de alertas de la API coincide con el conteo SQL | OBTENIDO: HTTP 422 (ruta inaccesible) → BD: 0
SELECT count(*) FROM food WHERE farm_id='a2cb7935-3d8f-4500-b357-528ff8eeaf87' AND is_active AND min_stock_alert IS NOT NULL AND current_stock <= min_stock_alert;

-- Caso de Prueba #11: CP11 — Registrar bovino
-- Acción App/API: POST /farms/{farm}/bovines — COL-083E52
-- Resultado Esperado: HTTP 201 y 1 fila en bovine | OBTENIDO: HTTP 500 → BD: 1
SELECT count(*) FROM bovine WHERE identification_number='COL-083E52';

-- Caso de Prueba #12: CP12 — Trazabilidad: auditoría del registro de bovino
-- Acción App/API: (sin acción nueva) verificar audit_log del CP11
-- Resultado Esperado: 1 registro de auditoría para la creación del bovino | OBTENIDO: BD: 0
SELECT count(*) FROM audit_log WHERE entity='bovine' AND entity_id='4d7513fe-d2ed-4a18-ae79-feda5fc61744';

-- Caso de Prueba #13: CP13 — Bovino con identificación duplicada (UNIQUE)
-- Acción App/API: POST /farms/{farm}/bovines — mismo número de identificación
-- Resultado Esperado: HTTP 409/400 con mensaje claro y count=1 (sin duplicado) | OBTENIDO: HTTP 500 → BD: 1
SELECT count(*) FROM bovine WHERE farm_id='a2cb7935-3d8f-4500-b357-528ff8eeaf87' AND identification_number='COL-083E52';

-- Caso de Prueba #14: CP14 — Bovino asignado a un lote inexistente (FK)
-- Acción App/API: POST /farms/{farm}/bovines — land_plot_id aleatorio
-- Resultado Esperado: HTTP 4xx y 0 filas (la FK debe impedir el huérfano) | OBTENIDO: HTTP 500 → BD: 0
SELECT count(*) FROM bovine WHERE identification_number='COL-083E52-FK';

-- Caso de Prueba #15: CP15 — Actualizar datos del bovino
-- Acción App/API: PUT /farms/{farm}/bovines/{id} — name='Lucera II'
-- Resultado Esperado: name='Lucera II' y breed='Holstein Rojo' | OBTENIDO: HTTP 500 → BD: Lucera II|Holstein Rojo
SELECT name,breed FROM bovine WHERE id='4d7513fe-d2ed-4a18-ae79-feda5fc61744';

-- Caso de Prueba #16: CP16 — Registrar pesaje del bovino
-- Acción App/API: POST /bovines/{id}/weights — 432.5 kg
-- Resultado Esperado: 1 fila con weight_kg=432.50 ligada al bovino | OBTENIDO: HTTP 201 → BD: 432.50
SELECT weight_kg FROM weight WHERE observations='CP16-083E52';

-- Caso de Prueba #17: CP17 — Registrar ordeño diario
-- Acción App/API: POST /farms/{farm}/milk-production — 18.4 L
-- Resultado Esperado: quantity_liters=18.40 | OBTENIDO: HTTP 500 → BD: 18.40
SELECT quantity_liters FROM milk_production WHERE observations='CP17-083E52';

-- Caso de Prueba #18: CP18 — Registrar tratamiento sanitario
-- Acción App/API: POST /farms/{farm}/treatments — Aftosa Bivalente
-- Resultado Esperado: product_name='Aftosa Bivalente' y dose='2 ml' | OBTENIDO: HTTP 201 → BD: Aftosa Bivalente|2 ml
SELECT product_name,dose FROM treatment WHERE observations='CP18-083E52';

-- Caso de Prueba #19: CP19 — Registrar egreso económico
-- Acción App/API: POST /farms/{farm}/economics — egreso $650.000
-- Resultado Esperado: record_type='egreso' y amount=650000.00 | OBTENIDO: HTTP 201 → BD: egreso|650000.00
SELECT record_type,amount FROM economic_record WHERE description='CP19-083E52 compra de concentrado';

-- Caso de Prueba #20: CP20 — Eliminar bovino (borrado lógico)
-- Acción App/API: DELETE /farms/{farm}/bovines/{id}
-- Resultado Esperado: La fila permanece (count=1) con is_active=f — se conserva la trazabilidad | OBTENIDO: HTTP 500 → BD: 1|t
SELECT count(*),bool_and(is_active) FROM bovine WHERE id='4d7513fe-d2ed-4a18-ae79-feda5fc61744';

-- Caso de Prueba #21: CP21 — Asignar tarea usando el id devuelto por GET /employees
-- Acción App/API: POST /farms/{farm}/tasks — assigned_to = id de GET /employees
-- Resultado Esperado: HTTP 201 y 1 tarea creada (el id debe existir en users) | OBTENIDO: HTTP 500 → BD: 0|0
SELECT (SELECT count(*) FROM task WHERE title='CP21-083E52 Rotación de potreros'),(SELECT count(*) FROM users WHERE id='92c89ae1-44da-438f-9891-8979fb670ed8');

-- Caso de Prueba #22: CP22 — Asignar tarea con el users.id correcto
-- Acción App/API: POST /farms/{farm}/tasks — assigned_to = users.id
-- Resultado Esperado: HTTP 201, status='pendiente' y join válido con jperez@bovitrack.com | OBTENIDO: HTTP 201 → BD: pendiente|jperez@bovitrack.com
SELECT t.status,u.email FROM task t JOIN users u ON u.id=t.assigned_to WHERE t.title='CP22-083E52 Vacunación aftosa';

-- Caso de Prueba #23: CP23 — Escritura sin token de autenticación
-- Acción App/API: POST /farms/{farm}/food sin encabezado Authorization
-- Resultado Esperado: HTTP 401 y 0 filas insertadas | OBTENIDO: HTTP 401 → BD: 0
SELECT count(*) FROM food WHERE name='Intruso QA-083E52';

-- Caso de Prueba #24: CP24 — Crear alimento con rol Veterinario (can_create=f)
-- Acción App/API: POST /farms/{farm}/food autenticado como mrestrepo (Veterinario)
-- Resultado Esperado: HTTP 403 y 0 filas — debe respetar la tabla permission | OBTENIDO: HTTP 403 → BD: 0
SELECT count(*) FROM food WHERE name='SinPermiso QA-083E52';

-- Caso de Prueba #25: CP25 — Nombre que excede la longitud de la columna (VARCHAR 255)
-- Acción App/API: POST /farms/{farm}/food — name de 300 caracteres
-- Resultado Esperado: HTTP 422 validado por la aplicación y 0 filas (sin truncamiento silencioso) | OBTENIDO: HTTP 500 → BD: 0
SELECT count(*) FROM food WHERE length(name)>255;

-- Caso de Prueba #26: CP26 — Consistencia inventario vs. kárdex de movimientos
-- Acción App/API: (consulta analítica, sin acción en la app)
-- Resultado Esperado: 0 alimentos descuadrados entre food.current_stock y el último stock_after | OBTENIDO: BD: 4 alimento(s) descuadrado(s)
SELECT count(*) FROM food f WHERE EXISTS (SELECT 1 FROM stock_movement m WHERE m.food_id=f.id) AND f.current_stock <> (SELECT m.stock_after FROM stock_movement m WHERE m.food_id=f.id ORDER BY m.movement_date DESC, m.created_at DESC LIMIT 1);

-- Caso de Prueba #27: CP27 — Actualizar alimento con rol Empleado (can_update=f)
-- Acción App/API: PUT /farms/{farm}/food/{id} autenticado como aortiz (Empleado)
-- Resultado Esperado: HTTP 403 y valor sin cambios (150.00) | OBTENIDO: HTTP 403 → BD: 150.00
SELECT min_stock_alert FROM food WHERE id='38879bcb-06f0-4584-ad56-198e314781a8';

