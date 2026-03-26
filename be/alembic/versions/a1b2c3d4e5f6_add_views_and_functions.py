"""add views and functions

Revision ID: a1b2c3d4e5f6
Revises: fb563e20cc8e
Create Date: 2026-03-25 21:00:00.000000
"""
from typing import Sequence, Union
from alembic import op


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fb563e20cc8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Vista 1: Resumen por finca ──────────────────────────
    # Muestra totales de bovinos, lotes, potreros y área por finca.
    op.execute("""
        CREATE OR REPLACE VIEW v_farm_summary AS
        SELECT
            f.id              AS farm_id,
            f.name            AS farm_name,
            f.farm_identifier,
            u.first_name || ' ' || u.last_name AS owner_name,
            f.total_area,
            f.area_unit,
            COALESCE(b.total_bovines, 0)   AS total_bovines,
            COALESCE(b.active_bovines, 0)  AS active_bovines,
            COALESCE(lp.total_land_plots, 0) AS total_land_plots,
            COALESCE(p.total_paddocks, 0)  AS total_paddocks,
            f.is_active,
            f.created_at
        FROM farm f
        JOIN users u ON u.id = f.owner_id
        LEFT JOIN (
            SELECT farm_id,
                   COUNT(*)                          AS total_bovines,
                   COUNT(*) FILTER (WHERE is_active)  AS active_bovines
            FROM bovine GROUP BY farm_id
        ) b ON b.farm_id = f.id
        LEFT JOIN (
            SELECT farm_id, COUNT(*) AS total_land_plots
            FROM land_plot WHERE is_active GROUP BY farm_id
        ) lp ON lp.farm_id = f.id
        LEFT JOIN (
            SELECT farm_id, COUNT(*) AS total_paddocks
            FROM paddock WHERE is_active GROUP BY farm_id
        ) p ON p.farm_id = f.id;
    """)

    # ── Vista 2: Censo de bovinos por finca ─────────────────
    # Agrupa bovinos activos por finca, sexo y propósito.
    op.execute("""
        CREATE OR REPLACE VIEW v_bovine_census AS
        SELECT
            f.id        AS farm_id,
            f.name      AS farm_name,
            b.sex,
            b.purpose,
            b.status,
            COUNT(*)    AS total,
            ROUND(AVG(b.current_weight), 2) AS avg_weight
        FROM bovine b
        JOIN farm f ON f.id = b.farm_id
        GROUP BY f.id, f.name, b.sex, b.purpose, b.status;
    """)

    # ── Vista 3: Producción de leche diaria ─────────────────
    # Totaliza litros por finca y día para reportes.
    op.execute("""
        CREATE OR REPLACE VIEW v_milk_production_daily AS
        SELECT
            mp.farm_id,
            f.name AS farm_name,
            DATE(mp.milking_date) AS production_date,
            COUNT(*)              AS total_milkings,
            SUM(mp.quantity_liters) AS total_liters,
            ROUND(AVG(mp.quantity_liters), 2) AS avg_liters_per_milking
        FROM milk_production mp
        JOIN farm f ON f.id = mp.farm_id
        GROUP BY mp.farm_id, f.name, DATE(mp.milking_date);
    """)

    # ── Vista 4: Alertas de inventario bajo ─────────────────
    # Muestra alimentos cuyo stock actual está por debajo del mínimo.
    op.execute("""
        CREATE OR REPLACE VIEW v_low_stock_alerts AS
        SELECT
            fo.id         AS food_id,
            fo.farm_id,
            f.name        AS farm_name,
            fo.name       AS food_name,
            fo.category,
            fo.current_stock,
            fo.min_stock_alert,
            fo.unit_of_measure,
            ROUND(
                fo.current_stock / NULLIF(fo.min_stock_alert, 0) * 100, 1
            ) AS stock_percentage
        FROM food fo
        JOIN farm f ON f.id = fo.farm_id
        WHERE fo.is_active
          AND fo.min_stock_alert IS NOT NULL
          AND fo.current_stock <= fo.min_stock_alert;
    """)

    # ── Vista 5: Tareas pendientes ──────────────────────────
    # Tareas no completadas con datos del asignado y la finca.
    op.execute("""
        CREATE OR REPLACE VIEW v_pending_tasks AS
        SELECT
            t.id          AS task_id,
            t.farm_id,
            f.name        AS farm_name,
            t.title,
            t.task_type,
            t.priority,
            t.status,
            t.due_date,
            ua.first_name || ' ' || ua.last_name AS assigned_to_name,
            ub.first_name || ' ' || ub.last_name AS assigned_by_name,
            CASE
                WHEN t.due_date < NOW() THEN 'vencida'
                WHEN t.due_date < NOW() + INTERVAL '24 hours' THEN 'por_vencer'
                ELSE 'a_tiempo'
            END AS urgency
        FROM task t
        JOIN farm f ON f.id = t.farm_id
        JOIN users ua ON ua.id = t.assigned_to
        JOIN users ub ON ub.id = t.assigned_by
        WHERE t.status IN ('pendiente', 'en_progreso');
    """)

    # ── Función 1: Estadísticas de finca ────────────────────
    # Retorna un JSON con estadísticas completas de una finca.
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_farm_statistics(p_farm_id UUID)
        RETURNS JSON
        LANGUAGE plpgsql STABLE
        AS $$
        DECLARE
            result JSON;
        BEGIN
            SELECT json_build_object(
                'farm_id', f.id,
                'farm_name', f.name,
                'total_bovines',    (SELECT COUNT(*) FROM bovine WHERE farm_id = f.id AND is_active),
                'males',            (SELECT COUNT(*) FROM bovine WHERE farm_id = f.id AND is_active AND sex = 'macho'),
                'females',          (SELECT COUNT(*) FROM bovine WHERE farm_id = f.id AND is_active AND sex = 'hembra'),
                'avg_weight',       (SELECT ROUND(AVG(current_weight), 2) FROM bovine WHERE farm_id = f.id AND is_active AND current_weight IS NOT NULL),
                'total_land_plots', (SELECT COUNT(*) FROM land_plot WHERE farm_id = f.id AND is_active),
                'total_paddocks',   (SELECT COUNT(*) FROM paddock WHERE farm_id = f.id AND is_active),
                'pending_tasks',    (SELECT COUNT(*) FROM task WHERE farm_id = f.id AND status IN ('pendiente', 'en_progreso')),
                'low_stock_items',  (SELECT COUNT(*) FROM food WHERE farm_id = f.id AND is_active AND min_stock_alert IS NOT NULL AND current_stock <= min_stock_alert),
                'total_treatments', (SELECT COUNT(*) FROM treatment WHERE farm_id = f.id),
                'milk_today_liters',(SELECT COALESCE(SUM(quantity_liters), 0) FROM milk_production WHERE farm_id = f.id AND DATE(milking_date) = CURRENT_DATE)
            ) INTO result
            FROM farm f
            WHERE f.id = p_farm_id;

            RETURN result;
        END;
        $$;
    """)

    # ── Función 2: Historial de peso de un bovino ───────────
    # Retorna la evolución de peso registrada en auditoría.
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_bovine_weight_history(p_bovine_id UUID)
        RETURNS TABLE(
            recorded_at TIMESTAMPTZ,
            old_weight TEXT,
            new_weight TEXT,
            recorded_by_name TEXT
        )
        LANGUAGE plpgsql STABLE
        AS $$
        BEGIN
            RETURN QUERY
            SELECT
                ba.performed_at,
                ba.old_value,
                ba.new_value,
                u.first_name || ' ' || u.last_name
            FROM bovine_audit ba
            JOIN users u ON u.id = ba.performed_by
            WHERE ba.bovine_id = p_bovine_id
              AND ba.field_changed = 'current_weight'
            ORDER BY ba.performed_at;
        END;
        $$;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS fn_bovine_weight_history(UUID);")
    op.execute("DROP FUNCTION IF EXISTS fn_farm_statistics(UUID);")
    op.execute("DROP VIEW IF EXISTS v_pending_tasks;")
    op.execute("DROP VIEW IF EXISTS v_low_stock_alerts;")
    op.execute("DROP VIEW IF EXISTS v_milk_production_daily;")
    op.execute("DROP VIEW IF EXISTS v_bovine_census;")
    op.execute("DROP VIEW IF EXISTS v_farm_summary;")
