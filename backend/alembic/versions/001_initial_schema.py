"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


api_status_enum = sa.Enum("ACTIVE", "DEPRECATED", "ZOMBIE", "SHADOW", name="api_status_enum")
traffic_source_type_enum = sa.Enum(
    "gateway", "vpc_flow", "load_balancer", "openapi_spec", name="traffic_source_type_enum"
)
severity_level_enum = sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="severity_level_enum")
alert_type_enum = sa.Enum(
    "ZOMBIE_RESURRECTION", "SHADOW_DISCOVERED", "SECURITY_VIOLATION", name="alert_type_enum"
)


def upgrade() -> None:
    bind = op.get_bind()

    api_status_enum.create(bind, checkfirst=True)
    traffic_source_type_enum.create(bind, checkfirst=True)
    severity_level_enum.create(bind, checkfirst=True)
    alert_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "apis",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column("current_status", api_status_enum, nullable=False),
        sa.Column("previous_status", sa.String(length=20), nullable=True),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("zombie_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_traffic_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dormant_duration_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("has_documentation", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("owner", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_apis_endpoint", "apis", ["endpoint"], unique=False)
    op.create_index("ix_apis_current_status", "apis", ["current_status"], unique=False)
    op.create_index("ix_apis_last_traffic_seen", "apis", ["last_traffic_seen"], unique=False)

    op.create_table(
        "api_security_posture",
        sa.Column("api_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owasp_category", sa.String(length=100), nullable=False),
        sa.Column("cvss_score", sa.Float(), nullable=False),
        sa.Column("severity", severity_level_enum, nullable=False),
        sa.Column("has_authentication", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("uses_https", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("tls_version", sa.String(length=10), nullable=True),
        sa.Column("has_rate_limiting", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("exposes_sensitive_data", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("security_risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_assessed", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["api_id"], ["apis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("api_id"),
    )
    op.create_index("ix_api_security_posture_api_id", "api_security_posture", ["api_id"], unique=False)

    op.create_table(
        "traffic_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", traffic_source_type_enum, nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["api_id"], ["apis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_traffic_sources_api_id", "traffic_sources", ["api_id"], unique=False)

    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_service", sa.String(length=100), nullable=False),
        sa.Column("source_ip", sa.String(length=50), nullable=True),
        sa.Column("target_api_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("call_frequency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("traffic_percentage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_observed", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["target_api_id"], ["apis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dependencies_target_api_id", "dependencies", ["target_api_id"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alert_type", alert_type_enum, nullable=False),
        sa.Column("trigger_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("previous_dormant_days", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["api_id"], ["apis.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_api_id", "alerts", ["api_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_api_id", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_dependencies_target_api_id", table_name="dependencies")
    op.drop_table("dependencies")

    op.drop_index("ix_traffic_sources_api_id", table_name="traffic_sources")
    op.drop_table("traffic_sources")

    op.drop_index("ix_api_security_posture_api_id", table_name="api_security_posture")
    op.drop_table("api_security_posture")

    op.drop_index("ix_apis_last_traffic_seen", table_name="apis")
    op.drop_index("ix_apis_current_status", table_name="apis")
    op.drop_index("ix_apis_endpoint", table_name="apis")
    op.drop_table("apis")

    bind = op.get_bind()
    alert_type_enum.drop(bind, checkfirst=True)
    severity_level_enum.drop(bind, checkfirst=True)
    traffic_source_type_enum.drop(bind, checkfirst=True)
    api_status_enum.drop(bind, checkfirst=True)
