from flask import render_template, request

def init_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/search")
    def search():
        return render_template("search.html")

    @app.route("/results", methods=["POST"])
    def results():
        year = request.form.get("year")
        make = request.form.get("make")
        model = request.form.get("model")
        mileage = request.form.get("mileage")
        
        print("Year: ", year)
        print("make: ", make)
        print("Model: ", model)
        print("mileage: ", mileage)
        
        # TODO: Add your price estimation logic here
        # For now, we'll just pass the data to the template
        return render_template("results.html", 
                             year=year,
                             make=make,
                             model=model,
                             mileage=mileage if mileage else None,
                             price=25000,  # Placeholder price
                             listings=[])  # Placeholder listings 