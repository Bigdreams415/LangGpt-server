import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime,
    Enum as SAEnum, Text, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database.database import Base


class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"


class LanguageChoice(str, enum.Enum):
    IGBO = "Igbo"
    YORUBA = "Yoruba"
    HAUSA = "Hausa"


class LevelChoice(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class User(Base):
    __tablename__ = "users"

    # Identity
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Null for Google-only accounts

    # Profile
    date_of_birth = Column(String(20), nullable=True)   # Stored as string DD/MM/YYYY
    country = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)

    # Learning preferences
    selected_language = Column(
        SAEnum(LanguageChoice),
        nullable=True,
    )
    level = Column(
        SAEnum(LevelChoice),
        default=LevelChoice.BEGINNER,
        nullable=True,
    )

    # Auth fields
    auth_provider = Column(
        SAEnum(AuthProvider),
        default=AuthProvider.EMAIL,
        nullable=False,
    )
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Gamification
    streak_count = Column(Integer, default=0, nullable=False)
    total_xp = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    progress_records = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"


class UserProgress(Base):
    """Tracks per-user progress on each topic."""
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    language = Column(SAEnum(LanguageChoice), nullable=False)
    topic = Column(String(100), nullable=False)
    level = Column(SAEnum(LevelChoice), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<UserProgress user={self.user_id} topic={self.topic}>"