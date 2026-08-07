# ESPECIFICACIÓN DE CASOS DE USO (UML)

## Sistema de Control y Registro de Ganado Bovino — BoviTrack

---

## 1. CARÁTULA Y REGISTRO DE MODIFICACIONES

### Datos Generales

| Campo | Valor |
|---|---|
| **Nombre del Sistema** | BoviTrack — Sistema de Control y Registro de Ganado Bovino |
| **Versión del Documento** | 1.0 |
| **Fecha de Elaboración** | Julio 2026 |
| **Programa** | Tecnólogo en Análisis y Desarrollo de Software |
| **Institución** | SENA — Quinto Trimestre |
| **Instructores** | Luz Ojeda — Freddy Rincon |
| **Autores** | Camilo Andrés Ortiz Arévalo (1000159472) |
| | Tomás Alejandro Cantón Moreno (1027401323) |
| | Edwin Nicolás Delgado Arboleda |

### Control de Cambios

| Versión | Fecha | Autor | Descripción del Cambio |
|---|---|---|---|
| 0.1 | Julio 2026 | Camilo Andrés Ortiz Arévalo | Creación inicial del documento con casos de uso CU001–CU010 |
| 0.2 | Julio 2026 | Tomás Alejandro Cantón Moreno | Adición de casos de uso CU011–CU018 (inventario, reportes, autenticación) |
| 0.3 | Julio 2026 | Edwin Nicolás Delgado Arboleda | Adición de casos de uso CU019–CU025 (trazabilidad, auditoría, offline) |
| 1.0 | Julio 2026 | Todos | Versión final: revisión completa, incorporación de disparadores y RNF |

---

## 2. DEFINICIÓN Y CARACTERIZACIÓN DE ACTORES

### 2.1 Actores Principales

Son los usuarios humanos que inician una acción directa en el sistema para lograr un objetivo.

#### Ficha: Administrador

| Campo | Descripción |
|---|---|
| **Nombre** | Administrador |
| **Descripción del Rol** | Usuario con privilegios máximos del sistema. Tiene acceso total a todas las funcionalidades y módulos. Gestiona usuarios, roles, permisos, fincas y supervisa todas las operaciones del sistema. |
| **Responsabilidades** | Crear, editar y eliminar usuarios; asignar roles y permisos; gestionar fincas, lotes, potreros y terrenos; supervisar registros de bovinos; generar reportes; consultar auditoría; configurar notificaciones. |
| **Interfaz Utilizada** | Web (React) y Móvil (React Native) |

#### Ficha: Capataz

| Campo | Descripción |
|---|---|
| **Nombre** | Capataz |
| **Descripción del Rol** | Supervisor de finca con permisos amplios para gestionar bovinos, control productivo, reproductivo, sanitario y movimientos. Ejerce funciones de dirección operativa en campo. |
| **Responsabilidades** | Registrar y editar bovinos; controlar producción (ordeño, peso, alimentación); gestionar eventos reproductivos; registrar tratamientos sanitarios; registrar movimientos; gestionar inventario; generar reportes. |
| **Interfaz Utilizada** | Web (React) y Móvil (React Native) |

#### Ficha: Veterinario

| Campo | Descripción |
|---|---|
| **Nombre** | Veterinario |
| **Descripción del Rol** | Profesional especializado en salud animal. Se enfoca en el registro de tratamientos, vacunaciones, desparasitaciones, planes sanitarios y eventos reproductivos (servicios, diagnósticos, partos). |
| **Responsabilidades** | Registrar eventos sanitarios (vacunas, desparasitaciones, tratamientos); crear planes sanitarios; registrar servicios reproductivos; registrar diagnósticos reproductivos; registrar partos; consultar fichas y trazabilidad de animales. |
| **Interfaz Utilizada** | Web (React) y Móvil (React Native) |

#### Ficha: Empleado

| Campo | Descripción |
|---|---|
| **Nombre** | Empleado |
| **Descripción del Rol** | Trabajador de finca con permisos limitados para consultas y registros básicos de producción diaria. |
| **Responsabilidades** | Consultar fichas de animales; registrar ordeños; registrar pesajes; registrar eventos de alimentación. |
| **Interfaz Utilizada** | Web (React) y Móvil (React Native) |

### 2.2 Actores Secundarios

Son sistemas o servicios externos que interactúan con la plataforma de forma pasiva o de soporte.

#### Ficha: Sistema de Correo Electrónico

| Campo | Descripción |
|---|---|
| **Nombre** | Sistema de Correo Electrónico (Resend / Mailpit) |
| **Descripción del Rol** | Servicio externo de envío de correos electrónicos. En producción se utiliza Resend; en entorno de desarrollo se usa Mailpit como servidor SMTP local. |
| **Responsabilidades** | Enviar correos de recuperación de contraseña; enviar correos de bienvenida; enviar notificaciones y alertas programadas a los usuarios. |
| **Interfaz Utilizada** | API REST externa (HTTPS) |

#### Ficha: Sistema de Auditoría

| Campo | Descripción |
|---|---|
| **Nombre** | Sistema de Auditoría (interno automático) |
| **Descripción del Rol** | Módulo interno del sistema que registra automáticamente todas las acciones críticas realizadas por los usuarios, sin intervención manual. |
| **Responsabilidades** | Registrar usuario, fecha, hora, acción y módulo afectado en cada operación relevante (creación, edición, eliminación, consulta). |
| **Interfaz Utilizada** | Backend API (automático, sin interfaz de usuario) |

---

## 3. DIAGRAMA GENERAL DE CASOS DE USO (UML)

### 3.1 Leyenda de Simbología UML

| Símbolo UML | Significado |
|---|---|
| ──────── | Asociación |
| ◇──────── | Generalización |
| ·· ·· ··> | `<<include>>` |
| ·· ·· ··> | `<<extend>>` |
| ( monigote ) | Actor |
| ( ovalo ) | Caso de Uso |
| [ rectángulo ] | Límite del Sistema |

### 3.2 Diagrama General

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SISTEMA BOVITRACK — Control y Registro Ganadero Bovino                  │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                              MÓDULO DE GESTIÓN ANIMAL                                       │    │
│   │                                                                                              │    │
│   │   (CU001: Registrar Animal)                                                                  │    │
│   │   (CU002: Editar Animal)                                                                     │    │
│   │   (CU003: Consultar Ficha del Animal)                                                        │    │
│   │   (CU019: Consultar Trazabilidad del Animal)                                                 │    │
│   │   (CU015: Gestionar Documentos del Animal)                                                   │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE CONTROL PRODUCTIVO                                       │    │
│   │                                                                                              │    │
│   │   (CU004: Registrar Pesaje)                                                                  │    │
│   │   (CU010: Registrar Evento de Alimentación)                                                  │    │
│   │   (CU023: Gestionar Potreros y Pasturas)                                                     │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE CONTROL REPRODUCTIVO                                     │    │
│   │                                                                                              │    │
│   │   (CU006: Registrar Servicio Reproductivo)                                                   │    │
│   │   (CU007: Registrar Diagnóstico Reproductivo)                                                │    │
│   │   (CU008: Registrar Parto)                                                                   │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE CONTROL SANITARIO                                        │    │
│   │                                                                                              │    │
│   │   (CU005: Registrar Evento Sanitario)                                                        │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE MOVIMIENTOS E INVENTARIO                                 │    │
│   │                                                                                              │    │
│   │   (CU009: Registrar Movimiento de Animales)                                                  │    │
│   │   (CU011: Registrar Compra de Insumos)                                                       │    │
│   │   (CU012: Registrar Consumo de Insumos)                                                      │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE ADMINISTRACIÓN Y SEGURIDAD                               │    │
│   │                                                                                              │    │
│   │   (CU016: Iniciar Sesión)                                                                    │    │
│   │   (CU017: Recuperar Contraseña)                                                              │    │
│   │   (CU018: Gestionar Roles y Permisos)                                                        │    │
│   │   (CU024: Gestionar Fincas y Lotes)                                                          │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO DE REPORTES, ALERTAS Y AUDITORÍA                           │    │
│   │                                                                                              │    │
│   │   (CU013: Generar Reporte)                                                                   │    │
│   │   (CU014: Generar Alertas Automáticas)                                                       │    │
│   │   (CU020: Registrar Acción de Auditoría)                                                     │    │
│   │   (CU025: Configurar Notificaciones Manuales)                                                │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
│   │                          MÓDULO OFFLINE Y SINCRONIZACIÓN                                    │    │
│   │                                                                                              │    │
│   │   (CU021: Operar en Modo Offline)                                                            │    │
│   │   (CU022: Sincronizar Datos Offline)                                                         │    │
│   └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Relaciones `<<include>>` y `<<extend>>`

| Caso de Uso Padre | Relación | Caso de Uso Relacionado | Descripción |
|---|---|---|---|
| CU006: Registrar Servicio Reproductivo | `<<include>>` | CU003: Consultar Ficha del Animal | Se consulta la ficha de la hembra antes de registrar el servicio |
| CU007: Registrar Diagnóstico Reproductivo | `<<include>>` | CU006: Registrar Servicio Reproductivo | Debe existir un servicio registrado para poder diagnosticar |
| CU008: Registrar Parto | `<<include>>` | CU007: Registrar Diagnóstico Reproductivo | Se verifica diagnóstico positivo antes del parto |
| CU012: Registrar Consumo de Insumos | `<<extend>>` | CU011: Registrar Compra de Insumos | Si no hay stock suficiente, se sugiere registrar compra |
| CU014: Generar Alertas Automáticas | `<<include>>` | Sistema de Correo | Siempre envía notificación por correo al generar alerta |
| CU017: Recuperar Contraseña | `<<include>>` | Sistema de Correo | Siempre envía enlace de recuperación por correo |
| CU019: Consultar Trazabilidad | `<<include>>` | CU003: Consultar Ficha del Animal | La trazabilidad se obtiene desde la ficha del animal |
| CU020: Registrar Acción de Auditoría | `<<include>>` | Todos los CU con modificación de datos | Se ejecuta automáticamente en cada acción crítica |
| CU021: Operar en Modo Offline | `<<extend>>` | CU022: Sincronizar Datos Offline | La sincronización se ejecuta cuando se recupera conexión |

### 3.4 Generalización de Actores

```
              (Empleado)
                  ▲
                  │ hereda
            ┌─────┴─────┐
            │           │
        (Capataz)  (Veterinario)
            ▲
            │ hereda
            │
      (Administrador)
```

**Nota:** El Administrador hereda los permisos del Capataz y el Veterinario, pero con acceso total a todas las funcionalidades del sistema.

---

## 4. ESPECIFICACIÓN DETALLADA DE CASOS DE USO (FICHA TÉCNICA)

---

### CU001: Registrar Animal

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU001: Registrar Animal |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz. **Actor secundario:** Sistema de Auditoría (registra la acción automáticamente). |
| **Propósito / Descripción** | Permitir al usuario registrar un nuevo animal en el inventario del sistema, ingresando datos de identificación (raza, sexo, fecha de nacimiento, hierro, origen) y opcionalmente peso inicial, fotos y notas, para disponer de un registro completo desde el ingreso del animal a la finca. |
| **Precondiciones** | El animal no debe estar previamente registrado en la finca. El usuario debe tener permisos para crear registros de animales (can_create.bovines). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Animal" desde el módulo de bovinos de la finca. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Animal". 2. El sistema muestra el formulario de registro. 3. El usuario ingresa datos del animal (raza, sexo, fecha de nacimiento, hierro, origen). 4. El usuario adjunta información opcional (peso inicial, fotos, notas). 5. El usuario confirma el registro. 6. El sistema valida los datos ingresados. 7. El sistema verifica duplicidad por hierro/identificación. 8. El sistema guarda la información del animal en la base de datos. 9. El sistema muestra mensaje de registro exitoso. |
| **Flujos Alternativos** | **1.A — Animal ya existe:** En el paso 7, si el hierro o identificación ya existe en la finca, el sistema muestra una advertencia y solicita al usuario verificar o corregir los datos. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar la información: El sistema muestra "Error al registrar el animal. Intente nuevamente." **E2.** Datos incompletos o inválidos: El sistema muestra los campos requeridos con errores de validación. |
| **Postcondiciones** | El animal queda registrado en el sistema con su información de identificación y genealogía. Se almacena la información ingresada y se registra la acción en auditoría. El animal está disponible para los módulos de producción, reproducción, sanidad y movimientos. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Validación de datos con Pydantic. Identificador único por finca. Registro en tabla de auditoría. |

---

### CU002: Editar Animal

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU002: Editar Animal |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir al usuario modificar información existente de un animal registrado en el sistema, actualizando datos permitidos como raza, fecha de nacimiento, notas y foto, manteniendo un historial de cambios para trazabilidad. |
| **Precondiciones** | El animal debe estar registrado previamente en el sistema. El usuario debe tener permisos para editar registros de animales (can_update.bovines). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona un animal del listado y hace clic en "Editar". |
| **Flujo Principal** | 1. El usuario selecciona un animal del listado. 2. El usuario hace clic en "Editar". 3. El sistema muestra el formulario con los datos actuales del animal. 4. El usuario modifica los datos permitidos (raza, fecha de nacimiento, notas, foto). 5. El usuario guarda los cambios. 6. El sistema valida la información modificada. 7. El sistema registra el cambio en el historial. 8. El sistema muestra confirmación al usuario. |
| **Flujos Alternativos** | **1.A — Dato restringido:** Si el usuario intenta modificar un dato restringido (como identificación o hierro), el sistema muestra mensaje indicando que no es editable. |
| **Flujos de Excepción / Errores** | **E1.** Error al actualizar la información: El sistema muestra "Error al actualizar. Intente nuevamente." **E2.** Datos inválidos o incompletos: El sistema muestra errores de validación. |
| **Postcondiciones** | Se actualiza la información del animal en la base de datos. Se registra el cambio en el historial de modificaciones. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Historial de cambios inmutable. Registro en auditoría. |

---

### CU003: Consultar Ficha del Animal

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU003: Consultar Ficha del Animal |
| **Actor(es) Involucrado(s)** | **Actor principal:** Veterinario, Administrador, Capataz, Empleado. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir al usuario visualizar la información completa e historial del animal registrado en el sistema, incluyendo datos generales, historial sanitario, reproductivo y productivo, con opción de descargar o imprimir la ficha. |
| **Precondiciones** | El animal debe existir en el sistema. El usuario debe estar autenticado. El usuario debe tener permisos de consulta (can_read.bovines). |
| **Disparador (Trigger)** | El usuario busca o selecciona un animal del listado. |
| **Flujo Principal** | 1. El usuario busca o selecciona un animal. 2. El sistema muestra los datos generales del animal. 3. El sistema muestra historial sanitario, reproductivo y productivo. 4. El usuario puede descargar o imprimir la ficha. |
| **Flujos Alternativos** | **1.A — Filtrar historial:** El usuario selecciona filtros (fecha o tipo de evento). El sistema aplica los filtros y muestra la información correspondiente. |
| **Flujos de Excepción / Errores** | **E1.** Animal no encontrado: El sistema muestra "El animal solicitado no existe en el sistema." **E2.** Error al cargar historial: El sistema muestra "No se pudo cargar el historial. Intente nuevamente." |
| **Postcondiciones** | Se muestra al usuario la ficha completa del animal. El usuario puede descargar o imprimir la información. Se registra la consulta en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Ficha exportable a PDF. Paginación de historial. |

---

### CU004: Registrar Pesaje

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU004: Registrar Pesaje |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz, Empleado. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir al usuario registrar un peso del animal para su seguimiento productivo, almacenando fecha y peso para el cálculo de indicadores de crecimiento y la actualización de gráficos históricos. |
| **Precondiciones** | El animal debe estar registrado en el sistema. El usuario debe tener permisos para registrar pesajes (can_create.weights). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Pesaje" desde la ficha del animal o el módulo de producción. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Pesaje". 2. El usuario ingresa fecha y peso. 3. El usuario confirma el registro. 4. El sistema valida valores extremos (peso demasiado bajo o alto para la especie/raza). 5. El sistema guarda el registro. 6. El sistema actualiza gráficos históricos del animal. 7. Se muestra confirmación al usuario. |
| **Flujos Alternativos** | **1.A — Peso fuera de rango:** Si el peso está fuera del rango permitido, el sistema muestra una advertencia. El usuario confirma o corrige el dato. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar el pesaje: El sistema muestra "Error al registrar el pesaje. Intente nuevamente." **E2.** Falta de conexión (modo offline): El sistema almacena localmente y muestra "Pendiente por sincronizar." |
| **Postcondiciones** | El sistema almacena el registro del pesaje. Se actualizan los gráficos históricos del animal. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Gráficos interactivos con Recharts. Soporte para modo offline. |

---

### CU005: Registrar Evento Sanitario

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU005: Registrar Evento Sanitario |
| **Actor(es) Involucrado(s)** | **Actor principal:** Veterinario, Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir al usuario registrar un evento sanitario como vacuna, desparasitación o tratamiento, incluyendo medicamento, dosis, lote, fecha y responsable, para mantener un historial sanitario completo del animal. |
| **Precondiciones** | El animal debe estar registrado en el sistema. El usuario debe tener permisos para registrar eventos sanitarios (can_create.treatments). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Evento Sanitario" desde la ficha del animal o el módulo de sanidad. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Evento Sanitario". 2. El usuario ingresa tipo de evento (vacuna, desparasitación, tratamiento). 3. El usuario registra medicamento, dosis, lote, fecha y responsable. 4. El usuario adjunta documentos opcionales (fotos, resultados). 5. El usuario confirma el registro. 6. El sistema guarda el evento sanitario. 7. El sistema actualiza el historial sanitario del animal. |
| **Flujos Alternativos** | **1.A — Programación futura:** Si el evento requiere programación futura, el sistema crea un recordatorio automático. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar el evento: El sistema muestra "Error al registrar el evento sanitario. Intente nuevamente." **E2.** Datos incompletos: El sistema muestra los campos requeridos con errores de validación. |
| **Postcondiciones** | El evento sanitario queda registrado en la base de datos. El sistema actualiza el historial sanitario del animal. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Historial sanitario exportable a PDF. Recordatorios automáticos para eventos programados. |

---

### CU006: Registrar Servicio Reproductivo

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU006: Registrar Servicio Reproductivo |
| **Actor(es) Involucrado(s)** | **Actor principal:** Veterinario, Administrador. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar un evento reproductivo como una inseminación artificial o una monta natural, incluyendo información del macho o pajuela, fecha, lote, dosis y responsable, calculando automáticamente la fecha probable de diagnóstico y parto. |
| **Precondiciones** | La hembra y el toro/pajuela deben existir en el sistema. La hembra debe estar apta para reproducción (sin gestación activa). El usuario debe tener permisos para registrar eventos reproductivos (can_create.reproductive_events). |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Servicio Reproductivo" desde la ficha del animal o el módulo de reproducción. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Servicio Reproductivo". 2. El usuario selecciona tipo de servicio (monta natural o IA). 3. El usuario selecciona la hembra. 4. El usuario ingresa información del macho o pajuela. 5. El usuario registra fecha del servicio, lote, dosis y responsable. 6. El usuario adjunta información opcional (notas, fotos de registro). 7. El usuario confirma el registro. 8. El sistema valida los datos. 9. El sistema guarda el servicio reproductivo. 10. El sistema calcula fecha probable de diagnóstico y parto. |
| **Flujos Alternativos** | **1.A — Hembra no apta:** Si la hembra no está apta para reproducción, el sistema muestra una advertencia. Permite continuar solo si el usuario confirma bajo responsabilidad. |
| **Flujos de Excepción / Errores** | **E1.** Datos incompletos: El sistema muestra errores de validación. **E2.** Error al guardar la información: El sistema muestra "Error al registrar el servicio. Intente nuevamente." |
| **Postcondiciones** | El servicio reproductivo queda registrado. El sistema calcula la fecha probable de diagnóstico y parto. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Cálculo automático de fechas reproductivas. Timeline visual del ciclo reproductivo. |

---

### CU007: Registrar Diagnóstico Reproductivo

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU007: Registrar Diagnóstico Reproductivo |
| **Actor(es) Involucrado(s)** | **Actor principal:** Veterinario. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar si una hembra resultó preñada o vacía después de un servicio reproductivo, actualizando el estado reproductivo del animal según el diagnóstico (positivo, negativo o repetición). |
| **Precondiciones** | La hembra debe tener un servicio reproductivo registrado. El usuario debe tener permisos para registrar diagnósticos reproductivos (can_create.reproductive_events). El usuario debe haber iniciado sesión como Veterinario. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Diagnóstico Reproductivo" desde la timeline reproductiva del animal. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Diagnóstico Reproductivo". 2. El usuario elige la hembra correspondiente. 3. El usuario selecciona tipo de diagnóstico (positivo, negativo o repetición). 4. El usuario ingresa fecha del diagnóstico. 5. El usuario registra método (palpación, ecografía, laboratorio). 6. El usuario adjunta imágenes opcionales. 7. El usuario confirma el registro. 8. El sistema guarda el diagnóstico. 9. El sistema actualiza el estado reproductivo del animal. |
| **Flujos Alternativos** | **1.A — Diagnóstico positivo:** El sistema calcula la nueva fecha estimada de parto. **2.A — Diagnóstico negativo:** El sistema marca la hembra como disponible para un nuevo servicio. |
| **Flujos de Excepción / Errores** | **E1.** No existe un servicio válido para diagnosticar: El sistema muestra "No se encontró un servicio reproductivo reciente para esta hembra." **E2.** Error al guardar el registro: El sistema muestra "Error al registrar el diagnóstico. Intente nuevamente." |
| **Postcondiciones** | El diagnóstico queda registrado. El estado reproductivo del animal se actualiza según el resultado. Si es positivo, se calcula fecha estimada de parto. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Cálculo automático de fechas. Timeline visual actualizado. |

---

### CU008: Registrar Parto

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU008: Registrar Parto |
| **Actor(es) Involucrado(s)** | **Actor principal:** Veterinario, Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar el nacimiento de una cría y actualizar el estado reproductivo de la madre, incluyendo información del parto (sexo, peso, tipo) y creación automática del registro del nuevo animal en el sistema. |
| **Precondiciones** | La hembra debe estar en estado de gestación confirmado (diagnóstico positivo). El usuario debe tener permisos para registrar nacimientos (can_create.calves). |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Parto" desde la timeline reproductiva de la madre. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Parto". 2. El usuario selecciona la madre. 3. El usuario ingresa fecha del parto. 4. El usuario registra sexo, peso y tipo de parto (normal, distócico, asistido). 5. El usuario ingresa información de la cría (ID, hierro, raza). 6. El usuario adjunta fotos opcionales. 7. El usuario confirma el registro. 8. El sistema valida la información. 9. El sistema registra el nacimiento. 10. El sistema actualiza historial de la madre. 11. El sistema registra automáticamente la cría como nuevo animal. |
| **Flujos Alternativos** | **1.A — Parto múltiple:** El sistema solicita registrar cada cría adicional. |
| **Flujos de Excepción / Errores** | **E1.** La madre no tiene diagnóstico positivo registrado: El sistema muestra "La madre no está en estado de gestación confirmado." **E2.** Error al registrar el parto: El sistema muestra "Error al registrar el parto. Intente nuevamente." |
| **Postcondiciones** | Se registra el parto y la información de la cría. El historial de la madre se actualiza. La cría se registra automáticamente como nuevo animal. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Creación automática de registro de cría. Timeline visual del ciclo reproductivo. |

---

### CU009: Registrar Movimiento de Animales

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU009: Registrar Movimiento de Animales |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar movimientos de animales entre potreros, fincas o para compras/ventas, incluyendo tipo de movimiento, origen, destino, fecha y documentos adjuntos, actualizando la ubicación actual de cada animal. |
| **Precondiciones** | Los animales deben existir en el sistema. El usuario debe tener permisos para registrar movimientos (can_create.movements). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Movimiento" desde el módulo de movimientos. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Movimiento". 2. El usuario define tipo de movimiento (entrada, salida, traslado interno). 3. El usuario selecciona los animales involucrados. 4. El usuario registra origen y destino. 5. El usuario ingresa fecha del movimiento. 6. El usuario adjunta documentos (guías, facturas) si aplica. 7. El usuario confirma el registro. 8. El sistema valida la información. 9. El sistema actualiza la ubicación actual de cada animal. |
| **Flujos Alternativos** | **1.A — Movimiento masivo:** El usuario carga archivo Excel o selecciona grupos completos de animales. |
| **Flujos de Excepción / Errores** | **E1.** Error al registrar el movimiento: El sistema muestra "Error al registrar el movimiento. Intente nuevamente." **E2.** Datos incompletos o inconsistentes: El sistema muestra errores de validación. |
| **Postcondiciones** | Se registra el movimiento. El sistema actualiza la ubicación actual de los animales. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Soporte para movimientos masivos. Exportación de historial a PDF. |

---

### CU010: Registrar Evento de Alimentación

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU010: Registrar Evento de Alimentación |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz, Empleado. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar la alimentación suministrada a un animal o lote, incluyendo tipo de alimento, cantidad, costo y notas, para el control productivo y la actualización del historial alimenticio. |
| **Precondiciones** | El lote o animal debe existir en el sistema. Debe haber inventario suficiente de alimento (si aplica). El usuario debe tener permisos para registrar alimentación (can_create.food). |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Alimentación" desde el módulo de alimentación o la ficha del animal. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Alimentación". 2. El usuario señala si es por animal o por lote. 3. El usuario selecciona animales involucrados. 4. El usuario registra tipo de alimento y cantidad. 5. El usuario adjunta información opcional (costo, notas). 6. El usuario confirma el registro. 7. El sistema valida disponibilidad de alimento en inventario. 8. El sistema guarda el evento. 9. El sistema actualiza historial productivo. |
| **Flujos Alternativos** | **1.A — Inventario insuficiente:** Si no hay inventario suficiente, el sistema advierte y solicita confirmar o ajustar cantidades. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar el evento: El sistema muestra "Error al registrar la alimentación. Intente nuevamente." **E2.** Datos inválidos: El sistema muestra errores de validación. |
| **Postcondiciones** | Se registra el evento de alimentación. Se actualiza el historial productivo del animal o lote. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Validación de stock en inventario. Gráficos de tendencia alimenticia. |

---

### CU011: Registrar Compra de Insumos

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU011: Registrar Compra de Insumos |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar compras de medicamentos, suplementos, herramientas o insumos para la finca, incluyendo proveedor, fecha, factura, cantidad y costo, incrementando automáticamente el inventario. |
| **Precondiciones** | El usuario debe tener permisos para gestionar inventario (can_create.inventory). El proveedor debe existir en el sistema o poder crearse durante el proceso. El usuario debe haber iniciado sesión como Administrador. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Compra" desde el módulo de inventario. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Compra". 2. El usuario ingresa proveedor, fecha, número de factura y tipo de insumo. 3. El usuario ingresa cantidad, costo unitario y lote (si aplica). 4. El usuario adjunta factura o documento soporte. 5. El usuario confirma el registro. 6. El sistema valida la información. 7. El sistema incrementa el inventario del insumo. 8. El sistema muestra confirmación al usuario. |
| **Flujos Alternativos** | **1.A — Proveedor no existe:** El sistema permite registrar un nuevo proveedor sin salir del proceso de compra. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar la compra: El sistema muestra "Error al registrar la compra. Intente nuevamente." **E2.** Datos incompletos o inválidos: El sistema muestra errores de validación. |
| **Postcondiciones** | La compra queda registrada. El inventario del insumo se incrementa. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Actualización automática de stock. Soporte para documentos adjuntos. |

---

### CU012: Registrar Consumo de Insumos

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU012: Registrar Consumo de Insumos |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar el uso de medicamentos, suplementos o materiales del inventario, descontando automáticamente la cantidad utilizada y registrando el destino (animal, lote, evento sanitario). |
| **Precondiciones** | Debe existir inventario suficiente del insumo. El usuario debe tener permisos para gestionar inventario (can_update.inventory). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona "Registrar Consumo" desde el módulo de inventario. |
| **Flujo Principal** | 1. El usuario selecciona "Registrar Consumo". 2. El usuario elige tipo de insumo. 3. El usuario ingresa cantidad utilizada. 4. El usuario selecciona destino (animal, lote, evento sanitario). 5. El usuario confirma el registro. 6. El sistema valida la disponibilidad en inventario. 7. El sistema descuenta automáticamente las existencias. 8. El sistema muestra confirmación. |
| **Flujos Alternativos** | **1.A — Inventario insuficiente:** Si el inventario es insuficiente, el sistema muestra advertencia y permite ajustar cantidades o cancelar. |
| **Flujos de Excepción / Errores** | **E1.** Error al descontar inventario: El sistema muestra "Error al registrar el consumo. Intente nuevamente." **E2.** Datos inválidos: El sistema muestra errores de validación. |
| **Postcondiciones** | Se descuenta automáticamente la cantidad utilizada del inventario. El sistema registra el movimiento de consumo. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Validación de stock antes del descuento. Alertas de stock bajo. |

---

### CU013: Generar Reporte

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU013: Generar Reporte |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Veterinario, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir generar reportes de información sanitaria, productiva o reproductiva de los animales o la finca, con opción de exportar a PDF o Excel según los filtros configurados por el usuario. |
| **Precondiciones** | Debe existir información registrada en el sistema. El usuario debe tener permisos para generar reportes (can_read.reports). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario ingresa a la sección "Reportes". |
| **Flujo Principal** | 1. El usuario ingresa a la sección "Reportes". 2. El usuario selecciona tipo de reporte (sanidad, reproducción, producción, movimientos, económico). 3. El usuario aplica filtros (fecha, categoría, lote, potrero). 4. El usuario solicita generar el reporte. 5. El sistema procesa la información. 6. El sistema muestra el reporte. 7. El usuario puede exportar a PDF, Excel o imprimir. |
| **Flujos Alternativos** | **1.A — Guardar como plantilla:** El usuario guarda filtros y configuraciones seleccionadas como plantilla para uso futuro. |
| **Flujos de Excepción / Errores** | **E1.** No hay datos suficientes: El sistema muestra "No se encontraron datos para los criterios seleccionados." **E2.** Error al procesar o exportar: El sistema muestra "Error al generar el reporte. Intente nuevamente." |
| **Postcondiciones** | Se genera el reporte solicitado. El usuario puede exportarlo o imprimirlo. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Generación de PDF en < 10 segundos. Generación de Excel en < 5 segundos. Formatos profesionales con encabezados. |

---

### CU014: Generar Alertas Automáticas

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU014: Generar Alertas Automáticas |
| **Actor(es) Involucrado(s)** | **Actor principal:** Sistema (automático, sin intervención humana). **Actor secundario:** Sistema de Correo (envía notificaciones). |
| **Propósito / Descripción** | Permitir generar automáticamente alertas sobre eventos importantes como partos, vacunas, vencimiento de tratamientos e inventario bajo, notificando a los usuarios según su configuración. |
| **Precondiciones** | Deben existir eventos programados o inventario con control mínimo. El sistema de notificaciones debe estar habilitado. |
| **Disparador (Trigger)** | El sistema analiza la base de datos periódicamente (tarea programada) e identifica eventos próximos. |
| **Flujo Principal** | 1. El sistema analiza la base de datos periódicamente. 2. El sistema identifica eventos próximos (servicios, diagnósticos, partos, vacunas, inventario bajo). 3. El sistema genera alertas según reglas configuradas. 4. El sistema envía notificaciones al usuario (app, correo, según configuración). 5. El usuario visualiza alertas en el panel principal. 6. El usuario puede marcar alertas como atendidas. |
| **Flujos Alternativos** | **1.A — Cambiar tipo de notificación:** El usuario modifica sus preferencias de notificación (canal, frecuencia). |
| **Flujos de Excepción / Errores** | **E1.** Fallo en el envío de notificaciones: El sistema reintenta automáticamente. Si falla 3 veces, mantiene la alerta como pendiente. **E2.** Configuración inválida: El sistema usa configuración por defecto. |
| **Postcondiciones** | Se generan alertas automáticas. Los usuarios reciben notificaciones según su configuración. Las alertas quedan registradas en la tabla alerts. |
| **Requisitos No Funcionales Relacionados** | Análisis periódico cada 24 horas. Envío de correo en < 10 segundos. Alertas acumulables en modo offline. |

---

### CU015: Gestionar Documentos del Animal

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU015: Gestionar Documentos del Animal |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Veterinario, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir adjuntar, visualizar y eliminar documentos asociados a un animal, como resultados de laboratorio, facturas, fotos y otros archivos relevantes para la trazabilidad. |
| **Precondiciones** | El animal debe estar registrado. El usuario debe tener permisos para gestionar documentos (can_create.documents, can_read.documents, can_delete.documents). |
| **Disparador (Trigger)** | El usuario ingresa a la ficha del animal y selecciona "Documentos". |
| **Flujo Principal** | 1. El usuario ingresa a la ficha del animal. 2. El usuario selecciona la opción "Documentos". 3. El usuario adjunta archivos (PDF, imágenes, resultados de laboratorio, facturas). 4. El sistema valida el formato y tamaño. 5. El sistema guarda el documento asociado al animal. 6. El usuario puede visualizar, descargar o eliminar documentos. 7. El sistema registra en auditoría la acción realizada. |
| **Flujos Alternativos** | **1.A — Formato no permitido:** Si el documento tiene formato no permitido, el sistema rechaza el archivo y muestra advertencia. |
| **Flujos de Excepción / Errores** | **E1.** Error al cargar o guardar el archivo: El sistema muestra "Error al subir el documento. Intente nuevamente." **E2.** Documento dañado o ilegible: El sistema muestra "El archivo está dañado. Intente con otro archivo." |
| **Postcondiciones** | Se guarda o elimina un documento asociado al animal. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tamaño máximo de archivo: 10 MB. Tipos permitidos: PDF, JPG, PNG, DOC, DOCX. Tiempo de subida < 15 segundos. |

---

### CU016: Iniciar Sesión

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU016: Iniciar Sesión |
| **Actor(es) Involucrado(s)** | **Actor principal:** Cualquier usuario registrado (Administrador, Capataz, Veterinario, Empleado). **Actor secundario:** Ninguno. |
| **Propósito / Descripción** | Permitir que un usuario acceda al sistema mediante autenticación segura con correo electrónico y contraseña, obteniendo un token JWT para el acceso a funcionalidades según su rol. |
| **Precondiciones** | El usuario debe estar registrado en el sistema con cuenta activa. Debe tener un rol activo con permisos asignados. |
| **Disparador (Trigger)** | El usuario abre la pantalla de inicio de sesión e ingresa sus credenciales. |
| **Flujo Principal** | 1. El usuario abre la pantalla de inicio de sesión. 2. El usuario ingresa correo y contraseña. 3. El usuario selecciona "Iniciar sesión". 4. El sistema valida credenciales. 5. El sistema valida estado del usuario (activo/inactivo). 6. El sistema genera tokens JWT (access y refresh). 7. El sistema permite el acceso al panel principal. |
| **Flujos Alternativos** | **1.A — Contraseña incorrecta:** El sistema muestra advertencia "Credenciales incorrectas" y permite reintentar. **1.B — Cuenta inactiva:** El sistema informa que debe contactar al administrador para reactivación. |
| **Flujos de Excepción / Errores** | **E1.** Error en el servicio de autenticación: El sistema muestra "No se pudo conectar con el servidor. Intente nuevamente." **E2.** Usuario no encontrado: El sistema muestra "Credenciales incorrectas" (sin revelar si el correo existe). |
| **Postcondiciones** | El usuario inicia sesión y accede al panel principal del sistema. Se genera un token JWT válido por 15 minutos. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Contraseñas hasheadas con bcrypt. Tokens JWT con expiración configurable. Rate limiting para prevenir fuerza bruta. Anti-enumeración de usuarios. |

---

### CU017: Recuperar Contraseña

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU017: Recuperar Contraseña |
| **Actor(es) Involucrado(s)** | **Actor principal:** Cualquier usuario registrado. **Actor secundario:** Sistema de Correo (envía enlace de recuperación). |
| **Propósito / Descripción** | Permitir al usuario restablecer su contraseña cuando la ha olvidado, mediante el envío de un enlace de recuperación por correo electrónico con token de un solo uso. |
| **Precondiciones** | El usuario debe tener un correo registrado en el sistema. |
| **Disparador (Trigger)** | El usuario selecciona "¿Olvidó su contraseña?" en la pantalla de login. |
| **Flujo Principal** | 1. El usuario selecciona "¿Olvidó su contraseña?". 2. El usuario ingresa su correo electrónico. 3. El sistema busca el correo en la base de datos. 4. El sistema genera token único de recuperación con expiración de 1 hora. 5. El sistema envía un enlace de recuperación por correo. 6. El usuario accede al enlace. 7. El usuario ingresa y confirma una nueva contraseña. 8. El sistema actualiza la contraseña hasheada. 9. El sistema muestra confirmación. |
| **Flujos Alternativos** | **1.A — Correo no existe:** El sistema muestra un mensaje genérico "Si el correo está registrado, recibirá un enlace de recuperación" (sin revelar información sensible). |
| **Flujos de Excepción / Errores** | **E1.** Error al enviar el correo: El sistema muestra "No se pudo enviar el correo. Intente más tarde." **E2.** Enlace vencido o inválido: El sistema muestra "El enlace ha expirado o es inválido. Solicite uno nuevo." |
| **Postcondiciones** | La contraseña del usuario se actualiza correctamente. El token queda marcado como usado (no reutilizable). El usuario puede iniciar sesión con la nueva contraseña. |
| **Requisitos No Funcionales Relacionados** | Token de un solo uso con expiración de 1 hora. Respuesta genérica para prevenir enumeración. Correo enviado en < 10 segundos. |

---

### CU018: Gestionar Roles y Permisos

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU018: Gestionar Roles y Permisos |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir crear, editar y administrar roles del sistema, asignando permisos granulares (lectura, edición, registro, eliminación) por módulo a cada rol, definiendo el nivel de acceso de los usuarios. |
| **Precondiciones** | El usuario debe tener rol Administrador. El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El administrador ingresa a "Roles y permisos" desde el panel de administración. |
| **Flujo Principal** | 1. El administrador ingresa a "Roles y permisos". 2. El sistema muestra roles existentes (Administrador, Capataz, Veterinario, Empleado). 3. El administrador crea un rol nuevo o selecciona uno existente. 4. El administrador asigna o quita permisos (lectura, edición, registro, eliminación) por módulo. 5. El administrador guarda los cambios. 6. El sistema actualiza configuraciones de acceso. 7. El sistema registra la acción en auditoría. |
| **Flujos Alternativos** | **1.A — Modificación de permisos críticos:** Si el administrador modifica permisos críticos, el sistema solicita confirmación adicional. |
| **Flujos de Excepción / Errores** | **E1.** Error al actualizar permisos: El sistema muestra "Error al actualizar los permisos. Intente nuevamente." **E2.** Configuración incompatible o duplicada: El sistema muestra "Ya existe un permiso configurado para este módulo y rol." |
| **Postcondiciones** | Se actualizan las configuraciones de acceso. Los usuarios afectados ven reflejados los cambios inmediatamente. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. 32 permisos granulares por módulo. Cambios inmediatos sin necesidad de recarga. |

---

### CU019: Consultar Trazabilidad del Animal

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU019: Consultar Trazabilidad del Animal |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Veterinario, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir visualizar todos los eventos registrados en el ciclo de vida del animal de forma cronológica (sanidad, reproducción, pesajes, movimientos, alimentación), con opción de filtrar y exportar la información completa. |
| **Precondiciones** | El animal debe existir en el sistema. El usuario debe tener permisos de consulta (can_read.bovines). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario selecciona un animal y entra a la sección "Trazabilidad". |
| **Flujo Principal** | 1. El usuario selecciona un animal. 2. El usuario entra a la sección "Trazabilidad". 3. El sistema muestra cronológicamente los eventos (sanidad, reproducción, pesajes, movimientos, alimentación). 4. El usuario puede filtrar por fechas o tipo de evento. 5. El usuario puede exportar la trazabilidad en PDF o Excel. |
| **Flujos Alternativos** | **1.A — Ver solo eventos críticos:** El sistema aplica filtros automáticos para mostrar solo eventos críticos (tratamientos, partos, movimientos). |
| **Flujos de Excepción / Errores** | **E1.** No existen registros de trazabilidad: El sistema muestra "No se encontraron eventos registrados para este animal." **E2.** Error al cargar la información: El sistema muestra "No se pudo cargar la trazabilidad. Intente nuevamente." |
| **Postcondiciones** | El usuario puede visualizar o exportar la trazabilidad completa del animal. Se registra la consulta en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Timeline visual cronológico. Exportación a PDF y Excel. |

---

### CU020: Registrar Acción de Auditoría

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU020: Registrar Acción de Auditoría |
| **Actor(es) Involucrado(s)** | **Actor principal:** Sistema (automático, sin intervención humana). **Actor secundario:** Ninguno. |
| **Propósito / Descripción** | Permitir registrar automáticamente acciones críticas o cambios importantes realizados por los usuarios en el sistema, incluyendo usuario, fecha, hora, acción y módulo afectado, para garantizar trazabilidad y control. |
| **Precondiciones** | Debe existir un usuario autenticado realizando acciones. El módulo de auditoría debe estar habilitado. |
| **Disparador (Trigger)** | El sistema detecta una acción relevante (registro, modificación, eliminación, acceso) de forma automática. |
| **Flujo Principal** | 1. El sistema detecta una acción relevante (registro, modificación, eliminación, acceso). 2. El sistema registra usuario, fecha, hora, acción y módulo afectado. 3. El sistema guarda el registro en la tabla de auditoría. 4. El administrador puede consultar el historial desde el módulo correspondiente. |
| **Flujos Alternativos** | **1.A — Filtrar auditoría:** El administrador aplica filtros a la auditoría (usuario, acción, fecha). El sistema muestra resultados filtrados. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar el registro de auditoría: El sistema reintenta automáticamente. Si falla 3 veces, registra en log de errores. **E2.** Falta de espacio o daño en la base de datos: El sistema muestra alerta al administrador. |
| **Postcondiciones** | La acción queda registrada en la tabla de auditoría. El administrador puede consultar el historial completo. Los registros son inmutables (no editables ni eliminables). |
| **Requisitos No Funcionales Relacionados** | Registros inmutables. Paginación de resultados. Tiempo de respuesta < 3 segundos. |

---

### CU021: Operar en Modo Offline

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU021: Operar en Modo Offline |
| **Actor(es) Involucrado(s)** | **Actor principal:** Cualquier usuario de la app móvil (Administrador, Capataz, Veterinario). **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir que el usuario registre información en el sistema aun cuando no haya conexión a internet, almacenando los datos localmente en una cola de pendientes para sincronización posterior. |
| **Precondiciones** | La aplicación debe tener habilitado el modo offline. El usuario debe haber iniciado sesión previamente (conexión requerida para login inicial). |
| **Disparador (Trigger)** | El usuario ingresa al sistema sin conexión a internet, o pierde la conexión mientras la usa. |
| **Flujo Principal** | 1. El usuario ingresa al sistema sin conexión a internet. 2. El sistema entra automáticamente en modo offline. 3. El usuario registra datos (pesajes, eventos sanitarios, movimientos, partos, etc.). 4. El sistema almacena la información de forma local en el dispositivo. 5. El sistema muestra indicadores de "pendiente por sincronizar". |
| **Flujos Alternativos** | **1.A — Consulta sin conexión:** Si el usuario intenta consultar información que no está disponible localmente, el sistema muestra advertencia y permite ver solo datos almacenados offline. |
| **Flujos de Excepción / Errores** | **E1.** Fallo en el almacenamiento local: El sistema muestra "Error al guardar localmente. Verifique el espacio disponible." **E2.** El usuario nunca había iniciado sesión antes: El sistema muestra "Debe conectarse a internet al menos una vez para usar la app." |
| **Postcondiciones** | Los datos registrados quedan almacenados localmente como pendientes por sincronizar. El usuario puede continuar trabajando sin conexión. |
| **Requisitos No Funcionales Relacionados** | Cola local persistente (no se pierde al cerrar la app). Sincronización automática al recuperar conexión. Indicador visual de modo offline. |

---

### CU022: Sincronizar Datos Offline

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU022: Sincronizar Datos Offline |
| **Actor(es) Involucrado(s)** | **Actor principal:** Cualquier usuario de la app móvil. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir enviar al servidor los registros creados mientras el sistema estuvo en modo offline, validando duplicados y resolviendo conflictos de datos si existen. |
| **Precondiciones** | Debe existir conexión a internet. Deben existir datos pendientes por sincronizar en la cola local. |
| **Disparador (Trigger)** | El usuario activa la conexión a internet, o el sistema detecta automáticamente la conexión recuperada. |
| **Flujo Principal** | 1. El usuario activa conexión a internet. 2. El sistema detecta datos locales pendientes. 3. El sistema inicia la sincronización automática. 4. El sistema sube todos los registros al servidor. 5. El sistema valida que no existan duplicados. 6. El sistema actualiza la base de datos. 7. El sistema muestra el estado de sincronización completada. |
| **Flujos Alternativos** | **1.A — Conflicto de datos:** Si existe un conflicto (mismo registro modificado en servidor y localmente), el sistema solicita elegir qué versión conservar. |
| **Flujos de Excepción / Errores** | **E1.** Error de conexión durante la sincronización: El sistema reintenta automáticamente. Si falla 3 veces, mantiene las operaciones pendientes. **E2.** Corrupción de datos locales: El sistema muestra "Error en los datos locales. Intente nuevamente." |
| **Postcondiciones** | La información local queda sincronizada con el servidor. El estado de sincronización se actualiza en la interfaz. Se registra la acción en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de sincronización < 5 segundos por operación. Detección de conflictos por versión. Reintentos automáticos. |

---

### CU023: Gestionar Potreros y Pasturas

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU023: Gestionar Potreros y Pasturas |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador, Capataz. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir registrar, actualizar y consultar potreros, áreas, tipos de pasturas y su estado actual, incluyendo disponibilidad y días de descanso para rotación de pastoreo. |
| **Precondiciones** | Deben existir fincas registradas. El usuario debe tener permisos para gestionar potreros (can_create.paddocks, can_update.paddocks). El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario ingresa a "Potreros y Pasturas" desde el módulo de la finca. |
| **Flujo Principal** | 1. El usuario ingresa a "Potreros y Pasturas". 2. El usuario consulta listado de potreros existentes. 3. El usuario registra un nuevo potrero (nombre, área, tipo de pasto, estado). 4. El usuario edita información de un potrero existente. 5. El usuario registra disponibilidad y días de descanso. 6. El sistema guarda los cambios. 7. El sistema muestra el estado actual de cada potrero. |
| **Flujos Alternativos** | **1.A — Inactivar potrero:** El usuario desea inactivar un potrero temporalmente. El sistema lo marca como no disponible sin eliminar información histórica. |
| **Flujos de Excepción / Errores** | **E1.** Datos inválidos: El sistema muestra errores de validación. **E2.** Error al crear o editar potreros: El sistema muestra "Error al guardar. Intente nuevamente." |
| **Postcondiciones** | El sistema actualiza o crea la información de potreros y pasturas. Se muestra el estado actual. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Control de rotación de pastoreo. Estados visuales (disponible, en descanso, inactivo). |

---

### CU024: Gestionar Fincas y Lotes

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU024: Gestionar Fincas y Lotes |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador. **Actor secundario:** Sistema de Auditoría. |
| **Propósito / Descripción** | Permitir crear y administrar fincas, lotes y sus características operativas, incluyendo nombre, ubicación (departamento y ciudad según datos DANE), extensión y responsables asignados. |
| **Precondiciones** | El usuario debe tener rol Administrador. El usuario debe haber iniciado sesión. |
| **Disparador (Trigger)** | El usuario ingresa a "Fincas y Lotes" desde el panel de administración. |
| **Flujo Principal** | 1. El usuario ingresa a "Fincas y Lotes". 2. El usuario registra una nueva finca (nombre, ubicación, extensión). 3. El usuario registra lotes asociados a la finca. 4. El usuario edita datos de fincas o lotes. 5. El usuario asocia responsables a cada finca. 6. El usuario guarda los cambios. 7. El sistema actualiza la información. 8. El sistema muestra mensaje de confirmación. |
| **Flujos Alternativos** | **1.A — Desactivar lote:** El usuario quiere desactivar un lote. El sistema lo marca como inactivo sin eliminar información histórica. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar cambios: El sistema muestra "Error al guardar. Intente nuevamente." **E2.** Finca duplicada según ubicación: El sistema muestra "Ya existe una finca registrada en esa ubicación." |
| **Postcondiciones** | Se actualiza la información de fincas y lotes. Se registra la acción en auditoría. Las fincas están disponibles para asignación de usuarios. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Datos DANE oficiales de Colombia. Validación de datos con Pydantic. |

---

### CU025: Configurar Notificaciones Manuales

| Campo | Descripción |
|---|---|
| **Identificador y Nombre** | CU025: Configurar Notificaciones Manuales |
| **Actor(es) Involucrado(s)** | **Actor principal:** Administrador. **Actor secundario:** Sistema de Correo (envía notificaciones configuradas). |
| **Propósito / Descripción** | Permitir configurar qué eventos generan notificaciones, a qué usuarios se envían, por qué canal (correo, app) y con qué frecuencia, definiendo las reglas de notificación del sistema. |
| **Precondiciones** | Los usuarios deben estar registrados. El módulo de alertas debe estar habilitado. El usuario debe tener rol Administrador. |
| **Disparador (Trigger)** | El usuario ingresa a "Configuración de Notificaciones" desde el panel de administración. |
| **Flujo Principal** | 1. El usuario ingresa a "Configuración de Notificaciones". 2. El usuario activa o desactiva tipos de notificación (sanidad, inventario, reproducción). 3. El usuario asigna quiénes reciben cada tipo de notificación. 4. El usuario define canal (correo, app). 5. El usuario guarda la configuración. 6. El sistema actualiza reglas de notificación. |
| **Flujos Alternativos** | **1.A — Horarios de no notificación:** El usuario define horarios en los que no desea recibir alertas. El sistema programa envíos solo en horarios permitidos. |
| **Flujos de Excepción / Errores** | **E1.** Error al guardar configuración: El sistema muestra "Error al guardar la configuración. Intente nuevamente." **E2.** Canales de notificación no disponibles: El sistema muestra "El canal seleccionado no está disponible en este momento." |
| **Postcondiciones** | Se actualizan las reglas de notificación. Los usuarios reciben alertas según la configuración establecida. Se registra en auditoría. |
| **Requisitos No Funcionales Relacionados** | Tiempo de respuesta < 3 segundos. Configuración aplicable inmediatamente. Soporte para múltiples canales. |

---

## 5. RESUMEN DE RELACIONES ENTRE CASOS DE USO

| Relación | Caso de Uso Padre | Tipo | Caso de Uso Relacionado | Descripción |
|---|---|---|---|---|
| 1 | CU006: Servicio Reproductivo | `<<include>>` | CU003: Consultar Ficha | Se consulta la ficha de la hembra antes del servicio |
| 2 | CU007: Diagnóstico Reproductivo | `<<include>>` | CU006: Servicio Reproductivo | Debe existir servicio registrado para diagnosticar |
| 3 | CU008: Registrar Parto | `<<include>>` | CU007: Diagnóstico Reproductivo | Se verifica diagnóstico positivo antes del parto |
| 4 | CU012: Consumo de Insumos | `<<extend>>` | CU011: Compra de Insumos | Si no hay stock, se sugiere registrar compra |
| 5 | CU014: Alertas Automáticas | `<<include>>` | Sistema de Correo | Siempre envía notificación por correo |
| 6 | CU017: Recuperar Contraseña | `<<include>>` | Sistema de Correo | Siempre envía enlace de recuperación |
| 7 | CU019: Trazabilidad | `<<include>>` | CU003: Consultar Ficha | La trazabilidad se obtiene desde la ficha |
| 8 | CU020: Auditoría | `<<include>>` | Todos los CU con modificación | Se ejecuta automáticamente en cada acción crítica |
| 9 | CU021: Modo Offline | `<<extend>>` | CU022: Sincronizar | La sincronización se ejecuta al recuperar conexión |
