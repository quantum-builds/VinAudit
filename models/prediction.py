from datetime import datetime
from sqlalchemy import ForeignKey, Index, String, Float
from sqlalchemy.orm import relationship
from .base import db

class Prediction(db.Model):
    """Model representing a cached price prediction."""
    
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.SmallInteger, nullable=False)
    model_id = db.Column(db.SmallInteger, ForeignKey('vehicles.model_id', ondelete='CASCADE'), nullable=False)
    mileage = db.Column(db.Integer, nullable=True)
    predicted_price = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    sample_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship('Vehicle', back_populates='predictions')
    
    __table_args__ = (
        Index('idx_year_model_mileage', 'year', 'model_id', 'mileage'),
    )
    
    def __repr__(self) -> str:
        return f"<Prediction {self.year} {self.vehicle.make} {self.vehicle.model} (${self.predicted_price:,.2f})>" 