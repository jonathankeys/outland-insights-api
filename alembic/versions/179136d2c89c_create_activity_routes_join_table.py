"""create activity_routes join table

Revision ID: 179136d2c89c
Revises: 5d8bb199f9c0
Create Date: 2025-02-24 20:59:27.562301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '179136d2c89c'
down_revision: Union[str, None] = '5d8bb199f9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'activity_routes',
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['activity_id'], ['activity_log.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('activity_id', 'route_id')
    )

    # Create indexes for better query performance
    op.create_index('idx_activity_routes_activity_id', 'activity_routes', ['activity_id'])
    op.create_index('idx_activity_routes_route_id', 'activity_routes', ['route_id'])


def downgrade():
    op.drop_index('idx_activity_routes_route_id')
    op.drop_index('idx_activity_routes_activity_id')
    op.drop_table('activity_routes')
