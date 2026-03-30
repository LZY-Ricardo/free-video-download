"""
会员服务
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import MembershipOrder, UserMembership
from app.models import MembershipStatusResponse
from app.security import utcnow


class MembershipService:
    """会员有效期与状态辅助逻辑。"""

    @staticmethod
    def calculate_membership_window(
        active_expires_at: datetime | None,
        duration_days: int,
        now: datetime | None = None,
    ) -> tuple[datetime, datetime]:
        now = now or utcnow()
        extension_base = (
            active_expires_at
            if active_expires_at is not None and active_expires_at > now
            else now
        )
        expires_at = extension_base + timedelta(days=duration_days)
        return now, expires_at

    @staticmethod
    def get_membership(db: Session, user_id: str) -> UserMembership | None:
        return db.scalar(select(UserMembership).where(UserMembership.user_id == user_id))

    @classmethod
    def has_active_membership(cls, db: Session, user_id: str) -> bool:
        membership = cls.get_membership(db, user_id)
        if not membership:
            return False
        return membership.status == "active" and membership.expires_at > utcnow()

    @classmethod
    def get_membership_status(cls, db: Session, user_id: str) -> MembershipStatusResponse:
        membership = cls.get_membership(db, user_id)
        now = utcnow()
        if not membership or membership.status != "active" or membership.expires_at <= now:
            return MembershipStatusResponse(is_member=False, status="inactive")

        remaining_seconds = max(0, (membership.expires_at - now).total_seconds())
        remaining_days = int(remaining_seconds // 86400)
        if remaining_seconds % 86400:
            remaining_days += 1

        return MembershipStatusResponse(
            is_member=True,
            plan_code=membership.plan_code,
            status=membership.status,
            expires_at=membership.expires_at.isoformat(),
            remaining_days=remaining_days,
        )

    @classmethod
    def activate_membership_from_order(cls, db: Session, order: MembershipOrder) -> UserMembership:
        started_at, expires_at = cls.calculate_membership_window(
            active_expires_at=(
                cls.get_membership(db, order.user_id).expires_at
                if cls.get_membership(db, order.user_id)
                else None
            ),
            duration_days=order.duration_days,
        )

        membership = cls.get_membership(db, order.user_id)
        if membership:
            membership.plan_code = order.plan_code
            membership.started_at = started_at
            membership.expires_at = expires_at
            membership.status = "active"
            membership.source_order_id = order.id
        else:
            membership = UserMembership(
                user_id=order.user_id,
                plan_code=order.plan_code,
                started_at=started_at,
                expires_at=expires_at,
                status="active",
                source_order_id=order.id,
            )
            db.add(membership)
        return membership


membership_service = MembershipService()
