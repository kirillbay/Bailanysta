"""Follow model."""
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from app.database.base import Base

class Follow(Base):
    __tablename__ = "follows"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    follower_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
        Index("ix_follows_follower_following", "follower_id", "following_id"),
        Index("ix_follows_following_follower", "following_id", "follower_id"),
    )
