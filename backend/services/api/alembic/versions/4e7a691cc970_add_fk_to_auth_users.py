"""add_fk_to_auth_users

Revision ID: 4e7a691cc970
Revises: be50339179e3
Create Date: 2026-08-30 10:08:32.417036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '4e7a691cc970'
down_revision: Union[str, Sequence[str], None] = 'be50339179e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = Inspector.from_engine(conn)
    
    # Check if 'auth' schema and 'users' table exist (Supabase environment)
    if 'auth' in insp.get_schema_names():
        if 'users' in insp.get_table_names(schema='auth'):
            # Check if FK already exists to prevent duplicate error
            fks = insp.get_foreign_keys('users')
            fk_exists = any(fk.get('referred_schema') == 'auth' and fk.get('referred_table') == 'users' for fk in fks)
            
            if not fk_exists:
                op.create_foreign_key(
                    "fk_public_users_auth_users",
                    "users",
                    "users",
                    ["id"],
                    ["id"],
                    source_schema="public",
                    referent_schema="auth",
                    ondelete="CASCADE"
                )

def downgrade() -> None:
    conn = op.get_bind()
    insp = Inspector.from_engine(conn)
    if 'auth' in insp.get_schema_names():
        if 'users' in insp.get_table_names(schema='auth'):
            op.drop_constraint("fk_public_users_auth_users", "users", type_="foreignkey")

