from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    links = relationship("Link", back_populates="owner")

    __table_args__ = (
        Index('ix_users_email', 'email', unique=True),
    )

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    custom_alias = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner = relationship("User", back_populates="links")

    __table_args__ = (
        Index('ix_links_short_code', 'short_code', unique=True),
        Index('ix_links_custom_alias', 'custom_alias', unique=True),
        Index('ix_links_original_url', 'original_url'),
    )