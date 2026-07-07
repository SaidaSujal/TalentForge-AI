"""
TalentForge AI — User Database Model
====================================
Defines the User model for authentication and RBAC.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.employee import Employee


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User/Employee accounts for authentication and RBAC.
    All users belong to a specific company/tenant.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (unique, indexed)",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt-hashed password",
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="employee",
        comment="User role (e.g. admin, hr_manager, recruiter, employee, manager)",
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the company tenant",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Soft-delete / active status flag",
    )

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="users")
    employee: Mapped[Optional[Employee]] = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
