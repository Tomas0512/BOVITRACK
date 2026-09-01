import { Link, useLocation } from "react-router-dom";

interface Crumb {
  label: string;
  to?: string;
}

export default function Breadcrumbs() {
  const { pathname } = useLocation();

  // En el dashboard no hace falta migas de pan (es la "casa" de la app).
  if (pathname === "/dashboard") return null;

  const crumbs: Crumb[] = [{ label: "Inicio", to: "/dashboard" }];

  // /farms/new → Inicio / Nueva Finca
  if (pathname === "/farms/new") {
    crumbs.push({ label: "Nueva Finca" });
  }
  // /audit → Inicio / Auditoría
  else if (pathname === "/audit") {
    crumbs.push({ label: "Auditoría" });
  }
  // /farms/:farmId → Inicio / Detalle de Finca
  else if (/^\/farms\/[^/]+$/.test(pathname)) {
    crumbs.push({ label: "Detalle de Finca" });
  }
  // /farms/:farmId/<sub> → Inicio / Detalle de Finca / <sub>
  else if (/^\/farms\/[^/]+\/[^/]+$/.test(pathname)) {
    const [, farmId, sub] = pathname.split("/").filter(Boolean);
    crumbs.push({ label: "Detalle de Finca", to: `/farms/${farmId}` });

    if (sub === "bovines") {
      // /farms/:farmId/bovines/:bovineId → Inicio / Detalle de Finca / Bovino
      crumbs.push({ label: "Bovino" });
    } else if (sub === "economics") {
      crumbs.push({ label: "Economía" });
    } else if (sub === "reports") {
      crumbs.push({ label: "Reportes" });
    } else if (sub === "alerts") {
      crumbs.push({ label: "Alertas" });
    }
  }

  if (crumbs.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb" className="mb-4 flex items-center gap-2 text-sm">
      {crumbs.map((crumb, idx) => (
        <span key={idx} className="flex items-center gap-2">
          {idx > 0 && <span className="text-text-muted">/</span>}
          {crumb.to ? (
            <Link
              to={crumb.to}
              className="text-primary no-underline hover:text-primary-light hover:underline"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="font-semibold text-text-secondary">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
