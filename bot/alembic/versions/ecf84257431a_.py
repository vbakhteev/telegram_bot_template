"""empty message

Revision ID: ecf84257431a
Revises: 
Create Date: 2022-06-25 22:25:45.483257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecf84257431a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('fullname', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('registration_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_id'), 'admins', ['id'], unique=False)
    op.create_table('groups',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('group_type', sa.Enum('reading', 'sleeping', name='grouptype'), nullable=True),
    sa.Column('invite', sa.BigInteger(), nullable=True),
    sa.Column('channel_id', sa.BigInteger(), nullable=True),
    sa.Column('deposit', sa.Integer(), nullable=True),
    sa.Column('rest_day_price_to_bank', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('creation_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('channel_id')
    )
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=False)
    op.create_index(op.f('ix_groups_invite'), 'groups', ['invite'], unique=True)
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('fullname', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('registration_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('administration_relation',
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.Column('admin_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'admin_id')
    )
    op.create_index(op.f('ix_administration_relation_admin_id'), 'administration_relation', ['admin_id'], unique=False)
    op.create_index(op.f('ix_administration_relation_group_id'), 'administration_relation', ['group_id'], unique=False)
    op.create_table('kicked_relation',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.Column('kick_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('kick_day', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_table('participation_relation',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.Column('entered_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('participation_details', sa.Text(), nullable=True),
    sa.Column('attempts_bought', sa.Integer(), nullable=True),
    sa.Column('notification_time', sa.Time(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_index(op.f('ix_participation_relation_group_id'), 'participation_relation', ['group_id'], unique=False)
    op.create_index(op.f('ix_participation_relation_user_id'), 'participation_relation', ['user_id'], unique=False)
    op.create_table('reports',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('sender', sa.BigInteger(), nullable=True),
    sa.Column('group', sa.BigInteger(), nullable=True),
    sa.Column('tg_msg_id', sa.Integer(), nullable=True),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('day', sa.Integer(), nullable=True),
    sa.Column('sent_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['group'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_group'), 'reports', ['group'], unique=False)
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_sender'), 'reports', ['sender'], unique=False)
    op.create_index(op.f('ix_reports_sent_datetime'), 'reports', ['sent_datetime'], unique=False)
    op.create_index(op.f('ix_reports_tg_msg_id'), 'reports', ['tg_msg_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_reports_tg_msg_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_sent_datetime'), table_name='reports')
    op.drop_index(op.f('ix_reports_sender'), table_name='reports')
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_group'), table_name='reports')
    op.drop_table('reports')
    op.drop_index(op.f('ix_participation_relation_user_id'), table_name='participation_relation')
    op.drop_index(op.f('ix_participation_relation_group_id'), table_name='participation_relation')
    op.drop_table('participation_relation')
    op.drop_table('kicked_relation')
    op.drop_index(op.f('ix_administration_relation_group_id'), table_name='administration_relation')
    op.drop_index(op.f('ix_administration_relation_admin_id'), table_name='administration_relation')
    op.drop_table('administration_relation')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_groups_name'), table_name='groups')
    op.drop_index(op.f('ix_groups_invite'), table_name='groups')
    op.drop_index(op.f('ix_groups_id'), table_name='groups')
    op.drop_table('groups')
    op.drop_index(op.f('ix_admins_id'), table_name='admins')
    op.drop_table('admins')
    # ### end Alembic commands ###
