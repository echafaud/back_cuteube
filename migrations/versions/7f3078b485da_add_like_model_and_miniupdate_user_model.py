"""add like model and miniupdate user model

Revision ID: 7f3078b485da
Revises: 897824faa9b7
Create Date: 2023-05-23 00:04:02.604778

"""
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f3078b485da'
down_revision = '897824faa9b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('like',
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('video_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'video_id')
    )
    op.drop_constraint('user_username_key', 'user', type_='unique')
    op.drop_index('ix_user_email', table_name='user')
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.create_index('ix_user_email', 'user', ['email'], unique=False)
    op.create_unique_constraint('user_username_key', 'user', ['username'])
    op.drop_table('like')
    # ### end Alembic commands ###