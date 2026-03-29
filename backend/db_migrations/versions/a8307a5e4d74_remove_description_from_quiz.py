"""remove description from quiz

Revision ID: a8307a5e4d74
Revises: 6bd343bb4acf
Create Date: 2026-03-26 10:35:09.145592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a8307a5e4d74'
down_revision: Union[str, Sequence[str], None] = '6bd343bb4acf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('quiz', 'description')

def downgrade() -> None:
    op.add_column('quiz', sa.Column('description', sa.String(), nullable=True))