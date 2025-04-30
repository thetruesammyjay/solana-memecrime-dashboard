"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2023-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables
    op.create_table('tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=44), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('symbol', sa.String(length=10), nullable=True),
        sa.Column('decimals', sa.Integer(), server_default='9', nullable=True),
        sa.Column('launch_time', sa.DateTime(), nullable=True),
        sa.Column('deployer', sa.String(length=44), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address')
    )
    
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=44), nullable=False),
        sa.Column('first_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address')
    )
    
    op.create_table('token_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_address', sa.String(length=44), nullable=False),
        sa.Column('liquidity_usd', sa.Float(), nullable=True),
        sa.Column('top_holder_pct', sa.Float(), nullable=True),
        sa.Column('unique_holders', sa.Integer(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['token_address'], ['tokens.address'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('token_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_address', sa.String(length=44), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['token_address'], ['tokens.address'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('wallet_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_address', sa.String(length=44), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['wallet_address'], ['wallets.address'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('alert_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=20), nullable=False),
        sa.Column('triggered_value', sa.Float(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('token_alert_id', sa.Integer(), nullable=True),
        sa.Column('wallet_alert_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['token_alert_id'], ['token_alerts.id'], ),
        sa.ForeignKeyConstraint(['wallet_alert_id'], ['wallet_alerts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('alert_history')
    op.drop_table('wallet_alerts')
    op.drop_table('token_alerts')
    op.drop_table('token_snapshots')
    op.drop_table('wallets')
    op.drop_table('tokens')