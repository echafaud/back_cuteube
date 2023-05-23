"""add comment model

Revision ID: 9ea1e3a04b05
Revises: 7f3078b485da
Create Date: 2023-05-23 19:19:16.066838

"""
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ea1e3a04b05'
down_revision = '7f3078b485da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('author_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('video_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('posted_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('edited_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    # ### end Alembic commands ###
