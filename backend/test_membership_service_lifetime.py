import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.db_models import User
from app.security import hash_password, utcnow
from app.services.membership_service import membership_service


class MembershipServiceLifetimeTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_activate_lifetime_membership_marks_user_as_active_member(self):
        with self.SessionLocal() as db:
            user = User(
                email="lifetime@test.dev",
                password_hash=hash_password("password123"),
                email_verified_at=utcnow(),
                status="active",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            membership_service.activate_lifetime_membership(db, user.id)
            db.commit()

            status = membership_service.get_membership_status(db, user.id)

            self.assertTrue(status.is_member)
            self.assertEqual(status.plan_code, membership_service.LIFETIME_PLAN_CODE)
            self.assertEqual(status.remaining_days, 0)
            self.assertIsNone(status.expires_at)
            self.assertTrue(membership_service.has_active_membership(db, user.id))


if __name__ == "__main__":
    unittest.main()
