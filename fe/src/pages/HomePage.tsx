import { Link } from "react-router-dom";
import { Header } from "../components/layout/Header";
import { Footer } from "../components/layout/Footer";

const features = [
  {
    icon: "🏡",
    title: "Gestión de Fincas",
    description:
      "Registra y administra tus fincas con datos de ubicación, extensión, propósito productivo y lotes de terreno.",
  },
  {
    icon: "🐂",
    title: "Control del Hato",
    description:
      "Lleva el registro completo de cada bovino: identificación, genealogía, peso, estado reproductivo y más.",
  },
  {
    icon: "🥛",
    title: "Producción Lechera",
    description:
      "Registra ordeños diarios por animal, consulta promedios y detecta cambios en la producción de tu hato.",
  },
  {
    icon: "💊",
    title: "Sanidad y Tratamientos",
    description:
      "Controla vacunas, desparasitaciones y tratamientos veterinarios con fechas de próxima aplicación.",
  },
];

const steps = [
  {
    number: "1",
    title: "Crea tu cuenta",
    description: "Regístrate en menos de un minuto con tus datos básicos.",
  },
  {
    number: "2",
    title: "Registra tu finca",
    description: "Agrega tus fincas con ubicación, extensión y propósito productivo.",
  },
  {
    number: "3",
    title: "Gestiona tu ganado",
    description: "Controla tu hato, producción, sanidad y tareas desde un solo lugar.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        {/* ── Hero ── */}
        <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-cream/60 to-accent/30 px-4 py-20 sm:py-28">
          <div className="mx-auto flex max-w-6xl flex-col items-center text-center">
            <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
              Plataforma de gestión ganadera
            </span>
            <h1 className="mb-5 text-4xl font-extrabold leading-tight text-gray-900 sm:text-5xl lg:text-6xl">
              Tu ganado bajo control con{" "}
              <span className="text-primary">BoviTrack</span>
            </h1>
            <p className="mb-10 max-w-2xl text-lg leading-relaxed text-gray-600">
              La herramienta integral para ganaderos colombianos. Registra fincas,
              controla tu hato, producción lechera, tratamientos, alimentación y
              tareas — todo desde un solo lugar.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row">
              <Link
                to="/register"
                className="rounded-xl bg-primary px-8 py-3.5 text-base font-bold text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary-light hover:shadow-xl active:scale-[0.98]"
              >
                Comenzar gratis
              </Link>
              <Link
                to="/login"
                className="rounded-xl border-2 border-primary px-8 py-3.5 text-base font-bold text-primary transition-all hover:bg-primary hover:text-white active:scale-[0.98]"
              >
                Ya tengo cuenta
              </Link>
            </div>
          </div>
        </section>

        {/* ── Características ── */}
        <section className="bg-white px-4 py-16 sm:py-20">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-3 text-center text-3xl font-extrabold text-gray-900">
              Todo lo que necesitas
            </h2>
            <p className="mx-auto mb-12 max-w-xl text-center text-gray-500">
              Módulos diseñados para cubrir cada aspecto de la operación ganadera diaria.
            </p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((f) => (
                <div
                  key={f.title}
                  className="rounded-2xl border border-gray-100 bg-surface p-6 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="mb-4 text-4xl">{f.icon}</div>
                  <h3 className="mb-2 text-lg font-bold text-gray-900">{f.title}</h3>
                  <p className="text-sm leading-relaxed text-gray-500">{f.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Cómo funciona ── */}
        <section className="bg-cream/40 px-4 py-16 sm:py-20">
          <div className="mx-auto max-w-4xl">
            <h2 className="mb-3 text-center text-3xl font-extrabold text-gray-900">
              Empieza en 3 pasos
            </h2>
            <p className="mx-auto mb-12 max-w-lg text-center text-gray-500">
              Sin configuraciones complicadas. Registra, configura y gestiona.
            </p>
            <div className="grid gap-8 sm:grid-cols-3">
              {steps.map((s) => (
                <div key={s.number} className="flex flex-col items-center text-center">
                  <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-xl font-extrabold text-white shadow-md">
                    {s.number}
                  </div>
                  <h3 className="mb-2 text-lg font-bold text-gray-900">{s.title}</h3>
                  <p className="text-sm leading-relaxed text-gray-500">{s.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Números / propuesta de valor ── */}
        <section className="bg-white px-4 py-16 sm:py-20">
          <div className="mx-auto grid max-w-5xl gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { value: "8", label: "Módulos integrados" },
              { value: "4", label: "Roles de usuario" },
              { value: "100%", label: "Basado en la nube" },
              { value: "24/7", label: "Acceso desde cualquier lugar" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-4xl font-extrabold text-primary">{stat.value}</p>
                <p className="mt-1 text-sm font-medium text-gray-500">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── CTA final ── */}
        <section className="bg-primary px-4 py-14 text-center sm:py-16">
          <h2 className="mb-3 text-3xl font-extrabold text-white">
            ¿Listo para gestionar tu ganado?
          </h2>
          <p className="mx-auto mb-8 max-w-lg text-base leading-relaxed text-cream/90">
            Únete a BoviTrack y lleva el control total de tus fincas, animales y
            producción desde hoy.
          </p>
          <Link
            to="/register"
            className="inline-block rounded-xl bg-white px-8 py-3.5 text-base font-bold text-primary shadow-lg transition-all hover:bg-cream hover:shadow-xl active:scale-[0.98]"
          >
            Crear cuenta gratis
          </Link>
        </section>
      </main>

      <Footer />
    </div>
  );
}
