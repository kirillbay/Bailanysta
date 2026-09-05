"""Notification service — centralized creation."""
import uuid
from sqlalchemy.orm import Session
from app.models.notification import Notification

# Allowed types
ALLOWED_TYPES = {"like", "comment", "follow", "mention", "club_message", "club_member", "club_role"}

def create_notification(
    db: Session,
    recipient_id: uuid.UUID,
    actor_id: uuid.UUID | None,
    type: str,
    title: str | None = None,
    message: str | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
) -> Notification | None:
    if type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid notification type: {type}")
    if recipient_id == actor_id:
        return None  # no self-notification
    n = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=type,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(n)
    db.flush()
    return n

def notify_follow(db: Session, followed_user_id, follower_user, follower_username: str):
    return create_notification(db, followed_user_id, follower_user.id, "follow", title="New follower", message=f"@{follower_username} started following you", entity_type="user", entity_id=follower_user.id)

def notify_like(db: Session, post_author_id, actor, post_id):
    return create_notification(db, post_author_id, actor.id, "like", title="New like", message=f"@{actor.username} liked your post", entity_type="post", entity_id=post_id)

def notify_comment(db: Session, post_author_id, actor, post_id):
    return create_notification(db, post_author_id, actor.id, "comment", title="New comment", message=f"@{actor.username} commented on your post", entity_type="post", entity_id=post_id)
