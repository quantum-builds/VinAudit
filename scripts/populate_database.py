import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.mysql import MySQLDatabase

CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS dealers (
        dealer_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        street VARCHAR(255),
        city VARCHAR(255) NOT NULL,
        state CHAR(2) NOT NULL,
        zip VARCHAR(10) NOT NULL,
        UNIQUE KEY dealer_loc (name(50), street(50), city, state, zip)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS vehicle_models (
        model_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
        make VARCHAR(255) NOT NULL,
        model VARCHAR(255) NOT NULL,
        UNIQUE KEY make_model (make, model)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS listings (
        vin VARCHAR(17) PRIMARY KEY,
        year SMALLINT NOT NULL,
        model_id SMALLINT NOT NULL,
        trim VARCHAR(255),
        dealer_id INT NOT NULL,
        price DECIMAL(10,2),
        mileage INT,
        used BOOLEAN NOT NULL DEFAULT 1,
        certified BOOLEAN NOT NULL DEFAULT 0,
        style VARCHAR(255),
        driven_wheels VARCHAR(255),
        engine VARCHAR(255),
        fuel_type VARCHAR(255),
        exterior_color VARCHAR(255),
        interior_color VARCHAR(255),
        first_seen DATE NOT NULL,
        last_seen DATE NOT NULL,
        vdp_last_seen DATE,
        status VARCHAR(20),
        
        INDEX idx_year_model (year, model_id),
        INDEX idx_mileage (mileage),
        FOREIGN KEY (model_id) 
            REFERENCES vehicle_models(model_id) ON DELETE CASCADE,
        FOREIGN KEY (dealer_id) 
            REFERENCES dealers(dealer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS dealer_websites (
        dealer_id INT PRIMARY KEY,
        url VARCHAR(255) NOT NULL,
        FOREIGN KEY (dealer_id) 
            REFERENCES dealers(dealer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def create_tables(connection):
    cursor = connection.cursor()
    try:
        for query in CREATE_TABLE_QUERY.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
    finally:
        cursor.close()

def process_file(file_path, connection):
    total_processed = 0
    total_errors = 0

    # SQL Queries
    dealer_insert = """
        INSERT INTO dealers (name, street, city, state, zip)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE dealer_id = LAST_INSERT_ID(dealer_id)
    """
    model_insert = """
        INSERT INTO vehicle_models (make, model)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE model_id = LAST_INSERT_ID(model_id)
    """
    website_insert = """
        INSERT INTO dealer_websites (dealer_id, url)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE url = VALUES(url)
    """
    listing_insert = """
        INSERT INTO listings (
            vin, year, model_id, trim, dealer_id, price, mileage, used, certified, style, 
            driven_wheels, engine, fuel_type, exterior_color, interior_color, 
            first_seen, last_seen, vdp_last_seen, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            year = VALUES(year),
            model_id = VALUES(model_id),
            trim = VALUES(trim),
            dealer_id = VALUES(dealer_id),
            price = VALUES(price),
            mileage = VALUES(mileage),
            used = VALUES(used),
            certified = VALUES(certified),
            style = VALUES(style),
            driven_wheels = VALUES(driven_wheels),
            engine = VALUES(engine),
            fuel_type = VALUES(fuel_type),
            exterior_color = VALUES(exterior_color),
            interior_color = VALUES(interior_color),
            first_seen = VALUES(first_seen),
            last_seen = VALUES(last_seen),
            vdp_last_seen = VALUES(vdp_last_seen),
            status = VALUES(status)
    """

    try:
        with open(file_path, 'r') as f:
            next(f)  # Skip header
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                fields = line.split('|')
                if len(fields) != 25:
                    total_errors += 1
                    print(f"Skipping line (invalid field count): {line}")
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
                    used = 1 if used_str == 'TRUE' else 0
                    certified = 1 if certified_str == 'TRUE' else 0

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

                    with connection.cursor() as cursor:
                        # Insert dealer and get ID
                        cursor.execute(dealer_insert, dealer_info)
                        dealer_id = cursor.lastrowid

                        # Insert model and get ID
                        cursor.execute(model_insert, (make, model))
                        model_id = cursor.lastrowid

                        # Insert website if exists
                        if website:
                            cursor.execute(website_insert, (dealer_id, website))

                        # Insert listing
                        listing_data = (
                            vin, year, model_id, trim, dealer_id, price, mileage, used, certified, style,
                            driven_wheels, engine, fuel_type, ext_color, int_color,
                            first_seen, last_seen, vdp_last_seen, status
                        )
                        cursor.execute(listing_insert, listing_data)

                    connection.commit()
                    total_processed += 1

                except Exception as e:
                    connection.rollback()
                    total_errors += 1
                    print(f"Error processing line: {line}\nError: {e}")

    except Exception as e:
        print(f"File error: {e}")
        sys.exit(1)

    return total_processed, total_errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python populate_database.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    db = MySQLDatabase()
    connection = db.get_connection()
    print("Connected to database")
    
    create_tables(connection)
    print("Tables created/verified")
    
    total_processed, total_errors = process_file(file_path, connection)
    
    connection.close()
    print(f"Finished: {total_processed} records processed, {total_errors} errors")

if __name__ == "__main__":
    main()