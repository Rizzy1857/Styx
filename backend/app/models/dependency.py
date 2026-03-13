import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_service: Mapped[str] = mapped_column(String(100), nullable=False)
    source_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_api_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("apis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    call_frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    traffic_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_observed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    target_api = relationship("API", back_populates="dependencies")
