import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class APIStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ZOMBIE = "ZOMBIE"
    SHADOW = "SHADOW"


class TrafficSourceType(str, enum.Enum):
    GATEWAY = "gateway"
    VPC_FLOW = "vpc_flow"
    LOAD_BALANCER = "load_balancer"
    OPENAPI_SPEC = "openapi_spec"


class API(Base):
    __tablename__ = "apis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    current_status: Mapped[APIStatus] = mapped_column(
        Enum(APIStatus, name="api_status_enum"), nullable=False, default=APIStatus.ACTIVE, index=True
    )
    previous_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    zombie_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_traffic_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    dormant_duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    has_documentation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    security_posture = relationship(
        "APISecurityPosture", back_populates="api", uselist=False, cascade="all, delete-orphan"
    )
    traffic_sources = relationship("TrafficSource", back_populates="api", cascade="all, delete-orphan")
    dependencies = relationship("Dependency", back_populates="target_api", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="api", cascade="all, delete-orphan")


class TrafficSource(Base):
    __tablename__ = "traffic_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("apis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[TrafficSourceType] = mapped_column(
        Enum(TrafficSourceType, name="traffic_source_type_enum"), nullable=False
    )
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    api = relationship("API", back_populates="traffic_sources")
