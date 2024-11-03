"""create initial cards

Revision ID: c982c5fc6739
Revises: 
Create Date: 2024-10-29 19:56:20.291857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c982c5fc6739'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('rarity', sa.String(), nullable=True),
    sa.Column('current_price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cards_id'), 'cards', ['id'], unique=False)
    op.create_index(op.f('ix_cards_name'), 'cards', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_cards_name'), table_name='cards')
    op.drop_index(op.f('ix_cards_id'), table_name='cards')
    op.drop_table('cards')
    # ### end Alembic commands ###