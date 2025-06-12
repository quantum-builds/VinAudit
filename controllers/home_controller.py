from .base_controller import BaseController
from flask import request
from models import Vehicle, Listing, Prediction, db
from sqlalchemy import func
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

class HomeController(BaseController):
    """Controller for handling home page and search functionality."""
    
    def index(self) -> str:
        """
        Handle the index route.
        
        Returns:
            Rendered index template
        """
        return self.render("index.html")
    
    def search(self) -> str:
        """
        Handle the search page route.
        
        Returns:
            Rendered search template with available makes and models
        """
        # Get unique makes and models for the search form
        makes = Vehicle.query.with_entities(Vehicle.make).distinct().all()
        makes = [make[0] for make in makes]
        
        return self.render("search.html", makes=makes)
    
    def results(self) -> str:
        """
        Handle the search results route.
        
        Returns:
            Rendered results template with search results
        """
        # Get search parameters
        year = request.form.get("year")
        make = request.form.get("make")
        model = request.form.get("model")
        mileage = request.form.get("mileage")
        
        # Build query
        query = Listing.query.join(Vehicle)
        
        if year:
            query = query.filter(Listing.year == year)
        if make:
            query = query.filter(Vehicle.make == make)
        if model:
            query = query.filter(Vehicle.model == model)

        # Get all matching listings and filter out those with None prices
        all_listings = [l for l in query.all() if l.price is not None]
        
        # Use up to 100 sample listings for both display and regression
        sample_listings = all_listings[:100]
    
        # Try to get cached prediction first
        estimated_price = 0
        if year and make and model and sample_listings:  # Only proceed if we have valid listings
            vehicle = Vehicle.query.filter_by(make=make, model=model).first()
            if vehicle:
                prediction = Prediction.query.filter_by(
                    year=int(year),
                    model_id=vehicle.model_id,
                    mileage=int(mileage) if mileage else None
                ).first()
                
                if prediction:
                    # Update last_used_at timestamp
                    prediction.last_used_at = datetime.utcnow()
                    db.session.commit()
                    estimated_price = prediction.predicted_price
                elif len(sample_listings) >= 2:
                    # Calculate new prediction
                    X = np.array([l.mileage for l in sample_listings]).reshape(-1, 1)
                    y = np.array([l.price for l in sample_listings])
                    lr_model = LinearRegression()
                    lr_model.fit(X, y)
                    
                    # Calculate confidence score based on R²
                    confidence_score = lr_model.score(X, y)
                    
                    # Predict price at the median mileage of the sample set
                    median_mileage = float(np.median(X))
                    estimated_price = lr_model.predict([[median_mileage]])[0]
                    
                    # Cache the prediction
                    new_prediction = Prediction(
                        year=int(year),
                        model_id=vehicle.model_id,
                        mileage=int(mileage) if mileage else None,
                        predicted_price=estimated_price,
                        confidence_score=confidence_score,
                        sample_size=len(sample_listings)
                    )
                    db.session.add(new_prediction)
                    db.session.commit()
        
        # Round the estimated price to the nearest hundred
        estimated_price = int(round(estimated_price / 100.0)) * 100
        
        return self.render(
            "results.html",
            year=year,
            make=make,
            model=model,
            mileage=mileage if mileage else None,
            estimated_price=estimated_price,
            listings=sample_listings
        )