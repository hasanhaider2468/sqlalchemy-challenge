# Import the dependencies.
#imports
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base=automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Prints out preciptation in inches for that given day<br/>"
        f"-------------------------------------------------------------<br/>"
        f"/api/v1.0/stations<br/>"
        f"Prints out all of the stations<br/>"
        f"-------------------------------------------------------------<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Prints out temperature for the most active station in the past year<br/>"
        f"-------------------------------------------------------------<br/>"
        f"/api/v1.0/start<br/>" 
        f"Prints out average , maximum and minimum for a specified start date<br/>"
        f"-------------------------------------------------------------<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Prints out average , maximum and minimum for a specified start date and end date<br/>"
        f"-------------------------------------------------------------<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    
    year_ago=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
    order_by(Measurement.date).all()
    
    session.close()
    
    prcp_data = []
    for key,value in year_ago:
        diction = {}
        diction[key] = value
        prcp_data.append(diction)
        
    return jsonify(prcp_data)

@app.route("/api/v1.0/precipitation")
def stations():
    
        session = Session(engine)
    
        stations = (session.query(Measurement.station).group_by(Measurement.station).all())

        session.close()
        
        return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)
    
    active_stations = (session.query(Measurement.station,func.count(Measurement.station))\
                   .group_by(Measurement.station)\
                   .order_by(func.count(Measurement.station).desc()).all())
    
    most_active = active_stations[0][0]
    
    year_ago=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(Measurement.station == most_active).order_by(Measurement.date).all()
    
    session.close()
    
    temp_data = []
    
    for key,value in year_ago:
        diction = {}
        diction[key] = value
        temp_data.append(diction)
        
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    temp_desc = (session.query(func.min(Measurement.tobs),
                func.max(Measurement.tobs),func.avg(Measurement.tobs))\
                   .filter(Measurement.date >= start)).all()
    session.close()
    
    dict_values = [{"Minimum":temp_desc[0][0],"Maximum":temp_desc[0][1],"Average":temp_desc[0][1]}]

    return jsonify(dict_values)

@app.route("/api/v1.0/<start>/<end>")
def dates(start,end):
    session = Session(engine)
    temp_desc = (session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
                   .filter(Measurement.date >= start).filter(Measurement.date <= end)).all()
    
    session.close()
    
    dict_values = [{"Minimum":temp_desc[0][0],"Maximum":temp_desc[0][1],"Average":temp_desc[0][1]}]

    return jsonify(dict_values)
    

if __name__ == '__main__':
    app.run(debug=True)
                                  


