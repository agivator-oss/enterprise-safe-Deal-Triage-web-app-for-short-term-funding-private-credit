"""initial schema

Revision ID: 0001_init
Revises: 
Create Date: 2025-12-15

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "deals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("deal_id", sa.String(length=36), sa.ForeignKey("deals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_deal_id", "documents", ["deal_id"])
    op.create_index("ix_documents_sha256", "documents", ["sha256"])

    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", "version", name="uq_prompt_versions_name_version"),
    )
    op.create_index("ix_prompt_versions_name", "prompt_versions", ["name"])
    op.create_index("ix_prompt_versions_content_hash", "prompt_versions", ["content_hash"])

    op.create_table(
        "llm_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("deal_id", sa.String(length=36), sa.ForeignKey("deals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prompt_name", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_llm_runs_deal_id", "llm_runs", ["deal_id"])
    op.create_index("ix_llm_runs_input_hash", "llm_runs", ["input_hash"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor", sa.String(length=256), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("deal_id", sa.String(length=36), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_actor", "audit_logs", ["actor"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_deal_id", "audit_logs", ["deal_id"])

    op.create_table(
        "deal_terms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("deal_id", sa.String(length=36), sa.ForeignKey("deals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("terms_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("citations_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confirmed_fields_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("deal_id", name="uq_deal_terms_deal_id"),
    )
    op.create_index("ix_deal_terms_deal_id", "deal_terms", ["deal_id"])

    op.create_table(
        "deal_analysis",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("deal_id", sa.String(length=36), sa.ForeignKey("deals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("risk_flags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("diligence_questions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("overall_triage", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("deal_id", name="uq_deal_analysis_deal_id"),
    )
    op.create_index("ix_deal_analysis_deal_id", "deal_analysis", ["deal_id"])

    op.create_table(
        "deal_drafts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("deal_id", sa.String(length=36), sa.ForeignKey("deals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("draft_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("prompt_name", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("deal_id", name="uq_deal_drafts_deal_id"),
    )
    op.create_index("ix_deal_drafts_deal_id", "deal_drafts", ["deal_id"])


def downgrade() -> None:
    op.drop_index("ix_deal_drafts_deal_id", table_name="deal_drafts")
    op.drop_table("deal_drafts")

    op.drop_index("ix_deal_analysis_deal_id", table_name="deal_analysis")
    op.drop_table("deal_analysis")

    op.drop_index("ix_deal_terms_deal_id", table_name="deal_terms")
    op.drop_table("deal_terms")

    op.drop_index("ix_audit_logs_deal_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_llm_runs_input_hash", table_name="llm_runs")
    op.drop_index("ix_llm_runs_deal_id", table_name="llm_runs")
    op.drop_table("llm_runs")

    op.drop_index("ix_prompt_versions_content_hash", table_name="prompt_versions")
    op.drop_index("ix_prompt_versions_name", table_name="prompt_versions")
    op.drop_table("prompt_versions")

    op.drop_index("ix_documents_sha256", table_name="documents")
    op.drop_index("ix_documents_deal_id", table_name="documents")
    op.drop_table("documents")

    op.drop_table("deals")
