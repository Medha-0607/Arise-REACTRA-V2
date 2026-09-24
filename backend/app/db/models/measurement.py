"""
SQLAlchemy ORM Model for Measurement Results.
Based on PRD Section 34.3.
"""

from sqlalchemy import String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class MeasurementResult(Base):
    __tablename__ = "measurement_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Adaptive Capture Guard Diagnostics Shell
    card_detection_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    calibration_residual: Mapped[float | None] = mapped_column(Float, nullable=True)
    blur_metric: Mapped[float | None] = mapped_column(Float, nullable=True)
    exposure_metric: Mapped[float | None] = mapped_column(Float, nullable=True)
    glare_metric: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # ROI & Color Coordinates
    roi_pixel_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specular_rejected_pixel_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specular_rejected_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    roi_sampling_method: Mapped[str | None] = mapped_column(String(32), default="KMEANS_CENTROID", nullable=True)
    roi_kmeans_k: Mapped[int | None] = mapped_column(Integer, default=3, nullable=True)
    selected_cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selected_cluster_area_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Measured Color Vector (Normalized CIE LAB)
    reaction_lab_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    reaction_lab_a: Mapped[float | None] = mapped_column(Float, nullable=True)
    reaction_lab_b: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Quality & Classification Interpretation
    quality_status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    result: Mapped[str | None] = mapped_column(String(32), nullable=True)  # PRESUMPTIVE_POSITIVE, PRESUMPTIVE_NEGATIVE, INCONCLUSIVE, INVALID_CAPTURE
    class_distance_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    class_distance_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    classifier_invocation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Version Binding
    algorithm_version: Mapped[str] = mapped_column(String(32), default="v1.0.0", nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), default="v1.0.0", nullable=False)

    session: Mapped["TestSession"] = relationship("TestSession", back_populates="measurement")
