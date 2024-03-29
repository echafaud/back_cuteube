"""add user_view model

Revision ID: 4c872bb3171d
Revises: e58e12f540d7
Create Date: 2023-05-24 00:58:28.886778

"""
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c872bb3171d'
down_revision = 'e58e12f540d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_view',
    sa.Column('author_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('video_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('view_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.ForeignKeyConstraint(['view_id'], ['view.id'], ),
    sa.PrimaryKeyConstraint('author_id', 'video_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_view')
    # ### end Alembic commands ###
