"""create shared tables

Revision ID: 0cc450c381ec
Revises: 
Create Date: 2026-03-24 17:36:40.245415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cc450c381ec'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # 1. Create roles table FIRST (no dependencies)
    op.create_table('roles',
        sa.Column('role_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('role_name')
    )

    # 2. Create organization table (owner_id nullable for now)
    op.create_table('organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('des', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create users table (depends on roles, organization)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=True),
        sa.Column('role_name', sa.String(), nullable=False),
        sa.Column('stripe_payment_method_id', sa.String(), nullable=True),
        sa.Column('pricing_plan', sa.String(), nullable=False, default='basic'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('first_login_done', sa.Boolean(), nullable=False, default=False),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        # FK to roles (roles exists now)
        sa.ForeignKeyConstraint(['role_name'], ['roles.role_name']),
        # FK to organization (organization exists now)
        sa.ForeignKeyConstraint(['org_id'], ['organization.id'])
    )

    # 4. Now add owner_id FK to organization (users table now exists)
    op.create_foreign_key(
        'fk_organization_owner_id',
        'organization',
        'users',
        ['owner_id'],
        ['id']
    )


def downgrade():
    # Reverse order
    op.drop_constraint('fk_organization_owner_id', 'organization', type_='foreignkey')
    op.drop_table('users')
    op.drop_table('organization')
    op.drop_table('roles')
