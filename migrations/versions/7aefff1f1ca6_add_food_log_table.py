import sqlmodel
"""Add Food log table

Revision ID: 7aefff1f1ca6
Revises: f92dae150f32
Create Date: 2025-04-18 21:45:57.295328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aefff1f1ca6'
down_revision: Union[str, None] = 'f92dae150f32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('foodlog',
    sa.Column('log_date', sa.Date(), nullable=False),
    sa.Column('food', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('meal_type', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
    sa.Column('calories', sa.Float(), nullable=False),
    sa.Column('carbs', sa.Float(), nullable=False),
    sa.Column('protein', sa.Float(), nullable=False),
    sa.Column('fat', sa.Float(), nullable=False),
    sa.Column('sugar', sa.Float(), nullable=True),
    sa.Column('sodium', sa.Float(), nullable=True),
    sa.Column('potassium', sa.Float(), nullable=True),
    sa.Column('fiber', sa.Float(), nullable=True),
    sa.Column('iron', sa.Float(), nullable=True),
    sa.Column('calcium', sa.Float(), nullable=True),
    sa.Column('cholesterol', sa.Float(), nullable=True),
    sa.Column('vitamin_a', sa.Float(), nullable=True),
    sa.Column('vitamin_c', sa.Float(), nullable=True),
    sa.Column('saturated_fat', sa.Float(), nullable=True),
    sa.Column('trans_fat', sa.Float(), nullable=True),
    sa.Column('polyunsaturated_fat', sa.Float(), nullable=True),
    sa.Column('monounsaturated_fat', sa.Float(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_foodlog_log_date'), 'foodlog', ['log_date'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_foodlog_log_date'), table_name='foodlog')
    op.drop_table('foodlog')
    # ### end Alembic commands ###
