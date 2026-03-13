import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SeverityLevel(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class APISecurityPosture(Base):
    __tablename__ = "api_security_posture"

    api_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("apis.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    owasp_category: Mapped[str] = mapped_column(String(100), nullable=False)
    cvss_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(Enum(SeverityLevel, name="severity_level_enum"), nullable=False)
    has_authentication: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    uses_https: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tls_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    has_rate_limiting: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    exposes_sensitive_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    security_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_assessed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    api = relationship("API", back_populates="security_posture")
