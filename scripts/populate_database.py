import sys
import os
import time
from urllib.parse import quote_plus 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Dealer, Vehicle, Listing, DealerWebsite
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Safely encode DB credentials
    db_user = quote_plus(os.getenv('DB_USER'))
    db_password = quote_plus(os.getenv('DB_PASSWORD'))
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3307')
    db_name = os.getenv('DB_NAME')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app
def get_file_line_count(file_path):
    """Get total number of lines in file for progress tracking"""
    print("Counting lines in file...")
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f) - 1  # Subtract 1 for header
    print(f"File contains {line_count:,} data lines")
    return line_count

def process_file(file_path, app):
    total_processed = 0
    total_errors = 0
    
    # Get total line count for progress tracking
    total_lines = get_file_line_count(file_path)
    
    # Progress tracking variables
    start_time = time.time()
    last_progress_time = start_time
    progress_interval = 1000  # Show progress every 1000 lines
    
    print(f"\nStarting to process {total_lines:,} lines...")
    print("=" * 50)

    try:
        with open(file_path, 'r') as f:
            next(f)  # Skip header
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Show progress every N lines
                if line_num % progress_interval == 0:
                    current_time = time.time()
                    elapsed = current_time - start_time
                    progress_elapsed = current_time - last_progress_time
                    
                    # Calculate rates
                    overall_rate = line_num / elapsed if elapsed > 0 else 0
                    recent_rate = progress_interval / progress_elapsed if progress_elapsed > 0 else 0
                    
                    # Calculate ETA
                    remaining_lines = total_lines - line_num
                    eta_seconds = remaining_lines / overall_rate if overall_rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    
                    # Progress percentage
                    progress_pct = (line_num / total_lines) * 100
                    
                    print(f"Progress: {line_num:,}/{total_lines:,} ({progress_pct:.1f}%) | "
                          f"Rate: {overall_rate:.1f}/sec (recent: {recent_rate:.1f}/sec) | "
                          f"Processed: {total_processed:,} | Errors: {total_errors:,} | "
                          f"ETA: {eta_minutes:.1f}min")
                    
                    last_progress_time = current_time
                
                fields = line.split('|')
                if len(fields) != 25:
                    total_errors += 1
                    if total_errors <= 10:  # Only show first 10 errors to avoid spam
                        print(f"  ERROR: Line {line_num} - Invalid field count: {len(fields)} fields")
                    elif total_errors == 11:
                        print("  ... (suppressing further field count errors)")
                    continue

                try:
                    # Extract and validate critical fields
                    vin, year_str, make, model, trim = fields[0:5]
                    dealer_info = fields[5:10]  # name, street, city, state, zip
                    price_str, mileage_str = fields[10:12]
                    used_str, certified_str = fields[12:14]
                    style, driven_wheels, engine, fuel_type = fields[14:18]
                    ext_color, int_color = fields[18:20]
                    website, first_seen, last_seen, vdp_last_seen, status = fields[20:25]

                    # Check required fields
                    if not (vin and year_str and first_seen and last_seen):
                        raise ValueError("Missing required field(s)")

                    # Convert types
                    year = int(year_str)
                    price = float(price_str) if price_str else None
                    mileage = int(mileage_str) if mileage_str else None
                    used = used_str == 'TRUE'
                    certified = certified_str == 'TRUE'

                    # Handle empty strings
                    trim = trim or None
                    style = style or None
                    driven_wheels = driven_wheels or None
                    engine = engine or None
                    fuel_type = fuel_type or None
                    ext_color = ext_color or None
                    int_color = int_color or None
                    vdp_last_seen = vdp_last_seen or None
                    status = status or None

                    with app.app_context():
                        # Create or get dealer
                        dealer = Dealer.query.filter_by(
                            name=dealer_info[0],
                            street=dealer_info[1],
                            city=dealer_info[2],
                            state=dealer_info[3],
                            zip=dealer_info[4]
                        ).first()
                        
                        if not dealer:
                            dealer = Dealer(
                                name=dealer_info[0],
                                street=dealer_info[1],
                                city=dealer_info[2],
                                state=dealer_info[3],
                                zip=dealer_info[4]
                            )
                            db.session.add(dealer)
                            db.session.flush()  # Get dealer_id

                        # Create or get vehicle model
                        vehicle = Vehicle.query.filter_by(
                            make=make,
                            model=model
                        ).first()
                        
                        if not vehicle:
                            vehicle = Vehicle(
                                make=make,
                                model=model
                            )
                            db.session.add(vehicle)
                            db.session.flush()  # Get model_id

                        # Create or update website
                        if website:
                            dealer_website = DealerWebsite.query.get(dealer.dealer_id)
                            if dealer_website:
                                dealer_website.url = website
                            else:
                                dealer_website = DealerWebsite(
                                    dealer_id=dealer.dealer_id,
                                    url=website
                                )
                                db.session.add(dealer_website)

                        # Create or update listing
                        listing = Listing.query.get(vin)
                        if listing:
                            # Update existing listing
                            listing.year = year
                            listing.model_id = vehicle.model_id
                            listing.trim = trim
                            listing.dealer_id = dealer.dealer_id
                            listing.price = price
                            listing.mileage = mileage
                            listing.used = used
                            listing.certified = certified
                            listing.style = style
                            listing.driven_wheels = driven_wheels
                            listing.engine = engine
                            listing.fuel_type = fuel_type
                            listing.exterior_color = ext_color
                            listing.interior_color = int_color
                            listing.first_seen = datetime.strptime(first_seen, '%Y-%m-%d').date()
                            listing.last_seen = datetime.strptime(last_seen, '%Y-%m-%d').date()
                            listing.vdp_last_seen = datetime.strptime(vdp_last_seen, '%Y-%m-%d').date() if vdp_last_seen else None
                            listing.status = status
                        else:
                            # Create new listing
                            listing = Listing(
                                vin=vin,
                                year=year,
                                model_id=vehicle.model_id,
                                trim=trim,
                                dealer_id=dealer.dealer_id,
                                price=price,
                                mileage=mileage,
                                used=used,
                                certified=certified,
                                style=style,
                                driven_wheels=driven_wheels,
                                engine=engine,
                                fuel_type=fuel_type,
                                exterior_color=ext_color,
                                interior_color=int_color,
                                first_seen=datetime.strptime(first_seen, '%Y-%m-%d').date(),
                                last_seen=datetime.strptime(last_seen, '%Y-%m-%d').date(),
                                vdp_last_seen=datetime.strptime(vdp_last_seen, '%Y-%m-%d').date() if vdp_last_seen else None,
                                status=status
                            )
                            db.session.add(listing)

                        db.session.commit()
                        total_processed += 1

                except Exception as e:
                    db.session.rollback()
                    total_errors += 1
                    if total_errors <= 10:  # Only show first 10 detailed errors
                        print(f"  ERROR: Line {line_num} - {str(e)}")
                    elif total_errors == 11:
                        print("  ... (suppressing further detailed errors)")

    except Exception as e:
        print(f"File error: {e}")
        sys.exit(1)
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"Processing complete!")
    print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"Average rate: {total_lines/total_time:.1f} lines/second")
    print(f"Lines processed: {total_lines:,}")
    print(f"Records successfully processed: {total_processed:,}")
    print(f"Errors encountered: {total_errors:,}")
    
    if total_errors > 0:
        error_rate = (total_errors / total_lines) * 100
        print(f"Error rate: {error_rate:.2f}%")

    return total_processed, total_errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python populate_database.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    file_size = os.path.getsize(file_path)
    print(f"Processing file: {file_path}")
    print(f"File size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)")
    
    app = create_app()
    
    with app.app_context():
        db.create_all()  # This will create tables if they don't exist
        print("Tables created/verified")
        
        total_processed, total_errors = process_file(file_path, app)
        print(f"\nFinal Summary: {total_processed:,} records processed, {total_errors:,} errors")

if __name__ == "__main__":
    main()
