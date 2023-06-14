"""add video permission and edit text comment limit

Revision ID: 6f0c596cacad
Revises: fb9efeef07cc
Create Date: 2023-06-14 12:39:15.147297

"""
from alembic import op
import sqlalchemy as sa

from src.video.models import Permission

# revision identifiers, used by Alembic.
revision = '6f0c596cacad'
down_revision = 'fb9efeef07cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    permission = sa.Enum(Permission, name="permission")
    permission.create(op.get_bind(), checkfirst=True)
    op.add_column('video', sa.Column('permission',
                                     sa.Enum('for_everyone', 'for_authorized', 'for_subscribers', 'for_myself',
                                             name='permission'), nullable=False))
    op.alter_column('comment', 'text',
                    existing_type=sa.VARCHAR(length=512),
                    type_=sa.String(length=5000),
                    existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('video', 'permission')
    status = sa.Enum(Permission, name="permission")
    status.drop(op.get_bind())
    op.alter_column('comment', 'text',
                    existing_type=sa.String(length=5000),
                    type_=sa.VARCHAR(length=512),
                    existing_nullable=False)
    # ### end Alembic commands ###