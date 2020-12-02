# Set up Flask
from flask import Flask, jsonify
import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

app = Flask(__name__)
######## Set up DB ########
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
statsToUse = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

# Calculate the date 1 year ago from the last data point in the database
initialSesh = Session(engine)
lastDate = initialSesh.query(Measurement.date).order_by(desc('date')).first()[0]
searchDate = (dt.date.fromisoformat(lastDate) - dt.timedelta(days=365)).isoformat()
initialSesh.close()

@app.route("/")
def index():
    return (
        f"<h1>Welcome to my Hawaii Climate Stats site!</h1>"
        f"Available Routes:<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/[startDate]</li>"
        f"<li>/api/v1.0/[startDate]/[endDate]</li></ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # query
    session = Session(engine)
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > searchDate).order_by(Measurement.date).all()
    session.close()

    # build a dictionary
    precipData = []
    for date,pre in precip:
        precipDict = {
            date : pre
        }
        precipData.append(precipDict)

    return jsonify(precipData)

@app.route("/api/v1.0/stations")
def stations():
    # query
    session = Session(engine)
    stations = session.query(Station)
    session.close()

    # build a dictionary
    stationList = []
    for station in stations:
        stationDict = {
            'station': station.station,
            'longitude': station.longitude, 
            'name': station.name, 
            'id': station.id, 
            'elevation': station.elevation, 
            'latitude': station.latitude
        }
        stationList.append(stationDict)

    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def tobs():
    # query
    session = Session(engine)
    activeStation = session.query(func.count(Measurement.station), Measurement.station).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).all()[0][1]
    activeLast = session.query(Measurement.tobs).filter(Measurement.station==activeStation).filter(Measurement.date > searchDate).all()
    session.close()

    # make it a list
    activeLast = list(np.ravel(activeLast))

    return jsonify(activeLast)

@app.route("/api/v1.0/<start>")
def startDate(start):
    # query
    session = Session(engine)
    stats = session.query(*statsToUse).filter(Measurement.date >= start).first()
    session.close()

    # build a dictionary
    statList =  {
            'min': stats[0],
            'avg': stats[2], 
            'max': stats[1]
        }

    return jsonify(statList)

@app.route("/api/v1.0/<start>/<end>")
def endDate(start,end):
    # query
    session = Session(engine)
    stats = session.query(*statsToUse).filter(Measurement.date >= start, Measurement.date <= end).first()
    session.close()

    # build a dictionary
    statList =  {
            'min': stats[0],
            'avg': stats[2], 
            'max': stats[1]
        }

    return jsonify(statList) 

# Run it
if __name__ == '__main__':
    app.run(debug=True)