from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MerchantModel(Base):
    __tablename__ = "merchant"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class AppUserModel(Base):
    __tablename__ = "app_user"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)


class ProductModel(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)


class SkuModel(Base):
    __tablename__ = "sku"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)


class ProductFaqModel(Base):
    __tablename__ = "product_faq"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)


class LiveSessionModel(Base):
    __tablename__ = "live_session"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)


class VoiceProfileModel(Base):
    __tablename__ = "voice_profile"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    voice_id: Mapped[str] = mapped_column(String(200), nullable=False)


class VoiceLicenseModel(Base):
    __tablename__ = "voice_license"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    voice_profile_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    authorized_by: Mapped[str] = mapped_column(String(200), nullable=False)
    authorization_record_url: Mapped[str] = mapped_column(Text, nullable=False)


class PlatformProductMappingModel(Base):
    __tablename__ = "platform_product_mapping"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    platform: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    platform_product_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
