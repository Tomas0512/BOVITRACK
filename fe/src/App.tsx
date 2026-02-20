/*
 * App.tsx
 * ¿Qué? Componente raíz de Bovitrack. Define el enrutador principal.
 * ¿Para qué? Centralizar el routing de la app. Cada página se añade aquí.
 * ¿Impacto? Sin este componente, React no sabe qué renderizar.
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* TODO: agregar rutas a medida que crees las páginas */}
        {/* <Route path="/" element={<DashboardPage />} /> */}
        {/* <Route path="/login" element={<LoginPage />} /> */}
        <Route path="/" element={<h1>🐄 Bovitrack — En construcción</h1>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
