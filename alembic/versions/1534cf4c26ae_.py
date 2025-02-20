"""Create basic routes table

Revision ID: 1534cf4c26ae
Revises:
Create Date: 2025-02-20 07:50:31.296000

"""
from typing import Union, Sequence

import sqlalchemy as sa
from geoalchemy2 import Geometry
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1534cf4c26ae'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create routes table
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('geo', Geometry('MULTILINESTRINGZM', srid=4326))
    )

    # Create spatial index
    op.execute('CREATE INDEX routes_geo_idx ON routes USING GIST (geo)')


def downgrade() -> None:
    # Drop the table and index
    op.drop_index('routes_geo_idx', table_name='routes')
    op.drop_table('routes')
