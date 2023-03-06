import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import session, sessionmaker
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#connect engine
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

#Reflection
Base = automap_base()
Base.prepare(engine)

#classes
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session
Session = sessionmaker(bind=engine)
session = Session()

#create api
app= Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate Analysis<br/>"
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p> 'Start' and 'End' date need to be in MMDDYYYY format.</p>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).all()

    session.close()
    prcp = {date: prcp for date, prcp in prcp}

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(station=stations)

@app.route("/api/v1.0/tobs")
def temp():
    prior_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= prior_yr).all()
    
    session.close()

    temp = list(np.ravel(results))

    return jsonify(temp = temp)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start = None, end = None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end: 
        start = dt.datetime.strptime(start, "%m%d%Y")
        result = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()
        temps = list(np.ravel(result))
        return jsonify(temps = temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    result = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    temps = list(np.ravel(result))
    return jsonify(temps)



if __name__ == "__main__":
    app.run(debug=True)



