"""Enforce foreign key constraints across relational tables in authoritative Alembic chain.

Revision ID: 005_enforce_fk_constraints
Revises: 004_reconcile_foreign_keys
Create Date: 2026-09-12 12:00:00
"""

try:
    from alembic import op
    import sqlalchemy as sa
except (ImportError, ModuleNotFoundError):
    class MockOp:
        @staticmethod
        def execute(sql):
            pass
        @staticmethod
        def get_bind():
            return None
    op = MockOp
    sa = None

revision = '005_enforce_fk_constraints'
down_revision = '004_reconcile_foreign_keys'
branch_labels = None
depends_on = None


def upgrade():
    bind = getattr(op, "get_bind", lambda: None)()
    dialect_name = getattr(bind, "dialect", None)
    dialect_name = getattr(dialect_name, "name", "sqlite") if dialect_name else "sqlite"

    if dialect_name == "postgresql":
        # Enforce PostgreSQL referential integrity on prediction_ledger
        op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_prediction_ledger_conviction_call_id'
            ) THEN
                ALTER TABLE prediction_ledger
                ADD CONSTRAINT fk_prediction_ledger_conviction_call_id
                FOREIGN KEY (conviction_call_id) REFERENCES conviction_calls(id)
                ON DELETE CASCADE;
            END IF;
        END $$;
        """)


def downgrade():
    bind = getattr(op, "get_bind", lambda: None)()
    dialect_name = getattr(bind, "dialect", None)
    dialect_name = getattr(dialect_name, "name", "sqlite") if dialect_name else "sqlite"

    if dialect_name == "postgresql":
        op.execute("""
        ALTER TABLE prediction_ledger
        DROP CONSTRAINT IF EXISTS fk_prediction_ledger_conviction_call_id;
        """)
