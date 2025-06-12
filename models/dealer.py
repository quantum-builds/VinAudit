from datetime import date
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship
from .base import db

class Dealer(db.Model):
    """Model representing a car dealer."""
    
    __tablename__ = 'dealers'
    
    dealer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255))
    city = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip = db.Column(db.String(10), nullable=False)
    
    # Relationships
    listings = relationship('Listing', back_populates='dealer')
    website = relationship('DealerWebsite', back_populates='dealer', uselist=False)
    
    def __repr__(self) -> str:
        return f"<Dealer {self.name} ({self.city}, {self.state})>" 