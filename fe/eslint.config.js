import fs from 'node:fs'
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'

// ══════════════════════════════════════════════════════════════
// Fronteras arquitectónicas del frontend (equivalente a import-linter en el backend)
//
// ¿Qué?    Reglas no-restricted-imports que dicen qué capa puede importar a cuál.
// ¿Para?   Que la estructura por features no dependa de la disciplina de cada
//          desarrollador: `pnpm lint` falla y dice qué import rompe la frontera.
// ¿Impacto? Capas (ver src/README.md):
//            app      -> compone todo (rutas, providers, layout de la app)
//            features -> una carpeta por dominio; se usan entre sí SOLO por su index.ts
//            shared   -> UI, hooks y layout genéricos (sin dominio)
//            core     -> infraestructura (cliente HTTP, errores de la API)
// ══════════════════════════════════════════════════════════════

const features = fs.existsSync('src/features')
  ? fs.readdirSync('src/features', { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)
  : []

const rule = (regex, message) => ({ regex, message })

// Capas de features (como "capas de módulos" de import-linter en el backend): una
// feature solo usa features de niveles INFERIORES; las del mismo nivel no se usan
// entre sí. Así no puede formarse un ciclo. Una feature nueva DEBE declararse aquí.
const FEATURE_LAYERS = [
  // consumidoras: nadie depende de ellas
  ['herd', 'documents', 'team', 'economics', 'reports', 'notifications', 'audit'],
  ['health', 'inventory', 'milk_production', 'reproduction'],
  ['livestock'],
  ['farms'],
  ['identity'], // base
]
const undeclared = features.filter((f) => !FEATURE_LAYERS.flat().includes(f))
if (undeclared.length) {
  throw new Error(`eslint.config.js: declara en FEATURE_LAYERS las features nuevas: ${undeclared.join(', ')}`)
}
const levelOf = (f) => FEATURE_LAYERS.findIndex((layer) => layer.includes(f))
const layerRule = (f) => {
  const notAllowed = FEATURE_LAYERS.slice(0, levelOf(f) + 1).flat().filter((g) => g !== f)
  const allowed = FEATURE_LAYERS.slice(levelOf(f) + 1).flat().join(', ') || 'ninguna'
  return notAllowed.length
    ? [rule(`^@/features/(${notAllowed.join('|')})(/|$)`, `Capas de features: "${f}" solo puede usar features de niveles inferiores (${allowed}).`)]
    : []
}
const COMMON = [
  rule('^@/features/[^/]+/.+', 'Importa una feature solo por su API pública: "@/features/<feature>".'),
  rule('^@/(shared|core)/[^/]+/.+', 'Importa shared/core por su API pública: "@/shared/<x>" o "@/core/<x>".'),
  rule('^(\\.\\./)+(app|core|shared|features)(/|$)', 'Entre capas usa el alias "@/…", no rutas relativas.'),
]
const restrict = (...extra) => ['error', { patterns: [...COMMON, ...extra] }]

const NO_DOMAIN = [
  rule('^@/(app|features)(/|$)', 'shared y core no conocen el dominio: no pueden importar app ni features.'),
]

export default tseslint.config(
  { ignores: ['dist', 'coverage'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'no-restricted-imports': restrict(),
    },
  },
  // ── core: infraestructura pura
  {
    files: ['src/core/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': restrict(...NO_DOMAIN, rule('^@/shared(/|$)', 'core no depende de shared.')),
    },
  },
  // ── shared: piezas genéricas, sin dominio
  {
    files: ['src/shared/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': restrict(...NO_DOMAIN, rule('^@/core(/|$)', 'shared no depende de core.')),
    },
  },
  // ── features: una por dominio. Dentro de la feature, rutas relativas; hacia
  //    afuera, solo APIs públicas. Como máximo UN nivel de subcarpetas
  //    (features/<f>/components/X.tsx), así "../../" siempre sale de la feature.
  ...features.map((f) => ({
    files: [`src/features/${f}/**/*.{ts,tsx}`],
    rules: {
      'no-restricted-imports': restrict(
        rule('^@/app(/|$)', 'Una feature no importa app: app es quien compone las features.'),
        rule(`^@/features/${f}(/|$)`, `Dentro de "${f}" usa rutas relativas (importar tu propio index.ts crea un ciclo).`),
        ...layerRule(f),
        rule('^\\.\\./\\.\\./','No salgas de la feature con "../../": usa "@/features/<otra>" o "@/shared/…".'),
      ),
    },
  })),
  ...features.map((f) => ({
    files: [`src/features/${f}/*.{ts,tsx}`],
    rules: {
      'no-restricted-imports': restrict(
        rule('^@/app(/|$)', 'Una feature no importa app: app es quien compone las features.'),
        rule(`^@/features/${f}(/|$)`, `Dentro de "${f}" usa rutas relativas (importar tu propio index.ts crea un ciclo).`),
        ...layerRule(f),
        rule('^\\.\\./','No salgas de la feature con "../": usa "@/features/<otra>" o "@/shared/…".'),
      ),
    },
  })),
)
