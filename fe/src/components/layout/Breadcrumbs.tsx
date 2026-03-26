import { Link, useLocation } from "react-router-dom";

export default function Breadcrumbs() {
  const { pathname } = useLocation();

  if (pathname === "/dashboard") return null;

  const crumbs: { label: string; to?: string }[] = [
    { label: "Inicio", to: "/dashboard" },
  ];

  if (pathname === "/farms/new") {
    crumbs.push({ label: "Nueva Finca" });
  } else if (/^\/farms\/[^/]+$/.test(pathname)) {
    crumbs.push({ label: "Detalle de Finca" });
  }

  if (crumbs.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb" className="mb-4 flex items-center gap-2 text-sm">
      {crumbs.map((crumb, idx) => (
        <span key={idx} className="flex items-center gap-2">
          {idx > 0 && <span className="text-gray-400">/</span>}
          {crumb.to ? (
            <Link
              to={crumb.to}
              className="text-primary no-underline hover:text-primary-light hover:underline"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="font-semibold text-gray-700">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
