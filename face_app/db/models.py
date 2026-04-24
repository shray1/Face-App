"""SQLAlchemy ORM models for the Face App database."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Image(Base):
    """Represents a single image file discovered during a folder scan."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_taken: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    gps_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    faces: Mapped[list[Face]] = relationship("Face", back_populates="image", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Image id={self.id} path={self.file_path!r}>"


class Person(Base):
    """Represents a unique identity — one cluster of faces belonging to the same person."""

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # The face crop used as the representative "profile photo" for this person.
    profile_face_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("faces.id", use_alter=True, name="fk_person_profile_face"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    faces: Mapped[list[Face]] = relationship(
        "Face",
        back_populates="person",
        foreign_keys="Face.person_id",
    )
    profile_face: Mapped[Face | None] = relationship(
        "Face",
        foreign_keys=[profile_face_id],
        post_update=True,  # avoids circular FK constraint during INSERT
    )

    def __repr__(self) -> str:
        return f"<Person id={self.id} label={self.label!r}>"


class Face(Base):
    """Represents a single detected face within an image."""

    __tablename__ = "faces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    # Bounding box in absolute pixels (top-left origin).
    bbox_x: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_y: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_w: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_h: Mapped[int] = mapped_column(Integer, nullable=False)
    # 128 float32 values packed as raw bytes (512 bytes total).
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    person_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("persons.id"), nullable=True, index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    image: Mapped[Image] = relationship("Image", back_populates="faces")
    person: Mapped[Person | None] = relationship(
        "Person",
        back_populates="faces",
        foreign_keys=[person_id],
    )

    def __repr__(self) -> str:
        return f"<Face id={self.id} image_id={self.image_id} person_id={self.person_id}>"


class DecisionEnum(str, enum.Enum):
    same = "same"
    different = "different"
    skip = "skip"


class UserDecision(Base):
    """Records a human-in-the-loop decision about whether two faces belong to the same person."""

    __tablename__ = "user_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    face_a_id: Mapped[int] = mapped_column(Integer, ForeignKey("faces.id"), nullable=False)
    face_b_id: Mapped[int] = mapped_column(Integer, ForeignKey("faces.id"), nullable=False)
    decision: Mapped[DecisionEnum] = mapped_column(Enum(DecisionEnum), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    face_a: Mapped[Face] = relationship("Face", foreign_keys=[face_a_id])
    face_b: Mapped[Face] = relationship("Face", foreign_keys=[face_b_id])

    def __repr__(self) -> str:
        return f"<UserDecision id={self.id} decision={self.decision}>"
