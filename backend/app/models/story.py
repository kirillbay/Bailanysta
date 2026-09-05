"""Story model — 24h ephemeral."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid

from app.database.base import Base

class Story(Base):
    __tablename__ = "stories"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    media_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # image | video
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    author: Mapped["User"] = relationship(lazy="joined")

    __table_args__ = (
        Index("ix_stories_author_expires", "author_id", "expires_at"),
    )

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        # ensure tz-aware
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return exp <= now
