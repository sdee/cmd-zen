"""
Revision ID: 0002_create_guesses
Revises: 0001_create_questions
Create Date: 2025-08-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_create_guesses'
down_revision = '0001_create_questions'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'guesses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('question_id', sa.Integer, nullable=False),
        sa.Column('answer', sa.String, nullable=False),
        sa.Column('is_correct', sa.Boolean, nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

def downgrade():
    op.drop_table('guesses')
