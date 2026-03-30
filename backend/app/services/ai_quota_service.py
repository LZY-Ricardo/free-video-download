"""
免费 AI 次数服务
"""
from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import DailyAIUsage


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


class AIQuotaService:
    DAILY_LIMIT = 2

    @staticmethod
    def current_usage_date(now: datetime | None = None) -> str:
        if now is None:
            aware_now = datetime.now(UTC)
        elif now.tzinfo is None:
            aware_now = now.replace(tzinfo=UTC)
        else:
            aware_now = now.astimezone(UTC)
        return aware_now.astimezone(SHANGHAI_TZ).date().isoformat()

    def get_daily_usage(self, db: Session, user_id: str, usage_date: str | None = None) -> DailyAIUsage | None:
        target_date = usage_date or self.current_usage_date()
        return db.scalar(
            select(DailyAIUsage).where(
                DailyAIUsage.user_id == user_id,
                DailyAIUsage.usage_date == target_date,
            )
        )

    def consume_free_analysis_use(self, db: Session, user_id: str) -> DailyAIUsage:
        usage_date = self.current_usage_date()
        usage = self.get_daily_usage(db, user_id, usage_date)
        if usage is None:
            usage = DailyAIUsage(user_id=user_id, usage_date=usage_date, used_count=0)
            db.add(usage)
            db.flush()

        if usage.used_count >= self.DAILY_LIMIT:
            raise PermissionError("今日免费 AI 次数已用完，请开通 VIP")

        usage.used_count += 1
        db.commit()
        db.refresh(usage)
        return usage


ai_quota_service = AIQuotaService()
