import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  Beef,
  Building2,
  Droplets,
  LayoutDashboard,
} from "lucide-react";
import { useFarm } from "../context/FarmContext";
import { listBovines } from "../api/bovines";
import { listLandPlots } from "../api/land_plots";
import { listMilkProduction } from "../api/milk_production";
import { useAuth } from "../hooks/useAuth";

const kpi = (value: string | number, label: string, icon: ReactNode, tint: string) => ({
  value,
  label,
  icon,
  tint,
});

interface ModuleCard {
  id: string;
  label: string;
  image: string;
  description: string;
  tab?: string;
  route?: string;
}

const MODULES: ModuleCard[] = [
  {
    id: "bovinos",
    label: "Ganado",
    image: "/imagenes/Ganado.jpg",
    tab: "bovinos",
    description:
      "Registro completo del hato: identificación (ID, arete y nombre), raza, sexo, color, edad, peso, estado y tipo de ingreso, con su lote o potrero actual. La tabla es personalizable: ordena, filtra, guarda vistas y exporta o importa CSV. Desde cada bovino accedes a su historial reproductivo, sanitario, de alimentación, movimientos y pesajes.",
  },
  {
    id: "terneros",
    label: "Terneros",
    image: "/imagenes/Terneros.jpg",
    tab: "terneros",
    description:
      "Seguimiento dedicado de terneros y crías: número de identificación, madre y padre, raza, fecha de nacimiento y peso. Registra pesajes para ver la curva de crecimiento, el peso promedio del lote y la ganancia diaria comparada con la referencia esperada.",
  },
  {
    id: "sanidad",
    label: "Sanidad",
    image: "/imagenes/Sanidad.jpg",
    tab: "sanidad",
    description:
      "Historial clínico de la finca: tratamientos y vacunaciones aplicados a cada animal (tipo, producto y fecha), con fecha de próxima aplicación. Incluye planes sanitarios por bovino para no dejar pasar dosis, desparasitaciones ni procedimientos pendientes.",
  },
  {
    id: "alimentacion",
    label: "Alimentación",
    image: "/imagenes/Alimentacion.jpg",
    tab: "alimentacion",
    description:
      "Control de alimentación y consumo por animal: raciones registradas con fecha y cantidad, y seguimiento del alimento suministrado. Visualiza cuánto ha consumido cada bovino, cuándo fue su última ración y mantén las dietas bajo control.",
  },
  {
    id: "movimientos",
    label: "Movimientos",
    image: "/imagenes/Movimientos.jpg",
    tab: "movimientos",
    description:
      "Trazabilidad de entradas y salidas del hato: compras, ventas, nacimientos y traslados con fecha, motivo, origen, destino, contraparte y precio. Lleva el historial completo de cada animal y su ubicación actual.",
  },
  {
    id: "lotes",
    label: "Lotes y Potreros",
    image: "/imagenes/Lotes_y_potreros.jpg",
    tab: "lotes",
    description:
      "Administra el terreno de la finca: lotes y potreros con su nombre y características, y asigna los bovinos a cada uno. Consulta en qué lote o potrero está cada animal para planificar el pastoreo y la rotación.",
  },
  {
    id: "documentos",
    label: "Documentos",
    image: "/imagenes/Documentos.jpg",
    tab: "documentos",
    description:
      "Repositorio digital de la documentación de la finca: sube, organiza por categorías y consulta de forma rápida los archivos legales y técnicos vinculados a tu operación ganadera.",
  },
  {
    id: "empleados",
    label: "Empleados",
    image: "/imagenes/Empleados.jpg",
    tab: "empleados",
    description:
      "Gestión del personal de la finca: datos de los trabajadores, roles y asignaciones de cada uno, para organizar la operación diaria y saber quién atiende cada área del hato.",
  },
  {
    id: "auditoria",
    label: "Auditoría",
    image: "/imagenes/Auditoria.jpg",
    tab: "auditoria",
    description:
      "Registro detallado de las acciones del sistema: quién, cuándo y qué cambió en cada módulo. Filtra por finca, usuario y tipo de evento para mantener la trazabilidad, el cumplimiento normativo y el control.",
  },
  {
    id: "reports",
    label: "Reportes",
    image: "/imagenes/Reportes.jpg",
    route: "/reports",
    description:
      "Informes consolidados de la operación: reúne indicadores de bovinos, sanidad, producción, alimentación y economía en reportes consultables y exportables para tomar decisiones con base en datos.",
  },
  {
    id: "economics",
    label: "Economía",
    image: "/imagenes/Economia.jpg",
    route: "/economics",
    description:
      "Control financiero de la finca: registra ingresos (ventas, leche, otros) y egresos por categoría, y visualiza balances y movimientos para conocer la rentabilidad de la operación.",
  },
  {
    id: "alerts",
    label: "Alertas",
    image: "/imagenes/Alertas.jpg",
    route: "/alerts",
    description:
      "Centro de notificaciones de la finca: configura alertas sanitarias, reproductivas, de nacimientos y de stock bajo para que no se pase nada importante en el hato.",
  },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const { farms, activeFarm, activeFarmId, loading } = useFarm();
  const [animals, setAnimals] = useState(0);
  const [lots, setLots] = useState(0);
  const [milk, setMilk] = useState(0);

  useEffect(() => {
    if (!activeFarmId) return;
    let cancelled = false;
    Promise.all([
      listBovines(activeFarmId),
      listLandPlots(activeFarmId, true),
      listMilkProduction(activeFarmId),
    ])
      .then(([bov, lands, milks]) => {
        if (cancelled) return;
        setAnimals(bov.length);
        setLots(lands.length);
        setMilk(milks.reduce((sum, m) => sum + Number(m.quantity_liters || 0), 0));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [activeFarmId]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (farms.length === 0) {
    const canCreate = !user?.role_name || user.role_name === "Administrador";
    return (
      <div className="rounded-2xl bg-surface p-12 text-center shadow-sm">
        <div className="mb-3 text-primary"><Building2 size={48} className="mx-auto" /></div>
        <h2 className="mb-2 text-lg font-bold text-text-primary">Aún no tienes fincas</h2>
        <p className="mb-6 text-sm text-text-secondary">
          {canCreate
            ? "Crea tu primera finca para empezar a gestionar tu ganado."
            : "Espera a que un administrador te asigne a una finca."}
        </p>
        {canCreate && (
          <Link
            to="/farms/new"
            className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline transition-colors hover:bg-primary-light"
          >
            Crear mi primera finca
          </Link>
        )}
      </div>
    );
  }

  if (!activeFarm) {
    return (
      <div className="rounded-2xl bg-surface p-12 text-center shadow-sm">
        <p className="text-sm text-text-secondary">Selecciona una finca del menú lateral.</p>
      </div>
    );
  }

  const cards = [
    kpi(animals, "Animales", <Beef size={24} />, "from-primary/15 to-accent/30"),
    kpi(lots, "Lotes activos", <Building2 size={24} />, "from-accent/30 to-cream"),
    kpi(milk.toLocaleString("es-CO") + " L", "Producción de leche", <Droplets size={24} />, "from-cream to-accent/20"),
  ];

  const moduleTo = (m: ModuleCard) => {
    const suffix = m.tab ? `?tab=${m.tab}` : m.route ?? "";
    return `/farms/${activeFarmId}${suffix}`;
  };

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-3">
        {cards.map((c) => (
          <div
            key={c.label}
            className="flex items-center gap-3 rounded-2xl bg-surface p-4 shadow-sm"
          >
            <div
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${c.tint} text-text-primary`}
            >
              {c.icon}
            </div>
            <div className="leading-tight">
              <p className="text-xl font-bold text-text-primary">{c.value}</p>
              <p className="text-xs text-text-muted">{c.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Módulos */}
      <div className="rounded-2xl bg-surface p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <LayoutDashboard size={18} className="text-primary" />
          <h2 className="text-base font-bold text-text-primary">Módulos</h2>
        </div>
        <div className="space-y-4">
          {MODULES.map((m, i) => {
            const image = (
              <div
                key="img"
                className="flex w-full items-center justify-center bg-surface-alt/60 p-2 sm:w-2/5 lg:w-1/2"
              >
                <img
                  src={m.image}
                  alt={m.label}
                  loading="lazy"
                  className="max-h-48 w-full object-contain transition-transform duration-300 group-hover:scale-105 sm:max-h-56"
                />
              </div>
            );
            const body = (
              <div
                key="body"
                className="flex min-w-0 flex-1 flex-col justify-center p-4"
              >
                <p className="text-base font-bold text-text-primary">{m.label}</p>
                <p className="mt-1 text-xs leading-relaxed text-text-secondary">
                  {m.description}
                </p>
              </div>
            );
            const flip = i % 2 === 1;
            return (
              <Link
                key={m.id}
                to={moduleTo(m)}
                className="group flex flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-sm no-underline transition-shadow hover:shadow-md sm:flex-row"
              >
                {flip ? [body, image] : [image, body]}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Información de la finca */}
      <div className="rounded-2xl bg-surface p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Building2 size={18} className="text-primary" />
          <h2 className="text-base font-bold text-text-primary">Información de la finca</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <InfoCard label="Dirección" value={activeFarm.address} />
          <InfoCard label="Ciudad o municipio" value={activeFarm.city_municipality} />
          <InfoCard label="Área total" value={`${activeFarm.total_area} ${activeFarm.area_unit}`} />
          <InfoCard label="Teléfono" value={activeFarm.phone ?? "No registrado"} />
          <InfoCard label="Estado" value={activeFarm.is_active ? "Activa" : "Inactiva"} />
          <InfoCard label="Fecha de creación" value={new Date(activeFarm.created_at).toLocaleDateString("es-CO")} />
          <InfoCard label="Última actualización" value={new Date(activeFarm.updated_at).toLocaleDateString("es-CO")} />
        </div>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">{label}</p>
      <p className="text-sm font-medium text-text-primary">{value}</p>
    </div>
  );
}
