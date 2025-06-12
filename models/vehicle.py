from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship
from .base import db

class Vehicle(db.Model):
    """Model representing a vehicle make and model."""
    
    __tablename__ = 'vehicles'
    
    model_id = db.Column(db.SmallInteger, primary_key=True)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    
    # Relationships
    listings = relationship('Listing', back_populates='vehicle')
    predictions = relationship('Prediction', back_populates='vehicle')
    
    __table_args__ = (
        db.UniqueConstraint('make', 'model', name='make_model'),
    )
    
    def __repr__(self) -> str:
        return f"<Vehicle {self.make} {self.model}>" 