import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  FileUp, Check, X, Search, SlidersHorizontal, Settings2, ChevronDown,
  Eye, Pencil, Trash2, Pin, MoveLeft, MoveRight, Save, BookOpen, Download, Plus,
} from "lucide-react";
import { listBovines, deleteBovine, importBovinesCsv, type BovineResponse, type ImportResult } from "../../api/bovines";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { listPaddocks, type PaddockResponse } from "../../api/paddocks";
import { listMilkProduction, type MilkProductionResponse } from "../../api/milk_production";
import { listConsumptions, type ConsumptionResponse } from "../../api/food";
import { listTreatments, type TreatmentResponse } from "../../api/treatments";
import { listMovements, type MovementResponse } from "../../api/movements";
import { listReproductiveEvents, type ReproductiveEventResponse } from "../../api/reproductive_events";
import { getApiErrorMessage } from "../../api/errors";
import Pagination from "../Pagination";
import ConfirmDialog from "../ConfirmDialog";
import BovineFormModal from "./BovineFormModal";
import ColumnCustomizePanel from "./ColumnCustomizePanel";
import AdvancedFiltersPanel from "./AdvancedFiltersPanel";
import {
  buildFilterFields, calcAgeMonths, conditionToChip, conditionsActive, DEFAULT_VISIBLE_COLUMNS,
  defaultOpForType, exportCsv, matchesConditions, COLUMN_DEFS,
  type ColumnDef, type EnrichedBovine, type FilterCondition, type FilterFieldDef,
} from "./bovineColumns";

interface Props {
  farmId: string;
}

const SEX_BADGE: Record<string, string> = {
  macho: "bg-blue-50 text-blue-700",
  hembra: "bg-pink-50 text-pink-700",
};

const STATUS_BADGE: Record<string, string> = {
  activo: "bg-green-50 text-green-700",
  vendido: "bg-surface-alt text-text-secondary",
  muerto: "bg-red-50 text-red-700",
  retirado: "bg-yellow-50 text-yellow-700",
};

export interface SavedView {
  name: string;
  order: string[];
  visible: string[];
  sortKey: string;
  sortDir: "asc" | "desc";
  conditions: FilterCondition[];
}

const configKey = (farmId: string) => `bovitrack:bovine-config:${farmId}`;
const viewsKey = (farmId: string) => `bovitrack:bovine-views:${farmId}`;

const estWidth = (def: ColumnDef) => Math.max(96, (def.label.length * 7) + 44);

export default function BovineList({ farmId }: Props) {
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [milkRecords, setMilkRecords] = useState<MilkProductionResponse[]>([]);
  const [consumptions, setConsumptions] = useState<ConsumptionResponse[]>([]);
  const [treatments, setTreatments] = useState<TreatmentResponse[]>([]);
  const [movements, setMovements] = useState<MovementResponse[]>([]);
  const [reproEvents, setReproEvents] = useState<ReproductiveEventResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<BovineResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [showColumns, setShowColumns] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [search, setSearch] = useState("");
  const [conditions, setConditions] = useState<FilterCondition[]>([]);
  const [order, setOrder] = useState<string[]>(DEFAULT_VISIBLE_COLUMNS);
  const [pinned, setPinned] = useState<Set<string>>(new Set(["identification_number"]));
  const [sortKey, setSortKey] = useState("identification_number");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);
  const [savedViews, setSavedViews] = useState<SavedView[]>([]);
  const [showSaveView, setShowSaveView] = useState(false);
  const [viewName, setViewName] = useState("");
  const [menuFor, setMenuFor] = useState<string | null>(null);
  const [menuAddCol, setMenuAddCol] = useState(false);
  const perPage = 8;
  const fileRef = useRef<HTMLInputElement>(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);

  const visible = useMemo(() => new Set(order), [order]);
  const visibleColumns = useMemo(() => {
    const defs = COLUMN_DEFS.filter((c) => visible.has(c.key));
    defs.sort((a, b) => order.indexOf(a.key) - order.indexOf(b.key));
    return defs;
  }, [order, visible]);

  const columnGroups = useMemo(() => {
    const groups = new Map<string, ColumnDef[]>();
    for (const c of COLUMN_DEFS) {
      const arr = groups.get(c.group) ?? [];
      arr.push(c);
      groups.set(c.group, arr);
    }
    return [...groups.entries()];
  }, []);

  /* ── Persistencia localStorage ── */
  useEffect(() => {
    try {
      const raw = localStorage.getItem(configKey(farmId));
      if (raw) {
        const cfg = JSON.parse(raw) as { order?: string[]; sortKey?: string; sortDir?: "asc" | "desc"; conditions?: FilterCondition[] };
        setOrder(cfg.order?.length ? cfg.order : DEFAULT_VISIBLE_COLUMNS);
        setSortKey(cfg.sortKey ?? "identification_number");
        setSortDir(cfg.sortDir ?? "asc");
        setConditions(cfg.conditions ?? []);
      }
      const rawViews = localStorage.getItem(viewsKey(farmId));
      if (rawViews) setSavedViews(JSON.parse(rawViews) as SavedView[]);
    } catch {
      /* sin restauración si hay error de parseo */
    }
  }, [farmId]);

  useEffect(() => {
    try {
      localStorage.setItem(configKey(farmId), JSON.stringify({ order, sortKey, sortDir, conditions }));
      localStorage.setItem(viewsKey(farmId), JSON.stringify(savedViews));
    } catch {
      /* almacenamiento no disponible */
    }
  }, [farmId, order, sortKey, sortDir, conditions, savedViews]);

  /* ── Carga de datos ── */
  const enriched: EnrichedBovine[] = useMemo(() => {
    const landName = new Map(landPlots.map((l) => [l.id, l.name]));
    const paddockName = new Map(paddocks.map((p) => [p.id, p.name]));
    const labelById = new Map(bovines.map((b) => [b.id, b.identification_number]));

    const milkMap = new Map<string, { total: number; count: number; lastDate: string | null }>();
    for (const m of milkRecords) {
      if (!m.bovine_id) continue;
      const cur = milkMap.get(m.bovine_id) ?? { total: 0, count: 0, lastDate: null };
      cur.total += Number(m.quantity_liters) || 0;
      cur.count += 1;
      if (cur.lastDate === null || m.milking_date > cur.lastDate) cur.lastDate = m.milking_date;
      milkMap.set(m.bovine_id, cur);
    }
    const feedMap = new Map<string, { count: number; totalQty: number; lastDate: string | null }>();
    for (const c of consumptions) {
      if (!c.bovine_id) continue;
      const cur = feedMap.get(c.bovine_id) ?? { count: 0, totalQty: 0, lastDate: null };
      cur.count += 1;
      cur.totalQty += Number(c.quantity) || 0;
      if (cur.lastDate === null || c.feeding_date > cur.lastDate) cur.lastDate = c.feeding_date;
      feedMap.set(c.bovine_id, cur);
    }

    const treatmentMap = new Map<string, { count: number; last: string | null; next: string | null; lastType: string | null; lastProduct: string | null }>();
    for (const t of treatments) {
      if (!t.bovine_id) continue;
      const cur = treatmentMap.get(t.bovine_id) ?? { count: 0, last: null, next: null, lastType: null, lastProduct: null };
      cur.count += 1;
      if (cur.last === null || t.application_date > cur.last) {
        cur.last = t.application_date;
        cur.lastType = t.treatment_type;
        cur.lastProduct = t.product_name;
      }
      if (t.next_application_date && (cur.next === null || t.next_application_date > cur.next)) cur.next = t.next_application_date;
      treatmentMap.set(t.bovine_id, cur);
    }

    const movementMap = new Map<string, { count: number; lastDate: string | null; lastType: string | null; origin: string | null; destination: string | null; counterparty: string | null; price: number | null; reason: string | null }>();
    for (const m of movements) {
      if (!m.bovine_id) continue;
      const cur = movementMap.get(m.bovine_id) ?? { count: 0, lastDate: null, lastType: null, origin: null, destination: null, counterparty: null, price: null, reason: null };
      cur.count += 1;
      if (cur.lastDate === null || m.movement_date > cur.lastDate) {
        cur.lastDate = m.movement_date;
        cur.lastType = m.movement_type;
        cur.origin = m.origin_farm_name ?? null;
        cur.destination = m.destination_farm_name ?? null;
        cur.counterparty = m.counterparty_name ?? null;
        cur.price = m.price ?? null;
        cur.reason = m.reason ?? null;
      }
      movementMap.set(m.bovine_id, cur);
    }

    const reproMap = new Map<string, {
      services: number; calvings: number; aborts: number; lastService: string | null; lastCalving: string | null;
      lastAbort: string | null; lastEvent: string | null; lastEventDate: string | null; lastEventResult: string | null;
      lastBullId: string | null; lastCalfId: string | null; nextDue: string | null;
    }>();
    for (const e of reproEvents) {
      const cur = reproMap.get(e.bovine_id) ?? {
        services: 0, calvings: 0, aborts: 0, lastService: null, lastCalving: null, lastAbort: null,
        lastEvent: null, lastEventDate: null, lastEventResult: null, lastBullId: null, lastCalfId: null, nextDue: null,
      };
      if (e.event_type === "servicio") {
        cur.services += 1;
        if (cur.lastService === null || e.event_date > cur.lastService) {
          cur.lastService = e.event_date;
          cur.lastBullId = e.bull_id ?? cur.lastBullId;
          cur.nextDue = e.due_date ?? cur.nextDue;
        }
      }
      if (e.event_type === "parto") {
        cur.calvings += 1;
        if (cur.lastCalving === null || e.event_date > cur.lastCalving) {
          cur.lastCalving = e.event_date;
          cur.lastCalfId = e.calf_id ?? cur.lastCalfId;
        }
      }
      if (e.event_type === "aborto" && (cur.lastAbort === null || e.event_date > cur.lastAbort)) {
        cur.aborts += 1;
        cur.lastAbort = e.event_date;
      }
      if (cur.lastEventDate === null || e.event_date > cur.lastEventDate) {
        cur.lastEventDate = e.event_date;
        cur.lastEvent = e.event_type;
        cur.lastEventResult = e.result ?? null;
      }
      reproMap.set(e.bovine_id, cur);
    }

    return bovines.map((b) => {
      const milk = milkMap.get(b.id) ?? { total: 0, count: 0, lastDate: null };
      const feed = feedMap.get(b.id) ?? { count: 0, totalQty: 0, lastDate: null };
      const tr = treatmentMap.get(b.id) ?? { count: 0, last: null, next: null, lastType: null, lastProduct: null };
      const mv = movementMap.get(b.id) ?? { count: 0, lastDate: null, lastType: null, origin: null, destination: null, counterparty: null, price: null, reason: null };
      const repro = reproMap.get(b.id) ?? {
        services: 0, calvings: 0, aborts: 0, lastService: null, lastCalving: null, lastAbort: null,
        lastEvent: null, lastEventDate: null, lastEventResult: null, lastBullId: null, lastCalfId: null, nextDue: null,
      };
      return {
        ...b,
        land_plot_name: b.land_plot_id ? landName.get(b.land_plot_id) ?? null : null,
        paddock_name: b.paddock_id ? paddockName.get(b.paddock_id) ?? null : null,
        age_months: calcAgeMonths(b.birth_date),
        total_milk: milk.total,
        milk_count: milk.count,
        avg_milk: milk.count > 0 ? milk.total / milk.count : 0,
        last_milking_date: milk.lastDate,
        ration_count: feed.count,
        total_feed_quantity: feed.totalQty,
        last_feeding_date: feed.lastDate,
        treatment_count: tr.count,
        last_treatment_date: tr.last,
        next_treatment_date: tr.next,
        last_treatment_type: tr.lastType,
        last_treatment_product: tr.lastProduct,
        movement_count: mv.count,
        last_movement_date: mv.lastDate,
        last_movement_type: mv.lastType,
        last_movement_origin: mv.origin,
        last_movement_destination: mv.destination,
        last_movement_counterparty: mv.counterparty,
        last_movement_price: mv.price,
        last_movement_reason: mv.reason,
        service_count: repro.services,
        calving_count: repro.calvings,
        abort_count: repro.aborts,
        last_service_date: repro.lastService,
        last_calving_date: repro.lastCalving,
        last_abort_date: repro.lastAbort,
        last_event_type: repro.lastEvent,
        last_event_date: repro.lastEventDate,
        last_event_result: repro.lastEventResult,
        next_due_date: repro.nextDue,
        bull_label: repro.lastBullId ? labelById.get(repro.lastBullId) ?? repro.lastBullId : null,
        calf_label: repro.lastCalfId ? labelById.get(repro.lastCalfId) ?? repro.lastCalfId : null,
        father_label: b.father_id ? labelById.get(b.father_id) ?? b.father_id : null,
        mother_label: b.mother_id ? labelById.get(b.mother_id) ?? b.mother_id : null,
      };
    });
  }, [bovines, landPlots, paddocks, milkRecords, consumptions, treatments, movements, reproEvents]);

  const fields: FilterFieldDef[] = useMemo(() => buildFilterFields({ rows: enriched, landPlots, paddocks }), [enriched, landPlots, paddocks]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return enriched.filter((b) => {
      if (!matchesConditions(b, fields, conditions)) return false;
      if (!q) return true;
      const hay = [
        b.identification_number, b.name, b.breed, b.color, b.purpose, b.markings,
        b.land_plot_name, b.paddock_name,
      ].filter(Boolean).join(" ").toLowerCase();
      return hay.includes(q);
    });
  }, [enriched, fields, conditions, search]);

  const { total, pageCount, safePage, paginated, start, end } = useMemo(() => {
    const arr = [...filtered];
    const def = COLUMN_DEFS.find((c) => c.key === sortKey);
    arr.sort((a, b) => {
      let av: string | number | null = def ? def.getValue(a) : a.identification_number;
      let bv: string | number | null = def ? def.getValue(b) : b.identification_number;
      if (def?.type === "string") {
        av = String(av ?? "").toLowerCase();
        bv = String(bv ?? "").toLowerCase();
        const cmp = av < bv ? -1 : av > bv ? 1 : 0;
        return sortDir === "asc" ? cmp : -cmp;
      }
      const an = Number(av ?? -1);
      const bn = Number(bv ?? -1);
      const cmp = an - bn;
      return sortDir === "asc" ? cmp : -cmp;
    });
    const count = arr.length;
    const pages = Math.max(1, Math.ceil(count / perPage));
    const p = Math.min(page, pages);
    return {
      total: count,
      pageCount: pages,
      safePage: p,
      paginated: arr.slice((p - 1) * perPage, p * perPage),
      start: count === 0 ? 0 : (p - 1) * perPage + 1,
      end: Math.min(p * perPage, count),
    };
  }, [filtered, sortKey, sortDir, page]);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [b, lp, p, milk, consum, tr, mv, repro] = await Promise.all([
        listBovines(farmId),
        listLandPlots(farmId, true),
        listPaddocks(farmId),
        listMilkProduction(farmId).catch(() => [] as MilkProductionResponse[]),
        listConsumptions(farmId).catch(() => [] as ConsumptionResponse[]),
        listTreatments(farmId).catch(() => [] as TreatmentResponse[]),
        listMovements(farmId).catch(() => [] as MovementResponse[]),
        listReproductiveEvents(farmId).catch(() => [] as ReproductiveEventResponse[]),
      ]);
      setBovines(b);
      setLandPlots(lp);
      setPaddocks(p);
      setMilkRecords(milk);
      setConsumptions(consum);
      setTreatments(tr);
      setMovements(mv);
      setReproEvents(repro);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los bovinos"));
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchData(); }, [farmId]);

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setImporting(true);
    setImportResult(null);
    setError("");
    try {
      const result = await importBovinesCsv(farmId, file);
      setImportResult(result);
      await fetchData();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo importar el archivo"));
    } finally {
      setImporting(false);
    }
  };

  const [toDelete, setToDelete] = useState<BovineResponse | null>(null);

  const handleDelete = async () => {
    if (!toDelete) return;
    setActionLoading(toDelete.id);
    try {
      await deleteBovine(farmId, toDelete.id);
      setToDelete(null);
      await fetchData();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo eliminar el bovino"));
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuccess = () => {
    setShowModal(false);
    setEditing(undefined);
    fetchData();
  };

  /* ── Orden de columnas ── */
  const handleApplyColumns = async (orderedKeys: string[], vis: Set<string>) => {
    const allKeys = orderedKeys;
    setVisibleConfig(allKeys, vis);
    setShowColumns(false);
  };

  const setVisibleConfig = (allKeys: string[], vis: Set<string>) => {
    setOrder(allKeys.filter((k) => vis.has(k)));
  };

  const togglePinned = (key: string) => {
    setPinned((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
    setMenuFor(null);
  };

  const moveColumn = (key: string, dir: -1 | 1) => {
    setOrder((prev) => {
      const idx = prev.indexOf(key);
      if (idx === -1) return prev;
      const next = [...prev];
      const target = idx + dir;
      if (target < 0 || target >= next.length) return prev;
      [next[idx], next[target]] = [next[target], next[idx]];
      return next;
    });
    setMenuFor(null);
  };

  const hideColumn = (key: string) => {
    setOrder((prev) => prev.filter((k) => k !== key));
    setPinned((prev) => {
      const next = new Set(prev);
      next.delete(key);
      return next;
    });
    setMenuFor(null);
  };

  const toggleColumnFromMenu = (key: string) => {
    setOrder((prev) => (prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]));
    if (order.includes(key)) {
      setPinned((prev) => {
        const next = new Set(prev);
        next.delete(key);
        return next;
      });
    }
  };

  const applySort = (key: string, dir: "asc" | "desc") => {
    setSortKey(key);
    setSortDir(dir);
    setPage(1);
    setMenuFor(null);
  };

  const handleSortClick = (key: string) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
    setPage(1);
  };

  /* ── Filtros ── */
  const setQuick = (field: string, value?: string) => {
    setConditions((prev) => {
      let next = prev.filter((c) => c.field !== field);
      if (value) {
        const f = fields.find((x) => x.key === field);
        next = next.concat([{ id: Math.random().toString(36).slice(2), connector: next.length > 0 ? "AND" : "AND", field, op: defaultOpForType(f?.type ?? "text"), value }]);
      }
      return next;
    });
    setPage(1);
  };

  const addConditionFromField = (fieldKey: string) => {
    const f = fields.find((x) => x.key === fieldKey);
    if (!f) return;
    setConditions((prev) => prev.concat([{
      id: Math.random().toString(36).slice(2),
      connector: prev.length > 0 ? "AND" : "AND",
      field: f.key,
      op: defaultOpForType(f.type),
      value: "",
    }]));
    setShowFilters(true);
  };

  const filterFromColumn = (def: ColumnDef) => {
    const f = fields.find((x) => x.key === def.filterField);
    if (!f) { setShowFilters(true); setMenuFor(null); return; }
    setConditions((prev) => prev.concat([{
      id: Math.random().toString(36).slice(2),
      connector: prev.length > 0 ? "AND" : "AND",
      field: f.key,
      op: defaultOpForType(f.type),
      value: "",
    }]));
    setShowFilters(true);
    setMenuFor(null);
  };

  const clearAll = () => {
    setConditions([]);
    setSearch("");
    setPage(1);
  };

  const removeCondition = (id: string) => {
    setConditions((prev) => prev.filter((c) => c.id !== id));
  };

  /* ── Vistas guardadas ── */
  const saveView = () => {
    const name = viewName.trim();
    if (!name) return;
    const view: SavedView = { name, order, visible: [...order], sortKey, sortDir, conditions };
    setSavedViews((prev) => [...prev.filter((v) => v.name !== name), view]);
    setViewName("");
    setShowSaveView(false);
  };

  const applyView = (view: SavedView) => {
    setOrder(view.visible);
    setSortKey(view.sortKey);
    setSortDir(view.sortDir);
    setConditions(view.conditions);
    setPinned((prev) => new Set([...(prev.size ? [view.visible[0]] : [])]));
    setPage(1);
  };

  const deleteView = (name: string) => {
    setSavedViews((prev) => prev.filter((v) => v.name !== name));
  };

  const chipCount = conditionsActive(conditions);

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-text-primary">Bovinos</h2>
          <p className="text-xs text-text-muted">
            {total} registro{total !== 1 ? "s" : ""}
            {chipCount > 0 && ` · ${chipCount} filtro${chipCount !== 1 ? "s" : ""}`}
          </p>
        </div>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          {savedViews.length > 0 && (
            <div className="relative">
              <div className="flex items-center rounded-lg border border-border px-2 py-1 text-sm">
                <BookOpen size={15} className="mr-1 text-text-muted" />
                <select
                  className="bg-transparent text-sm text-text-secondary focus:outline-none"
                  value=""
                  onChange={(e) => {
                    const v = savedViews.find((x) => x.name === e.target.value);
                    if (v) applyView(v);
                  }}
                >
                  <option value="" disabled>Mis vistas</option>
                  {savedViews.map((v) => (
                    <option key={v.name} value={v.name}>{v.name}</option>
                  ))}
                </select>
              </div>
              {savedViews.length > 0 && (
                <div className="absolute right-0 top-full z-20 mt-1 w-56 rounded-lg border border-border bg-surface p-1 shadow-lg">
                  {savedViews.map((v) => (
                    <div key={v.name} className="flex items-center justify-between rounded px-2 py-1 hover:bg-surface-alt">
                      <button onClick={() => applyView(v)} className="truncate text-left text-xs text-text-secondary">{v.name}</button>
                      <button onClick={() => deleteView(v.name)} aria-label={`Eliminar vista ${v.name}`} className="text-text-muted hover:text-red-500"><X size={13} /></button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          <button
            onClick={() => setShowSaveView((s) => !s)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
          >
            <Save size={15} /> Guardar vista
          </button>
          {showSaveView && (
            <div className="flex items-center gap-1.5">
              <input
                autoFocus
                value={viewName}
                onChange={(e) => setViewName(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") saveView(); }}
                placeholder="Nombre de la vista"
                className="w-44 rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
              <button onClick={saveView} className="rounded-lg bg-primary px-3 py-2 text-sm font-bold text-white hover:bg-primary-light">Guardar</button>
            </div>
          )}
          <button
            onClick={() => exportCsv(filtered, order, visible)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
          >
            <Download size={15} /> Exportar
          </button>
          <button onClick={() => fileRef.current?.click()} disabled={importing} className="rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt disabled:opacity-50">
            <FileUp size={15} className="mr-1 inline align-text-bottom" /> {importing ? "Importando…" : "Importar CSV"}
          </button>
          <button onClick={() => { setEditing(undefined); setShowModal(true); }} className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
            + Registrar bovino
          </button>
        </div>
        <input ref={fileRef} type="file" accept=".csv,text/csv" onChange={handleImportFile} className="hidden" />
      </div>

      {/* Buscador + filtros rápidos */}
      <div className="mb-3 flex flex-col gap-2 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por ID, nombre, arete, raza…"
            className="w-full rounded-lg border border-border bg-white py-2 pl-9 pr-3 text-sm focus:border-primary focus:outline-none"
          />
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { label: "Todos", value: undefined },
            { label: "Machos", value: { field: "sex", v: "macho" } },
            { label: "Hembras", value: { field: "sex", v: "hembra" } },
            { label: "Activos", value: { field: "status", v: "activo" } },
          ].map((qb) => (
            <button
              key={qb.label}
              onClick={() => setQuick(qb.value?.field ?? "sex", qb.value ? qb.value.v : undefined)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                !qb.value
                  ? "bg-primary text-white"
                  : "bg-surface-alt text-text-secondary hover:bg-border"
              }`}
            >
              {qb.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chips de filtros activos */}
      {conditions.length > 0 && (
        <div className="mb-3 flex flex-wrap items-center gap-1.5">
          {conditions.map((c) => {
            const f = fields.find((x) => x.key === c.field);
            if (!f) return null;
            return (
              <button
                key={c.id}
                onClick={() => removeCondition(c.id)}
                className="group inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary hover:bg-red-50 hover:text-red-600"
              >
                <span className="uppercase">{conditionToChip(f, c)}</span>
                <X size={13} className="text-primary/60 group-hover:text-red-500" />
              </button>
            );
          })}
          <button onClick={clearAll} className="text-xs font-semibold text-text-muted underline hover:text-text-secondary">
            Limpiar filtros
          </button>
        </div>
      )}

      {importResult && (
        <div className="mb-3 rounded-lg border px-4 py-3 text-sm">
          <div className="flex items-center justify-between">
            <p className="font-semibold text-text-primary">
              <Check size={15} className="mr-1 inline text-green-600" />
              {importResult.imported} importado{importResult.imported !== 1 ? "s" : ""} · {importResult.failed} con error{importResult.failed !== 1 ? "es" : ""}
            </p>
            <button onClick={() => setImportResult(null)} aria-label="Cerrar" className="text-text-muted hover:text-text-secondary"><X size={16} /></button>
          </div>
          {importResult.errors.length > 0 && (
            <ul className="mt-2 space-y-1 text-xs text-red-600">
              {importResult.errors.slice(0, 6).map((err, i) => (
                <li key={i}>Fila {err.row}: {err.error}</li>
              ))}
              {importResult.errors.length > 6 && <li>… y {importResult.errors.length - 6} más.</li>}
            </ul>
          )}
          <p className="mt-1 text-xs text-text-muted">
            Plantilla: <span className="font-mono">identification_number, name, sex, birth_date, entry_type, entry_date, birth_weight, current_weight, breed, purpose, land_plot, paddock</span>
          </p>
        </div>
      )}

      {error && <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : bovines.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay bovinos registrados</p>
        </div>
      ) : total === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">Ningún bovino coincide con los filtros</p>
          <button onClick={clearAll} className="mt-2 text-xs font-semibold text-primary hover:underline">
            Limpiar filtros
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                {/* Columna sticky de ID */}
                {visibleColumns.length === 0 && (
                  <th className="pb-2 pr-4">ID</th>
                )}
                {visibleColumns.map((def) => {
                  const isPinned = pinned.has(def.key);
                  const pinnedBefore = visibleColumns.filter((c) => c.key !== def.key && pinned.has(c.key));
                  const left = isPinned ? pinnedBefore.reduce((acc, c) => acc + estWidth(c), 0) : 0;
                  return (
                    <th
                      key={def.key}
                      className="relative pb-2 pr-4"
                      style={{
                        ...(isPinned ? { position: "sticky", left, zIndex: 5, background: "var(--color-surface, #fff)" } : {}),
                      }}
                    >
                      <div className="flex items-center gap-1">
                        <button onClick={() => handleSortClick(def.key)} className="flex items-center gap-1 uppercase">
                          {def.label.split(" (kg)")[0].split(" (L)")[0]}
                          {(sortKey === def.key) && (sortDir === "asc" ? "▲" : "▼")}
                        </button>
                        <button
                          onClick={() => setMenuFor(menuFor === def.key ? null : def.key)}
                          aria-label={`Menú de columna ${def.label}`}
                          className={`rounded p-0.5 transition-colors ${menuFor === def.key ? "text-primary" : "text-text-muted hover:text-text-secondary"}`}
                        >
                          <ChevronDown size={14} />
                        </button>
                      </div>
                      {menuFor === def.key && (
                        <>
                          <div className="fixed inset-0 z-10" onClick={() => setMenuFor(null)} />
                          <div className="absolute left-0 top-full z-20 mt-1 w-52 rounded-lg border border-border bg-surface p-1 shadow-xl">
                            <button onClick={() => applySort(def.key, "asc")} className="block w-full rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">Ordenar menor a mayor</button>
                            <button onClick={() => applySort(def.key, "desc")} className="block w-full rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">Ordenar mayor a menor</button>
                            <button onClick={() => applySort(def.key, "asc")} className="block w-full rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">Ordenar A → Z</button>
                            <button onClick={() => applySort(def.key, "desc")} className="block w-full rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">Ordenar Z → A</button>
                            <div className="my-1 border-t border-border" />
                            <button onClick={() => filterFromColumn(def)} className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">
                              <SlidersHorizontal size={13} /> Filtrar por {def.label.split(" (kg)")[0].toLowerCase()}
                            </button>
                            <div className="my-1 border-t border-border" />
                            <button onClick={() => hideColumn(def.key)} className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs text-red-500 hover:bg-red-50">
                              <X size={13} /> Ocultar columna
                            </button>
                            <button onClick={() => togglePinned(def.key)} className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">
                              <Pin size={13} /> {isPinned ? "Desfijar columna" : "Fijar columna"}
                            </button>
                            <div className="my-1 border-t border-border" />
                            <button onClick={() => moveColumn(def.key, -1)} className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">
                              <MoveLeft size={13} /> Mover a la izquierda
                            </button>
                            <button onClick={() => moveColumn(def.key, 1)} className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-surface-alt">
                              <MoveRight size={13} /> Mover a la derecha
                            </button>
                          </div>
                        </>
                      )}
                    </th>
                  );
                })}
                <th className="relative pb-2">
                  <div className="flex items-center gap-1">
                    <span>Columnas</span>
                    <button
                      onClick={() => { setMenuAddCol((s) => !s); setMenuFor(null); }}
                      aria-label="Añadir o quitar columnas"
                      className={`rounded p-1 text-white transition-colors ${menuAddCol ? "bg-primary-dark" : "bg-primary hover:bg-primary-light"}`}
                    >
                      <Plus size={13} />
                    </button>
                  </div>
                  {menuAddCol && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setMenuAddCol(false)} />
                      <div className="absolute right-0 top-full z-20 mt-1 max-h-[28rem] w-72 overflow-y-auto rounded-lg border border-border bg-surface p-2 shadow-xl">
                        <div className="flex items-center justify-between px-2 py-1.5">
                          <p className="text-xs font-bold uppercase tracking-wide text-text-muted">Añadir columna</p>
                          <button onClick={() => { setMenuAddCol(false); setShowColumns(true); }} className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline">
                            <Settings2 size={12} /> Personalizar
                          </button>
                        </div>
                        {columnGroups.map(([group, defs]) => (
                          <div key={group} className="mb-1">
                            <p className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-text-muted">{group}</p>
                            <div className="space-y-0.5">
                              {defs.map((def) => {
                                const on = order.includes(def.key);
                                return (
                                  <label key={def.key} className={`flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-xs transition-colors ${on ? "bg-primary/5 text-text-primary" : "text-text-muted hover:bg-surface-alt"}`}>
                                    <input
                                      type="checkbox"
                                      checked={on}
                                      onChange={() => toggleColumnFromMenu(def.key)}
                                      className="h-4 w-4 accent-primary"
                                    />
                                    <span className="truncate">{def.label}</span>
                                  </label>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map((b) => (
                <tr key={b.id} className="hover:bg-surface-alt">
                  {visibleColumns.length === 0 && (
                    <td className="py-3 pr-4 font-mono text-xs text-text-secondary">{b.identification_number}</td>
                  )}
                  {visibleColumns.map((def) => {
                    const isPinned = pinned.has(def.key);
                    const pinnedBefore = visibleColumns.filter((c) => c.key !== def.key && pinned.has(c.key));
                    const left = isPinned ? pinnedBefore.reduce((acc, c) => acc + estWidth(c), 0) : 0;
                    const value = def.getValue(b);
                    return (
                      <td
                        key={def.key}
                        className="py-3 pr-4 whitespace-nowrap text-text-secondary"
                        style={{ ...(isPinned ? { position: "sticky", left, zIndex: 4, background: "var(--color-surface, #fff)" } : {}) }}
                      >
                        {def.key === "identification_number" ? (
                          <span className="font-mono text-xs">{b.identification_number}</span>
                        ) : def.key === "name" ? (
                          <span className="font-medium text-text-primary">{b.name ?? "—"}</span>
                        ) : def.key === "sex" ? (
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEX_BADGE[b.sex] ?? "bg-surface-alt text-text-secondary"}`}>{b.sex}</span>
                        ) : def.key === "status" ? (
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[b.status] ?? "bg-surface-alt text-text-secondary"}`}>{b.status}</span>
                        ) : def.key === "current_weight" ? (
                          b.current_weight ? <span>{b.current_weight} kg</span> : <span className="text-text-muted">—</span>
                        ) : def.key === "birth_weight" ? (
                          b.birth_weight ? <span>{b.birth_weight} kg</span> : <span className="text-text-muted">—</span>
                        ) : def.key === "total_milk" || def.key === "milk_count" || def.key === "avg_milk" ? (
                          value && Number(value) > 0 ? <span className="font-semibold text-blue-700">{def.format ? def.format(b) : String(value)}</span> : <span className="text-text-muted">—</span>
                        ) : def.key === "ration_count" ? (
                          value && Number(value) > 0 ? <span className="font-semibold text-green-700">{String(value)}</span> : <span className="text-text-muted">—</span>
                        ) : (
                          def.format ? def.format(b) || <span className="text-text-muted">—</span> : String(value ?? "—")
                        )}
                      </td>
                    );
                  })}
                  <td className="py-3">
                    <div className="flex gap-2">
                      <Link to={`/farms/${farmId}/bovines/${b.id}`} className="rounded px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10 no-underline">
                        <Eye size={14} className="mr-0.5 inline align-text-bottom" /> Ver
                      </Link>
                      <button onClick={() => { setEditing(b); setShowModal(true); }} className="rounded px-2 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt">
                        <Pencil size={14} className="mr-0.5 inline align-text-bottom" /> Editar
                      </button>
                      <button onClick={() => setToDelete(b)} disabled={actionLoading === b.id} className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                        <Trash2 size={14} className="mr-0.5 inline align-text-bottom" /> Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {visibleColumns.length === 0 && (
            <p className="mt-3 text-center text-xs text-text-muted">
              Todas las columnas están ocultas.{` `}
              <button onClick={() => setShowColumns(true)} className="font-semibold text-primary hover:underline">Personalizar columnas</button>
            </p>
          )}

          <Pagination page={safePage} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
        </div>
      )}

      {showModal && (
        <BovineFormModal farmId={farmId} landPlots={landPlots} paddocks={paddocks} existing={editing} onSuccess={handleSuccess} onClose={() => { setShowModal(false); setEditing(undefined); }} />
      )}

      {showColumns && (
        <ColumnCustomizePanel
          onClose={() => setShowColumns(false)}
          orderedKeys={order}
          visible={visible}
          onApply={handleApplyColumns}
        />
      )}

      <AdvancedFiltersPanel open={showFilters} onClose={() => setShowFilters(false)} fields={fields} conditions={conditions} onChange={(c) => { setConditions(c); setPage(1); }} onQuickField={addConditionFromField} />

      <ConfirmDialog
        open={!!toDelete}
        title="Eliminar bovino"
        message={`¿Eliminar el bovino "${toDelete?.identification_number}"? Se marcará como retirado y dejará de aparecer en el hato.`}
        confirmLabel="Eliminar"
        loading={actionLoading !== null}
        onConfirm={handleDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}