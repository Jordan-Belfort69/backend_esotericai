# app/db/models.py

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .postgres import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    referrer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=True
    )
    ref_code: Mapped[Optional[str]] = mapped_column(String, unique=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    messages_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    histories: Mapped[list["History"]] = relationship(back_populates="user")
    xp: Mapped[Optional["UserXP"]] = relationship(back_populates="user", uselist=False)
    tasks: Mapped[list["UserTask"]] = relationship(back_populates="user")
    daily_tip_settings: Mapped[Optional["DailyTipSettings"]] = relationship(
        back_populates="user", uselist=False
    )
    referrals_made: Mapped[list["Referral"]] = relationship(
        back_populates="referrer",
        foreign_keys="Referral.referrer_id",
    )
    referrals_received: Mapped[list["Referral"]] = relationship(
        back_populates="friend",
        foreign_keys="Referral.friend_user_id",
    )
    sms_purchases: Mapped[list["SmsPurchase"]] = relationship(back_populates="user")


class DailyTipSettings(Base):
    __tablename__ = "daily_tip_settings"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_from: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    time_to: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="daily_tip_settings")


class AdviceSentLog(Base):
    __tablename__ = "advice_sent_log"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    sent_date: Mapped[str] = mapped_column(String, primary_key=True)


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[Optional[str]] = mapped_column(Text)
    answer_full: Mapped[Optional[str]] = mapped_column(Text)
    answer_short: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="histories")


class Level(Base):
    __tablename__ = "levels"

    level: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    min_xp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_xp: Mapped[Optional[int]] = mapped_column(Integer)
    icon: Mapped[Optional[str]] = mapped_column(String)
    color_from: Mapped[Optional[str]] = mapped_column(String)
    color_to: Mapped[Optional[str]] = mapped_column(String)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime(2099, 12, 31, 23, 59, 59)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class ReferralLink(Base):
    __tablename__ = "referral_links"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    referral_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    friend_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    friend_display_name: Mapped[Optional[str]] = mapped_column(String)
    joined_at: Mapped[str] = mapped_column(String, nullable=False)
    bonus_credits: Mapped[int] = mapped_column(Integer, default=0)
    bonus_referrer_given: Mapped[bool] = mapped_column(Boolean, default=False)
    bonus_friend_given: Mapped[bool] = mapped_column(Boolean, default=False)

    referrer: Mapped["User"] = relationship(
        back_populates="referrals_made", foreign_keys=[referrer_id]
    )
    friend: Mapped["User"] = relationship(
        back_populates="referrals_received", foreign_keys=[friend_user_id]
    )


class SmsPurchase(Base):
    __tablename__ = "sms_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    messages_count: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price_rub: Mapped[float] = mapped_column(Float, nullable=False)
    final_price_rub: Mapped[float] = mapped_column(Float, nullable=False)
    promocode: Mapped[Optional[str]] = mapped_column(String)
    discount_percent: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    paid_at: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="sms_purchases")


class UserPromocode(Base):
    __tablename__ = "user_promocodes"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    code: Mapped[str] = mapped_column(
        String, ForeignKey("promo_codes.code"), primary_key=True
    )
    assigned_at: Mapped[str] = mapped_column(String, nullable=False)
    used_at: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[Optional[str]] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("user_id", "code", name="uq_user_promocode"),
    )


class UserTask(Base):
    __tablename__ = "user_tasks"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    task_code: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    progress_current: Mapped[int] = mapped_column(Integer, default=0)
    progress_target: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="tasks")


class UserXP(Base):
    __tablename__ = "user_xp"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), primary_key=True
    )
    xp: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="xp")
