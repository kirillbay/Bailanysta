"""ClubMessage model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Boolean, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.database.base import Base

class ClubMessage(Base):
    __tablename__ = "club_messages"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("club_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    author: Mapped["User"] = relationship(lazy="joined")

    __table_args__ = (
        Index("ix_messages_channel_created", "channel_id", "created_at"),
    )
