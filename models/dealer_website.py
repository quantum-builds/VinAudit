from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship
from .base import db

class DealerWebsite(db.Model):
    """Model representing a dealer's website."""
    
    __tablename__ = 'dealer_websites'
    
    dealer_id = db.Column(db.Integer, ForeignKey('dealers.dealer_id', ondelete='CASCADE'), primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    
    # Relationships
    dealer = relationship('Dealer', back_populates='website')
    
    def __repr__(self) -> str:
        return f"<DealerWebsite {self.url}>" 