# add imports
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect

from flask import Flask, jsonify

# database setup
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# # reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Define what to do when a user hits the index route


@app.route("/")
def home():
    """List all available api routes."""
    return (f"available routes:<br>"
             f"/api/v1.0/precipitation<br>"
             f"/api/v1.0/stations<br>"
             f"/api/v1.0/tobs<br>"
             f"/api/v1.0/<start>")


# * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

#   * Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    precip = session.query(measurement.date, measurement.prcp).all()

    session.close()


    all_precip = []

    for date, prcp in precip:
        all_precip_dict = {}
        all_precip_dict["date"] = date
        all_precip_dict["prcp"] = prcp
        all_precip.append(all_precip_dict)

    return jsonify(all_precip)


#   * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_names = session.query(station.station).\
            group_by(station.station).all()

    session.close()

    return jsonify(station_names)


#   * Query the dates and temperature observations of the most active station for the last year of data.


#   * Return a JSON list of temperature observations (TOBS) for the previous year.


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Design a query to find the most active stations (i.e. what stations have the most rows?)

    most_active=session.query(measurement.station, func.count(measurement.station)).\
                group_by(measurement.station).\
                order_by(func.count(measurement.station).desc()).first()


    #recent date varible for forumlas - .date was from web allowed variable to not be a tuple/list
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
  

    # Calculate the date one year from the last date in data set.
    last_twelve_months = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    most_active_station=most_active.station



    most_active_obs_data = session.query(measurement.tobs).\
    filter(measurement.date >= last_twelve_months).\
    filter(measurement.station == most_active_station).\
    group_by(measurement.date).all()

    session.close()

    twelve_month_temps=list(np.ravel(most_active_obs_data))

  

    return jsonify(twelve_month_temps)
        


#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#* When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    # https://geo-python.github.io/site/notebooks/L6/numpy/Advanced-data-processing-with-NumPy.html

## https://geo-python.github.io/site/notebooks/L6/numpy/Advanced-data-processing-with-NumPy.html

@app.route("/api/v1.0/<start>")
def start_search(start):
    session = Session(engine)

    start_date= dt.datetime.strptime(start, '%m-%d-%Y')

    start_date_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date>= start_date).all()
    
    session.close()

    return jsonify(start_date_temps)

    
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@ app.route("/api/v1.0/<first>/<end>")
def first_end(first,end):

    session = Session(engine)

    start_date= dt.datetime.strptime(first, '%m-%d-%Y')
    
    end_date= dt.datetime.strptime(end, '%m-%d-%Y')

    btwn_date_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    
    session.close()

    
    

    return jsonify(btwn_date_temps)



# MUST HAVE THIS CODE OR IT WILL NOT RUN!
if __name__ == "__main__":
    app.run(debug=True)
