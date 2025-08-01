"""
Revision ID: 0001_create_questions
Revises: 
Create Date: 2025-08-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_questions'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    questions = op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('command', sa.String(255), nullable=False),
        sa.Column('shortcut', sa.String(32), nullable=False),
    )
    op.bulk_insert(
        questions,
        [
            {"command": "move cursor left", "shortcut": "h"},
            {"command": "move cursor right", "shortcut": "l"},
            {"command": "move cursor up", "shortcut": "k"},
            {"command": "move cursor down", "shortcut": "j"},
            {"command": "delete character", "shortcut": "x"},
            {"command": "insert mode", "shortcut": "i"},
            {"command": "append after cursor", "shortcut": "a"},
            {"command": "save file", "shortcut": ":w"},
            {"command": "quit", "shortcut": ":q"},
            {"command": "undo", "shortcut": "u"},
        ]
    )

def downgrade():
    op.drop_table('questions')
