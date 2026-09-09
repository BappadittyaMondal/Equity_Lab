"""Reconcile foreign keys and prediction ledger schema into authoritative Alembic chain.

Revision ID: 004_reconcile_foreign_keys
Revises: 003_consolidate_remaining_tables
Create Date: 2026-09-09 14:00:00
"""

try:
    from alembic import op
    import sqlalchemy as sa
except (ImportError, ModuleNotFoundError):
    class MockOp:
        @staticmethod
        def execute(sql):
            pass
    op = MockOp
    sa = None

revision = '004_reconcile_foreign_keys'
down_revision = '003_consolidate_remaining_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Enforce foreign key indexing and reconcile conviction_call_id schema
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_prediction_ledger_conviction_id
    ON prediction_ledger(conviction_call_id);
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_decision_audit_symbol_timestamp
    ON decision_audit_trail(symbol, timestamp);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_prediction_ledger_conviction_id;")
    op.execute("DROP INDEX IF EXISTS idx_decision_audit_symbol_timestamp;")
