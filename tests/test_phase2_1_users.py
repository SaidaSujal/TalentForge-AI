import pytest
import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models import Company, User
from app.core.security import hash_password, verify_password



@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session():
    """Provides a database session that rolls back changes after each test."""
    async with AsyncSessionLocal() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


@pytest.mark.anyio
class TestUserModel:
    """Verify constraints and behaviors of the User model."""

    async def test_create_user_success(self, db_session: AsyncSession):
        """Verify that a User can be created successfully with correct fields."""
        # 1. Create a tenant company
        company = Company(name="Test Tenant", slug=f"test-tenant-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        # 2. Hash password and create user
        raw_password = "securepassword123"
        pwd_hash = hash_password(raw_password)
        
        user = User(
            email=f"test-{uuid.uuid4().hex[:6]}@talentforge.ai",
            password_hash=pwd_hash,
            role="recruiter",
            company_id=company.id,
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        # 3. Retrieve and assert fields
        query = select(User).where(User.id == user.id)
        result = await db_session.execute(query)
        db_user = result.scalar_one_or_none()

        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.email == user.email
        assert db_user.role == "recruiter"
        assert db_user.company_id == company.id
        assert db_user.is_active is True
        assert db_user.created_at is not None
        assert db_user.updated_at is not None
        assert db_user.password_hash == pwd_hash
        assert db_user.password_hash != raw_password

    async def test_user_company_relationship(self, db_session: AsyncSession):
        """Verify that the relationship between User and Company works bidirectionally."""
        company = Company(name="Relationship Co", slug=f"rel-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        user = User(
            email=f"user-{uuid.uuid4().hex[:6]}@relationship.com",
            password_hash=hash_password("pass"),
            role="employee",
            company_id=company.id,
        )
        db_session.add(user)
        await db_session.flush()

        # Refresh objects with relationships loaded eagerly to prevent async lazy-load errors
        await db_session.refresh(company, ["users"])
        await db_session.refresh(user, ["company"])

        assert user.company == company
        assert user in company.users

    async def test_user_email_uniqueness(self, db_session: AsyncSession):
        """Verify that duplicate emails are rejected by unique constraint."""
        company = Company(name="Unique Co", slug=f"uniq-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        shared_email = f"duplicate-{uuid.uuid4().hex[:6]}@talentforge.ai"
        
        user1 = User(
            email=shared_email,
            password_hash=hash_password("pass"),
            role="employee",
            company_id=company.id,
        )
        db_session.add(user1)
        await db_session.flush()

        user2 = User(
            email=shared_email,
            password_hash=hash_password("pass2"),
            role="employee",
            company_id=company.id,
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_user_company_fk_requirement(self, db_session: AsyncSession):
        """Verify that creating a user without a valid company_id fails."""
        non_existent_company_id = uuid.uuid4()
        
        user = User(
            email=f"invalid-{uuid.uuid4().hex[:6]}@talentforge.ai",
            password_hash=hash_password("pass"),
            role="employee",
            company_id=non_existent_company_id,
        )
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_user_password_hashing(self, db_session: AsyncSession):
        """Verify password hashing, verification, and non-plain text storage."""
        raw_password = "mypassword123"
        hashed = hash_password(raw_password)

        assert hashed != raw_password
        assert verify_password(raw_password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
