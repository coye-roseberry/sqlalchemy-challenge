from tracemalloc import start
from unittest import result
from matplotlib import style
from requests import session
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, null
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement

station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route('/')
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Home Page<br/>"
        f"The following routes are available:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (Format date as YYYY-MM-DD)<br/>"
        f"/api/v1.0/<start>/<end> (Format date as YYYY-MM-DD)<br/>"
)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    results = session.query(measurement.date,measurement.prcp).all()
    session.close()
    all_precipitation = []

    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precipitation.append(precip_dict)



    return jsonify(all_precipitation)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    mrdQuery = [r for r in session.query(measurement.date).order_by(measurement.date.desc()).first()]
    most_recent_date = mrdQuery[0]
    yearcalc = (datetime.strptime(most_recent_date, '%Y-%m-%d')) - timedelta(days=365)
    year_ago_date = datetime.strftime(yearcalc,'%Y-%m-%d')

    
    results = session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date.between(year_ago_date, most_recent_date)).all()

    session.close()
    tobs_most_active = list(np.ravel(results))

    return jsonify(tobs_most_active)


@app.route('/api/v1.0/<start>')
def start_route(start):
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date>=start).all()

    session.close()

    minAvgMax_tobs_start_only = list(np.ravel(results))

    if (minAvgMax_tobs_start_only[0] is None) or (minAvgMax_tobs_start_only[1] is None) or (minAvgMax_tobs_start_only[2] is None):
        return jsonify('Data not found. Please make sure you have entered the dates correctly in a YYYY-MM-DD format. Or this dataset may not include requested data')

    else:
        return jsonify(f'For {start} and dates after, TMIN is {minAvgMax_tobs_start_only[0]}. TAVG is {minAvgMax_tobs_start_only[1]}. TMAX is {minAvgMax_tobs_start_only[2]}')


@app.route('/api/v1.0/<start>/<end>')
def start_end_route(start,end):
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date.between(start, end)).all()

    session.close()

    minAvgMax_tobs = list(np.ravel(results))

    if (minAvgMax_tobs[0] is None) or (minAvgMax_tobs[1] is None) or (minAvgMax_tobs[2] is None):
        return jsonify('Data not found. Please make sure you have entered the dates correctly in a YYYY-MM-DD format and your end date is after your start date')

    else:
        return jsonify(f'For the period between {start} and {end}, TMIN is {minAvgMax_tobs[0]} TAVG is {minAvgMax_tobs[1]} TMAX is {minAvgMax_tobs[2]}')










if __name__ == "__main__":
    app.run(debug=True)