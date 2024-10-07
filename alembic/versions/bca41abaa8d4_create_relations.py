"""create relations

Revision ID: bca41abaa8d4
Revises: d4e420428492
Create Date: 2024-08-28 11:41:11.000395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bca41abaa8d4'
down_revision: Union[str, None] = 'd4e420428492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('centros_costo', sa.Column('id_gerencia', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'centros_costo', 'gerencias', ['id_gerencia'], ['id'], ondelete='SET NULL')
    op.add_column('usuarios', sa.Column('gerencia_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'usuarios', 'gerencias', ['gerencia_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'usuarios', type_='foreignkey')
    op.drop_column('usuarios', 'gerencia_id')
    op.drop_constraint(None, 'centros_costo', type_='foreignkey')
    op.drop_column('centros_costo', 'id_gerencia')
    # ### end Alembic commands ###