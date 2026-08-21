from datetime import datetime
from sqlalchemy import DateTime, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    candidate_name: Mapped[str] = mapped_column(String(255), default="Unknown")
    skills: Mapped[str] = mapped_column(Text, default="[]")
    experience: Mapped[str] = mapped_column(Text, default="[]")
    education: Mapped[str] = mapped_column(Text, default="[]")
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
