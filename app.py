import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)


# Flask Routes
@app.route("/")
def welcome():
    """Available api routes."""
    return (
        f"Available API Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        "</br>"
        f"/api/v1.0/temp/<start></br>"
        'Temp & Date Query (min, avg, max): After temp/[insert start date] as format "YYYY-MM-DD".</br>'
        "</br>"
        f"/api/v1.0/temp/<start>/<end></br>"
        'Temp & Date Range Query (min, avg, max): After temp/[insert start date]/[insert end date] as format "YYYY-MM-DD".'
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query dates and precipation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_dates = {date:prcp for date, prcp in results}

    return jsonify(all_dates)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query station names
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Create last year and most active station variables
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    active_sts = session.query(Measurement.station,func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_sts[0][0]

    # Query temps for most active station over previous year
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date >= year_ago).all()

    session.close()

    # Convert list of tuples into normal list
    temp_date = {date:tobs for date, tobs in results}

    return jsonify(temp_date)


@app.route("/api/v1.0/temp/<start>")
def start_date(start=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query min, average, and max temps for any given date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results))

    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>/<end>")
def startdate_enddate(start=None,end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # # Query min, average, and max temps for any given date range.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    temp_start_end = list(np.ravel(results))

    return jsonify(temp_start_end)


if __name__ == '__main__':
    app.run(debug=True)

