"""
Módulo: models/sanitary_plan.py

¿Qué es?
Define el modelo ORM para "planes sanitarios" — protocolos de vacunaciones,
desparasitaciones y suplementaciones programadas para bovinos o lotes.

¿Por qué existe?
El sistema debe poder planificar y rastrear cuándo cada animal o lote
debe recibir un tratamiento (ej: fiebre aftosa cada 6 meses, vitaminas cada mes).

¿Impacto?
- Centraliza la configuración de protocolos sanitarios por finca
- Permite auditoría de cuándo se aplicó cada vacuna/tratamiento
- Facilita alertas automáticas cuando una aplicación está vencida
- Vincula con la tabla 'treatment' para registrar aplicaciones reales

Ejemplo de datos:
┌─ SanitaryPlan ────────────────────────────────────────┐
│ id: uuid                                               │
│ farm_id: finca-123                                     │
│ bovine_id: bovino-456 (o NULL si es para lote)        │
│ land_plot_id: NULL (o lote-789 si es para lote)       │
│ vaccine_name: "Fiebre Aftosa"                          │
│ frequency_days: 180 (cada 6 meses = 180 días)         │
│ last_applied_date: 2026-05-01 (última vez que se dio)  │
│ next_scheduled_date: 2026-11-01 (próxima fecha)        │
│ is_active: true                                        │
│ created_at: 2026-01-15                                 │
└────────────────────────────────────────────────────────┘

Nota: Este es el PLAN (configuración).
      El registro real de quién recibió qué va en 'treatment'.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SanitaryPlan(Base):
    """
    Tabla: sanitary_plan
    
    ¿Qué almacena?
    Planes de vacunación/desparasitación para cada bovino o lote de una finca.
    Define QUÉ se debe aplicar, CUÁNDO y CADA CUÁNTO TIEMPO.
    """

    __tablename__ = "sanitary_plan"

    # ════════════════════════════════════════════════════════════════════════════════
    # 🔑 Clave primaria y referencias
    # ════════════════════════════════════════════════════════════════════════════════

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    """
    ID único del plan sanitario
    Generado automáticamente (UUID)
    """

    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
    )
    """
    ¿A qué finca pertenece este plan?
    Si la finca se elimina, el plan también (CASCADE)
    """

    # ════════════════════════════════════════════════════════════════════════════════
    # 🐄 Objetivo del plan (individual o lote)
    # ════════════════════════════════════════════════════════════════════════════════

    bovine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bovine.id", ondelete="CASCADE"),
        nullable=True,
    )
    """
    ¿A qué bovino aplica este plan?
    Si es NULL, entonces es para un lote completo (ver land_plot_id)
    Si el bovino se elimina, el plan también
    """

    land_plot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("land_plot.id", ondelete="CASCADE"),
        nullable=True,
    )
    """
    ¿A qué lote/potrero aplica este plan?
    Si es NULL, entonces es para un bovino específico (ver bovine_id)
    Si el lote se elimina, el plan también
    
    Nota: UN plan tiene bovine_id O land_plot_id, pero NO ambos a la vez
    """

    # ════════════════════════════════════════════════════════════════════════════════
    # 💊 Información del tratamiento
    # ════════════════════════════════════════════════════════════════════════════════

    vaccine_or_treatment_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    """
    Nombre de la vacuna o tratamiento
    Ejemplos: "Fiebre Aftosa", "Brucelosis", "Vitaminas A,D,E", "Antiparasitario"
    """

    treatment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    """
    Tipo de aplicación
    Ejemplos: "vacuna", "desparasitacion", "suplemento", "vitamina"
    """

    administration_route: Mapped[str] = mapped_column(
        String(30), nullable=False, default="intramuscular"
    )
    """
    ¿Cómo se aplica?
    Ejemplos: "intramuscular", "oral", "tópica", "subcutánea", "intravenosa"
    """

    dose: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """
    ¿Cuánto se aplica?
    Ejemplos: "2 mL", "100 mL", "1 comprimido", "ad libitum"
    """

    # ════════════════════════════════════════════════════════════════════════════════
    # 📅 Fechas y frecuencia
    # ════════════════════════════════════════════════════════════════════════════════

    frequency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    """
    ¿Cada cuántos días se debe aplicar?
    Ejemplos:
    - 180 = cada 6 meses (fiebre aftosa)
    - 90 = cada 3 meses
    - 30 = cada mes (vitaminas)
    - 365 = cada año
    """

    last_applied_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    """
    ¿Cuándo se aplicó por última vez?
    Si es NULL, es porque aún no se ha aplicado
    """

    next_scheduled_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    """
    ¿Cuándo se debe aplicar la próxima vez?
    Se calcula automáticamente:
    next_scheduled_date = last_applied_date + frequency_days
    """

    # ════════════════════════════════════════════════════════════════════════════════
    # 📝 Información adicional
    # ════════════════════════════════════════════════════════════════════════════════

    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    """
    Notas adicionales sobre el plan
    Ejemplos: "Aplicar antes del destete", "Observar reacciones alérgicas"
    """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    """
    ¿El plan está activo?
    false = el plan fue archivado/desactivado (pero los registros siguen en BD)
    """

    # ════════════════════════════════════════════════════════════════════════════════
    # 👤 Auditoría
    # ════════════════════════════════════════════════════════════════════════════════

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    """¿Quién creó este plan?"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    """¿Cuándo se creó?"""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    """¿Cuándo se actualizó por última vez?"""

    # ════════════════════════════════════════════════════════════════════════════════
    # 🔗 Relaciones con otras tablas
    # ════════════════════════════════════════════════════════════════════════════════

    farm: Mapped["Farm"] = relationship()
    """Acceder a la finca: plan.farm.name"""

    bovine: Mapped["Bovine | None"] = relationship()
    """Acceder al bovino (si aplica): plan.bovine.identification_number"""

    land_plot: Mapped["LandPlot | None"] = relationship()
    """Acceder al lote (si aplica): plan.land_plot.name"""

    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    """Acceder al usuario que creó el plan: plan.creator.email"""

    def __repr__(self) -> str:
        target = self.bovine.identification_number if self.bovine else f"Lote {self.land_plot_id}"
        return f"SanitaryPlan(id={self.id}, vaccine={self.vaccine_or_treatment_name}, target={target})"
