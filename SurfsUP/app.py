# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import os
os.chdir(os.path.dirname(__file__))
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
#1 Start at the homepage. List all the available routes.
@app.route("/")
def welcome():
    """ List all available API routes."""
    return(
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/&lt;start&gt;<br/>"
        f"/api/v1.0/temp/&lt;start&gt;/&lt;end&gt;"
        
        
    )
# 2. Convert the query results from your precipitation analysis
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query results from your precipitation analysis
    to a dictionary. Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    
    # Calculate the date one year from the most recent data point in the database.
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prior_year).all()

    # close the session
    session.close()
    
    # Convert the query to a dictionary using date as the key and prcp as the value
    # We are creating a dictionary from the row data and then appending that into a list
    # Reference: Week 10, Day 3, Activity 10-Ins_Flask_with_ORM
    hawaii_prcp = []
    for date, prcp in results:
        results = {}
        results['date'] = date
        results['prcp'] = prcp
        hawaii_prcp.append(results)
    
    # Return the JSON representation of the dictionary
    return jsonify(hawaii_prcp)

# 3. Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Query the active stations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
             group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Close the session
    session.close()

    # Convert to dictionary using station as key, station count as value
    all_stations = []
    for station, count in active_stations:
        active_stations = {}
        active_stations["station"] = station
        active_stations["count"] = count
        all_stations.append(active_stations)
    
    # Return JSON
    return jsonify(all_stations)

# 4. Query the dates and temperature observations of the most-active station for the previous year of data.
    # Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station
    for the previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
             group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # To find all dates of the previous year, first find the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).first()
    # Next, calculate the date one year from the most recent date in dataset.
    prior_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    
    # Query the dates and temperature observations of the most active station for the previous year
    date_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(
        Measurement.date>= prior_year,\
        Measurement.station == most_active_station).all()
    
    # Close the session
    session.close()
    
    # date_temps is a list of tuples, and we want to convert that to a dictionary
    all_values = []
    for date, tobs in date_temps:
        date_tobs = {}
        date_tobs["date"] = date
        date_tobs["tobs"] = tobs
        all_values.append(date_tobs)
    # Return JSON
    return jsonify(all_values)
    
    # Select statement
    
@app.route("/api/v1.0/temp/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and 
    the maximum temperature for a specified start. 
    For a specified start, calculate TMIN, TAVG, and TMAX for all the dates
    greater than or equal to the start date"""
    # Create our session (link) from Python to the DB.
    
    session = Session(engine)
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Query min temp, avg temp, and max temp for date greater than or equal to start date
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    # start_date_query = session.query(
    #     func.min(Measurement.tobs),\
    #     func.avg(Measurement.tobs),\
    #     func.max(Measurement.tobs)).\
    #     filter(Measurement.date >= start).all()
    start_date_query = session.query(*sel).filter(Measurement.date>=start).all()
    
    # Close the session
    session.close()

    # Convert query results to a dictionary
    start_date_values = []
    for tmin, tavg, tmax in start_date_query:
        start_dict = {}
        start_dict["min"] = tmin
        start_dict["avg"] = tavg
        start_dict["max"] = tmax
        start_date_values.append(start_dict)
    # Return JSON
    return jsonify(start_date_values)

@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the 
    maximum temperature for a specified start-end range. For a specified start date 
    and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date 
    to the end date, inclusive."""
    # Create our session (link) from Python to the DB.
    
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Query min temp, avg temp, and max temp for date greater than or equal to start date
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    # start_date_query = session.query(
    #     func.min(Measurement.tobs),\
    #     func.avg(Measurement.tobs),\
    #     func.max(Measurement.tobs)).\
    #     filter(Measurement.date >= start).all()
    start_end_date_query = session.query(*sel)\
    .filter(Measurement.date >= start,Measurement.date <= end).all()
    
    # Close the session
    session.close()

    # Convert query results to a dictionary
    start_end_date_values = []
    for tmin, tavg, tmax in start_end_date_query:
        start_end_dict = {}
        start_end_dict["min"] = tmin
        start_end_dict["avg"] = tavg
        start_end_dict["max"] = tmax
        start_end_date_values.append(start_end_dict)
        
    # Return JSON
    return jsonify(start_end_date_values)

if __name__ == '__main__':
    app.run(debug=True)
