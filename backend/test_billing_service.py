import unittest
from datetime import UTC, datetime, timedelta


def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class TestBillingInfrastructure(unittest.TestCase):
    def test_database_bootstrap_creates_sqlite_engine(self):
        from app.database import SessionLocal, engine

        self.assertIsNotNone(engine)
        self.assertIsNotNone(SessionLocal)

    def test_membership_extension_uses_existing_expiry_when_active(self):
        from app.services.membership_service import MembershipService

        current_expiry = utcnow_naive() + timedelta(days=10)
        starts_at, expires_at = MembershipService.calculate_membership_window(
            active_expires_at=current_expiry,
            duration_days=30,
        )

        self.assertGreaterEqual(starts_at, utcnow_naive() - timedelta(seconds=2))
        self.assertGreater(expires_at, current_expiry)
        self.assertAlmostEqual(
            (expires_at - current_expiry).total_seconds(),
            timedelta(days=30).total_seconds(),
            delta=2,
        )

    def test_membership_extension_uses_now_when_membership_expired(self):
        from app.services.membership_service import MembershipService

        previous_expiry = utcnow_naive() - timedelta(days=2)
        starts_at, expires_at = MembershipService.calculate_membership_window(
            active_expires_at=previous_expiry,
            duration_days=30,
        )

        self.assertGreaterEqual(starts_at, utcnow_naive() - timedelta(seconds=2))
        self.assertAlmostEqual(
            (expires_at - starts_at).total_seconds(),
            timedelta(days=30).total_seconds(),
            delta=2,
        )


if __name__ == "__main__":
    unittest.main()
