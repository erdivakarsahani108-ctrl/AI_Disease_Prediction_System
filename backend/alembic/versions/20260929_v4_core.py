"""V4 core schema bootstrap: auth, organizations, transfer, medicine, scans."""
from alembic import op
from app.db.database import Base
from app.db import models  # noqa: F401

revision = "20260929_v4_core"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
