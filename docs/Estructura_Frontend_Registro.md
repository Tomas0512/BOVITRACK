# Estructura Frontend - Página de Registro BoviTrack

**Proyecto:** BoviTrack  
**Fecha:** 2 de marzo de 2026  
**Análisis:** Estructura de carpetas y archivos del frontend para la página de registro

---

## 📁 Estructura de carpetas y archivos involucrados

```
fe/src/
├── main.tsx                          ← 1. Punto de entrada
├── App.tsx                           ← 2. Enrutador
├── index.css                         ← Estilos globales
├── api/
│   └── auth.ts                       ← 3. Cliente HTTP (llamadas al backend)
├── components/
│   └── layout/
│       ├── AuthLayout.tsx / .css      ← 4. Layout envolvente
│       ├── Header.tsx / .css          ← 5. Cabecera (logo + botón)
│       └── Footer.tsx / .css          ← 6. Pie de página
└── pages/
    ├── RegisterPage.tsx               ← 7. LA PÁGINA DE REGISTRO
    └── RegisterPage.css               ← 8. Sus estilos
```

---

## 📋 Análisis detallado (¿Qué? ¿Para? ¿Impacto?)

### 📁 `fe/src/` — Directorio raíz del código fuente

**¿Qué?** Contiene todo el código TypeScript/React del frontend de BoviTrack.  
**¿Para?** Organizar el código fuente separado de configuraciones y archivos públicos.  
**¿Impacto?** Sin esta estructura, el código estaría mezclado con node_modules y archivos de build. Todo el desarrollo se centra aquí.

---

### 📄 `fe/src/main.tsx` — Punto de entrada de React

**¿Qué?** Archivo que monta la aplicación React en el DOM. Renderiza `<App />` dentro de `<StrictMode>` en el elemento `#root`.  
**¿Para?** Inicializar React y conectar la aplicación con el HTML base (`index.html`).  
**¿Impacto?** Sin este archivo, React no se ejecuta. Es el primer código que se ejecuta al cargar la página.

```tsx
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

---

### 📄 `fe/src/App.tsx` — Enrutador principal

**¿Qué?** Componente raíz que define todas las rutas de la aplicación usando React Router.  
**¿Para?** Centralizar la navegación. Decide qué página mostrar según la URL (`/register` → `<RegisterPage />`).  
**¿Impacto?** Sin este enrutador, la aplicación no sabría qué renderizar. Controla toda la navegación entre páginas.

```tsx
<Route path="/register" element={<RegisterPage />} />
<Route path="/" element={<Navigate to="/register" replace />} />
```

---

### 📁 `fe/src/api/` — Capa de comunicación HTTP

**¿Qué?** Directorio que contiene módulos para comunicarse con el backend.  
**¿Para?** Separar la lógica de llamadas HTTP del código de componentes UI.  
**¿Impacto?** Sin esta separación, cada página tendría código axios duplicado. Centraliza cambios de URL y manejo de errores.

---

### 📄 `fe/src/api/auth.ts` — Cliente HTTP de autenticación

**¿Qué?** Módulo que exporta funciones para llamar endpoints de auth del backend (`registerUser`, `loginUser`, etc.).  
**¿Para?** Encapsular todas las llamadas a `/auth/*` en funciones tipadas. Crear una instancia axios configurada.  
**¿Impacto?** Sin este módulo, RegisterPage tendría que manejar axios directamente. Si cambia la URL del backend, solo se modifica aquí.

```typescript
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
});

export async function registerUser(data: RegisterData): Promise<UserResponse> {
  const response = await api.post<UserResponse>("/auth/register", data);
  return response.data;
}
```

**Interfaces definidas:**
- `RegisterData` — Datos del formulario de registro
- `UserResponse` — Respuesta del backend al registrar
- `LoginData` — Datos del formulario de login  
- `TokenResponse` — Tokens JWT del login
- `MessageResponse` — Mensajes del servidor

---

### 📁 `fe/src/components/` — Componentes reutilizables

**¿Qué?** Directorio para componentes UI que se usan en múltiples páginas.  
**¿Para?** Promover reutilización de código y mantener consistencia visual.  
**¿Impacto?** Sin esta organización, cada página duplicaría componentes como Header/Footer. Facilita mantenimiento del diseño.

---

### 📁 `fe/src/components/layout/` — Componentes de estructura

**¿Qué?** Subdirectorio con componentes que definen la estructura visual (AuthLayout, Header, Footer).  
**¿Para?** Separar la lógica de layout de los componentes de negocio/formularios.  
**¿Impacto?** Sin esta separación, cada página auth (register/login/forgot) duplicaría el código de header/footer.

---

### 📄 `fe/src/components/layout/AuthLayout.tsx` — Layout para páginas auth

**¿Qué?** Componente wrapper que estructura páginas de autenticación con Header + contenido + Footer.  
**¿Para?** Proporcionar una estructura visual consistente para register/login/forgot/reset password.  
**¿Impacto?** Sin este layout, cada página auth tendría que incluir manualmente Header y Footer. Garantiza UX uniforme.

```tsx
export function AuthLayout({ children, headerActionLabel, headerActionTo }) {
  return (
    <div className="auth-layout">
      <Header actionLabel={headerActionLabel} actionTo={headerActionTo} />
      <main className="auth-layout__main">{children}</main>
      <Footer />
    </div>
  );
}
```

**Props:**
- `children` — El contenido de la página (RegisterPage, LoginPage, etc.)
- `headerActionLabel` — Texto del botón del header ("Iniciar sesión")
- `headerActionTo` — Ruta del botón del header (`/login`)

---

### 📄 `fe/src/components/layout/Header.tsx` — Cabecera de la aplicación

**¿Qué?** Componente que renderiza el logo de BoviTrack y un botón de acción configurable.  
**¿Para?** Mostrar branding consistente y navegación principal. En registro muestra "Iniciar sesión".  
**¿Impacto?** Sin header, los usuarios no tendrían navegación clara ni reconocimiento de marca. Es el primer elemento visual.

```tsx
<header className="header">
  <Link to="/" className="header__logo">
    <img src="/Logo_BoviTrack.png" alt="BoviTrack" />
  </Link>
  <Link to={actionTo} className="header__action-btn">
    {actionLabel}
  </Link>
</header>
```

**Props:**
- `actionLabel` — Texto del botón ("Iniciar sesión", "Registrarse")
- `actionTo` — Ruta de navegación del botón

---

### 📄 `fe/src/components/layout/Footer.tsx` — Pie de página

**¿Qué?** Componente que muestra información legal, contacto y copyright con año dinámico.  
**¿Para?** Proporcionar información corporativa y cumplir requisitos legales de la aplicación.  
**¿Impacto?** Sin footer, faltaría información legal obligatoria y contacto. Completa la estructura visual profesional.

```tsx
<footer className="footer">
  <p>&copy; {currentYear} BoviTrack. Todos los derechos reservados.</p>
  <p>Términos y condiciones · Política de privacidad</p>
</footer>
```

**Características:**
- Año dinámico calculado con `new Date().getFullYear()`
- Links a términos y política de privacidad
- Información de contacto (+57 300 123 4567)

---

### 📁 `fe/src/pages/` — Páginas principales de la aplicación

**¿Qué?** Directorio que contiene los componentes que representan páginas completas.  
**¿Para?** Organizar las "pantallas" de la aplicación separadas de componentes reutilizables.  
**¿Impacto?** Sin esta organización, sería difícil encontrar y mantener páginas específicas. Estructura clara por funcionalidad.

---

### 📄 `fe/src/pages/RegisterPage.tsx` — LA PÁGINA DE REGISTRO (359 líneas)

**¿Qué?** Componente completo que maneja el formulario de registro con validación, estado y envío al backend.  
**¿Para?** Permitir a usuarios crear cuentas nuevas en BoviTrack mediante un formulario de 8 campos + 2 checkboxes.  
**¿Impacto?** Sin esta página, no habría forma de registrar usuarios. Es el punto de entrada principal para nuevos usuarios.

#### 📊 Estructura interna del componente:

#### **1. Estado (useState):**
**¿Qué?** 4 estados principales para controlar el formulario  
**¿Para?** Manejar interactividad, validaciones y comunicación con backend  
**¿Impacto?** Sin estado, el formulario sería estático y no funcional

- **`formData`** — Objeto con 10 campos del formulario
- **`errors`** — Objeto con mensajes de validación por campo
- **`loading`** — Boolean para mostrar "Registrando..." 
- **`serverError`** — String con errores del backend

#### **2. Constante DOCUMENT_TYPES:**
**¿Qué?** Array con tipos de documento válidos (CC, CE, TI, PP, NIT)  
**¿Para?** Generar las opciones del select de tipo de documento  
**¿Impacto?** Debe coincidir exactamente con el ENUM del backend

```tsx
const DOCUMENT_TYPES = [
  { value: "", label: "Seleccione..." },
  { value: "CC", label: "Cédula de Ciudadanía" },
  { value: "CE", label: "Cédula de Extranjería" },
  { value: "TI", label: "Tarjeta de Identidad" },
  { value: "PP", label: "Pasaporte" },
  { value: "NIT", label: "NIT" },
];
```

#### **3. Function handleChange:**
**¿Qué?** Maneja cambios en inputs de texto y selects  
**¿Para?** Actualizar `formData` y limpiar errores del campo específico  
**¿Impacto?** Sin esta función, el usuario no vería lo que escribe

#### **4. Function handleCheck:**
**¿Qué?** Maneja cambios en checkboxes de términos y datos personales  
**¿Para?** Actualizar los booleanos para aceptación de términos  
**¿Impacto?** Sin esta función, no se podrían marcar los checkboxes obligatorios

#### **5. Function validate:**
**¿Qué?** Validación completa del formulario con 16 reglas  
**¿Para?** Verificar datos antes del envío al backend  
**¿Impacto?** Evita errores 400 del servidor y mejora UX

**Validaciones implementadas:**
- Campos vacíos
- Solo letras en nombres/apellidos (`TEXT_ONLY = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/`)
- Formato email válido
- Contraseña mínimo 8 caracteres
- Contraseñas coincidentes
- Checkboxes obligatorios marcados

#### **6. Function handleSubmit:**
**¿Qué?** Proceso completo de envío del formulario  
**¿Para?** Registrar el usuario y dirigirlo al siguiente paso  
**¿Impacto?** Es la conexión real con el backend

**Flujo:**
1. Prevenir submit por defecto
2. Validar formulario
3. Activar estado loading
4. Llamar `registerUser()` de `api/auth.ts`
5. Si éxito → `navigate("/login")` con estado
6. Si error → mostrar mensaje del servidor
7. Desactivar loading

#### **7. JSX (Render) - Estructura visual:**
**¿Qué?** 192 líneas de JSX que crean la interfaz del formulario  
**¿Para?** Permitir al usuario interactuar con el registro  
**¿Impacto?** Sin el JSX, no habría interfaz visual

**Estructura del formulario:**
1. **Fila 1:** Nombres + Apellidos
2. **Fila 2:** Tipo documento (select) + Número documento  
3. **Fila 3:** Email + Teléfono
4. **Fila 4:** Contraseña + Confirmar contraseña
5. **Checkboxes:** Términos y condiciones + Autorización datos
6. **Botón:** Submit (deshabilitado si formulario incompleto)
7. **Link:** "¿Ya estás registrado? Inicia sesión"

#### **8. Computed Property isFormComplete:**
**¿Qué?** Boolean que verifica que todos los campos estén completos  
**¿Para?** Habilitar/deshabilitar el botón de envío  
**¿Impacto?** Evita envíos con datos faltantes, mejora UX

---

### 📄 `fe/src/pages/RegisterPage.css` — Estilos de la página de registro

**¿Qué?** Hoja de estilos CSS específica usando metodología BEM.  
**¿Para?** Dar estilo visual al formulario: layout, colores, espaciado, estados.  
**¿Impacto?** Sin estilos, el formulario funcionaría pero se vería como HTML básico.

#### **Clases CSS principales:**
- `.register__card` — Tarjeta contenedora centrada
- `.register__title` — Título "Crear cuenta"
- `.register__subtitle` — Descripción bajo el título
- `.register__row` — Filas de 2 campos en desktop, 1 en mobile
- `.register__field` — Contenedor de cada campo (label + input + error)
- `.register__required` — Asterisco rojo para campos obligatorios
- `.register__error` — Mensaje de error en rojo
- `.register__server-error` — Error del backend
- `.register__btn` — Botón de submit
- `.register__btn--disabled` — Estado deshabilitado del botón
- `.register__checkbox` — Styling de checkboxes
- `.register__login-link` — Link al final para ir a login

---

### 📄 `fe/src/index.css` — Estilos globales

**¿Qué?** Hoja de estilos global que afecta toda la aplicación.  
**¿Para?** Establecer reset CSS, fuentes, variables y base visual.  
**¿Impacto?** Sin estilos globales, cada componente tendría estilos inconsistentes.

---

## 🔄 Flujo de renderizado (RegisterPage)

```
1. main.tsx
   ↓ monta React
2. App.tsx 
   ↓ ruta /register renderiza
3. RegisterPage.tsx 
   ↓ se envuelve en
4. AuthLayout.tsx 
   ↓ que renderiza
5. Header.tsx + RegisterPage + Footer.tsx
   ↓ usuario llena formulario y hace submit
6. handleSubmit() → validate() → registerUser() 
   ↓ POST al backend
7. FastAPI /auth/register
   ↓ si éxito
8. navigate("/login") con mensaje de éxito
```

---

## 📡 Flujo de datos (Registro)

### **Frontend → Backend:**
```javascript
// Datos que se envían al servidor
{
  email: "usuario@ejemplo.com",
  first_name: "Juan",
  last_name: "Pérez", 
  document_type: "CC",
  document_number: "1234567890",
  phone: "3001234567",
  password: "MiPassword123"
}
```

### **Backend → Frontend:**
```javascript
// Respuesta exitosa (201 Created)
{
  id: "uuid-generado",
  email: "usuario@ejemplo.com", 
  first_name: "Juan",
  last_name: "Pérez",
  document_type: "CC", 
  document_number: "1234567890",
  phone: "3001234567",
  is_active: true,
  created_at: "2026-03-02T10:30:00Z",
  updated_at: "2026-03-02T10:30:00Z"
}
```

```javascript
// Respuesta de error (422 Unprocessable Entity)
{
  detail: "El email ya está registrado"
}
```

---

## 🎯 Puntos clave del registro

### **Validaciones del Frontend:**
- ✅ Campos obligatorios no vacíos
- ✅ Solo letras en nombres/apellidos 
- ✅ Email con formato válido
- ✅ Contraseña mínimo 8 caracteres
- ✅ Contraseñas coincidentes
- ✅ Checkboxes de términos marcados

### **Estados del formulario:**
- **Inicial:** Vacío, botón deshabilitado
- **Llenando:** Errores en tiempo real, botón se habilita gradualmente
- **Enviando:** Loading, botón deshabilitado, texto "Registrando..."
- **Éxito:** Redirección automática a `/login`
- **Error:** Mensaje del servidor, formulario editable

### **Navegación:**
- Ruta actual: `/register`
- Header muestra: "Iniciar sesión" → `/login`
- Al completar: Redirección a `/login` con estado `{ registered: true }`
- Link manual: "¿Ya estás registrado? Inicia sesión" → `/login`

---

## 🔧 Dependencias clave

### **Librerías React:**
- `react` — Framework base
- `react-dom` — Manipulación del DOM  
- `react-router-dom` — Navegación SPA

### **Comunicación HTTP:**
- `axios` — Cliente HTTP para llamadas al backend

### **Herramientas de desarrollo:**
- `typescript` — Tipado estático
- `vite` — Bundler y dev server
- CSS modules / BEM — Metodología de estilos

---

## ✅ Resumen ejecutivo

**La página de registro de BoviTrack es un formulario completo y robusto que:**

1. **Captura 8 campos** de datos del usuario más 2 checkboxes legales
2. **Valida en tiempo real** con 16 reglas de validación
3. **Se conecta al backend** vía API REST tipada
4. **Maneja errores** tanto de validación como de servidor
5. **Proporciona UX fluida** con estados loading y disabled
6. **Sigue buenas prácticas** de arquitectura frontend moderno

**Impacto total:** Es el punto de entrada principal para nuevos usuarios y determina su primera impresión de la aplicación. Su correcto funcionamiento es crítico para el crecimiento del negocio.

---

***Documento generado automáticamente el 2 de marzo de 2026***