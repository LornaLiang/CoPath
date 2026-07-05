from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    setting_key: Mapped[str] = mapped_column(Text, primary_key=True)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
