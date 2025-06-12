# VinAudit - Vehicle Price Estimation System

VinAudit is a Flask-based web application that provides vehicle price estimation using machine learning. The system analyzes vehicle listings and uses linear regression to predict market prices based on various factors like mileage, make, model, and year.

## Features

- Vehicle search functionality with filtering by year, make, model, and mileage
- Price estimation using machine learning (linear regression)
- Caching system for price predictions to improve performance
- Responsive web interface with Bootstrap
- MySQL database for data storage
- Docker support for easy deployment

## Tech Stack

- **Backend**: Python 3.12, Flask 3.1.1
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0.41
- **Machine Learning**: scikit-learn 1.7.0
- **Frontend**: Bootstrap, Jinja2 templates
- **Containerization**: Docker

## Project Structure

```
VinAudit/
├── controllers/         # Business logic and request handling
├── models/             # Database models and relationships
├── templates/          # Jinja2 HTML templates
├── migrations/         # Database migration files
├── routes/            # Route definitions
├── scripts/           # Utility scripts
├── app.py             # Application entry point
├── requirements.txt   # Python dependencies
└── docker-compose.yml # Docker configuration
```

## Prerequisites

- Python 3.12 or higher
- MySQL 8.0
- Docker and Docker Compose (for containerized deployment)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd VinAudit
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:

```
DB_USER=vin_user
DB_PASSWORD=vin_pass
DB_HOST=localhost
DB_PORT=3307
DB_NAME=vin_db
```

## Running the Application

### Using Docker (Recommended)

1. Start the containers:

```bash
docker-compose up -d
```

2. The application will be available at `http://localhost:5000`

### Running Locally

1. Start MySQL server (if not using Docker)

2. Run database migrations:

```bash
flask db upgrade
```

3. Start the Flask application:

```bash
python app.py
```

## Database Population

The application includes a script to populate the database with vehicle listings from a text file. The input file should be pipe-delimited (|) with the following fields:

```
VIN|Year|Make|Model|Trim|DealerName|Street|City|State|Zip|Price|Mileage|Used|Certified|Style|DrivenWheels|Engine|FuelType|ExteriorColor|InteriorColor|Website|FirstSeen|LastSeen|VdpLastSeen|Status
```

Example line:

```
1HGCM82633A123456|2003|Honda|Accord|EX|ABC Motors|123 Main St|Los Angeles|CA|90001|15000|50000|TRUE|FALSE|Sedan|FWD|2.4L I4|Gasoline|Silver|Black|http://abcmotors.com|2024-01-01|2024-01-15|2024-01-15|Active
```

To populate the database:

1. Prepare your data file in the format described above
2. Run the population script:

```bash
python scripts/populate_database.py path/to/your/data.txt
```

The script will:

- Create necessary database tables if they don't exist
- Process each line in the input file
- Create or update dealers, vehicles, and listings
- Handle duplicate entries by updating existing records
- Report the number of records processed and any errors

Note: The script requires the database to be running and properly configured in your `.env` file.

## Usage

1. Access the application at `http://localhost:5000`
2. Use the search form to find vehicles by:
   - Year
   - Make
   - Model
   - Mileage
3. View the estimated price and sample listings used for the calculation

## Database Schema

The application uses the following main models:

- `Vehicle`: Stores vehicle make and model information
- `Listing`: Contains individual vehicle listings with price and mileage
- `Prediction`: Caches price predictions for improved performance
- `Dealer`: Stores dealer information
