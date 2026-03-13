import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AlertType(str, enum.Enum):
    ZOMBIE_RESURRECTION = "ZOMBIE_RESURRECTION"
    SHADOW_DISCOVERED = "SHADOW_DISCOVERED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("apis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType, name="alert_type_enum"), nullable=False)
    trigger_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    previous_dormant_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    api = relationship("API", back_populates="alerts")
