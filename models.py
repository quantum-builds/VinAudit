from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Dealer(db.Model):
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

class VehicleModel(db.Model):
    __tablename__ = 'vehicle_models'
    
    model_id = db.Column(db.SmallInteger, primary_key=True)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    
    # Relationships
    listings = relationship('Listing', back_populates='vehicle_model')
    
    __table_args__ = (
        db.UniqueConstraint('make', 'model', name='make_model'),
    )

class Listing(db.Model):
    __tablename__ = 'listings'
    
    vin = db.Column(db.String(17), primary_key=True)
    year = db.Column(db.SmallInteger, nullable=False)
    model_id = db.Column(db.SmallInteger, ForeignKey('vehicle_models.model_id', ondelete='CASCADE'), nullable=False)
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
    vehicle_model = relationship('VehicleModel', back_populates='listings')
    
    __table_args__ = (
        Index('idx_year_model', 'year', 'model_id'),
        Index('idx_mileage', 'mileage'),
    )

class DealerWebsite(db.Model):
    __tablename__ = 'dealer_websites'
    
    dealer_id = db.Column(db.Integer, ForeignKey('dealers.dealer_id', ondelete='CASCADE'), primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    
    # Relationships
    dealer = relationship('Dealer', back_populates='website') 