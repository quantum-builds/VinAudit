from datetime import date
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import relationship
from .base import db

class Listing(db.Model):
    """Model representing a vehicle listing."""
    
    __tablename__ = 'listings'
    
    vin = db.Column(db.String(17), primary_key=True)
    year = db.Column(db.SmallInteger, nullable=False)
    model_id = db.Column(db.SmallInteger, ForeignKey('vehicles.model_id', ondelete='CASCADE'), nullable=False)
    trim = db.Column(db.String(255))
    dealer_id = db.Column(db.Integer, ForeignKey('dealers.dealer_id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    mileage = db.Column(db.Integer)
    used = db.Column(db.Boolean, nullable=False, default=True)
    certified = db.Column(db.Boolean, nullable=False, default=False)
    style = db.Column(db.String(255))
    driven_wheels = db.Column(db.String(255))
    engine = db.Column(db.String(255))
    fuel_type = db.Column(db.String(255))
    exterior_color = db.Column(db.String(255))
    interior_color = db.Column(db.String(255))
    first_seen = db.Column(db.Date, nullable=False)
    last_seen = db.Column(db.Date, nullable=False)
    vdp_last_seen = db.Column(db.Date)
    status = db.Column(db.String(20))
    
    # Relationships
    dealer = relationship('Dealer', back_populates='listings')
    vehicle = relationship('Vehicle', back_populates='listings')
    
    __table_args__ = (
        Index('idx_year_model', 'year', 'model_id'),
        Index('idx_mileage', 'mileage'),
    )
    
    def __repr__(self) -> str:
        return f"<Listing {self.year} {self.vehicle.make} {self.vehicle.model} ({self.vin})>" 