# Import the dependencies.
from matplotlib import style

style.use("fivethirtyeight")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
print(Base.classes.keys())

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        "<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).first()
    most_recent_date = str(most_recent_date)
    most_recent_as_dt = datetime.strptime(most_recent_date, "('%Y-%m-%d',)").date()

    # Calculate the date one year from the last date in data set.
    one_year_ago = most_recent_as_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    data_df = pd.DataFrame(data)
    data_df = data_df.rename(columns={"date": "Date", "prcp": "Precipitation (in)"})

    # Sort the dataframe by date
    sorted_data_df = data_df.sort_values(by=["Date"], ascending=True)
    data_dict = sorted_data_df.to_dict("split")["data"]

    return jsonify(data_dict)


@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(
        Station.station,
        Station.name,
        Station.latitude,
        Station.longitude,
        Station.elevation,
    ).all()

    station_dicts = [
        {
            "station": station.station,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation,
        }
        for station in station_list
    ]

    return jsonify(station_dicts)


# @app.route(/api/v1.0/tobs)
# def tobs():


if __name__ == "__main__":
    app.run(debug=True)
