# Import the dependencies.
from os import startfile
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
st = Base.classes.station
me = Base.classes.measurement

# Create session engine
session=Session(engine)



###############################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    # List all the available routes.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - dictionary of precipitation for one year<br/>"
        f"/api/v1.0/stations - list of stations<br/>"
        f"/api/v1.0/tobs - list of temperature observations for most active station<br/>"
        f"/api/v1.0/start - min,max, and avg temperature from start date (must be in YYYY-MM-DD format)<br/>"
        f"/api/v1.0/start/end - min,max, and avg temperature from start date to end date (must be in YYYY-MM-DD format)"
    )


@app.route('/api/v1.0/precipitation')
def prcp():
    # Calculate the date one year from the last date in data set.
    current_date = session.query(me.date).order_by(me.date.desc()).first()[0]
    prev_year = dt.datetime.strftime(dt.datetime.strptime(current_date,'%Y-%m-%d') - dt.timedelta(days = 365),'%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    dt_prcp = session.query(me.date,me.prcp).\
        filter(me.date >= prev_year).\
        order_by(me.date.desc()).all()
        
    session.close()

 # Precipitation scores and date held in dictionaries
    precipitation_dictionary = {date: pr for (date, pr) in dt_prcp}
    # Return dictionary jsonify
    return jsonify(precipitation_dictionary)



@app.route('/api/v1.0/stations')
def stations():
    # Query station id and name
    station_list = session.query(st.station,st.name).all()
    print('Successful stations query')
    session.close()
    return jsonify([(i[0],i[1]) for i in station_list])


@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year from the last date in data set.
    current_date = session.query(me.date).order_by(me.date.desc()).first()[0]
    prev_year = dt.datetime.strftime(dt.datetime.strptime(current_date,'%Y-%m-%d') - dt.timedelta(days = 365),'%Y-%m-%d')

    # Order stations by number of occurrences for the active station
    active_st=session.query(me.station,(func.count(me.id))).group_by(me.station).order_by(func.count(me.id).desc()).all()
    
    # Find temperature observations of most active station
    station_name = active_st[0][0]
    temps=session.query(me.tobs).filter(me.station == station_name).filter(me.date >= prev_year).all()
    print('Successful tobs query')
    session.close()
    return jsonify([i[0] for i in temps])


@app.route('/api/v1.0/<start>')
def temps_date(start):
    try:
        dt.date.fromisoformat(start)
    except ValueError:
        return jsonify({"Error": f"Date must be in 'YYYY-MM-DD' format"})

    #Get the date and fetch results for the same.

    temp_query=session.query(func.min(me.tobs),func.max(me.tobs),func.avg(me.tobs))\
        .filter(me.date >= start).all()
    print('Successful start date query')
    session.close()
    return jsonify([temp_query[0][0],temp_query[0][1],temp_query[0][2]])

@app.route('/api/v1.0/<start>/<end>')
def temps_start_end(start,end):
    # Check if date is in right format YYYY-MM-DD
    try:
        dt.date.fromisoformat(start)
        dt.date.fromisoformat(end)
        assert start < end
    except ValueError:
        return jsonify({"error": f"Date must be in YYYY-MM-DD format."})
    except AssertionError:
        return jsonify({"error": f"End date must be later than start date."})
    
    # Query based on date used
    temp_metrics = session.query(func.min(me.tobs),func.max(me.tobs),func.avg(me.tobs))\
        .filter(me.date >= start).filter(me.date <= end)\
        .all()
    print('Successful start-end date query')
    session.close()

    
    return jsonify([temp_metrics[0][0],temp_metrics[0][1],temp_metrics[0][2]])


if __name__ == '__main__':
    app.run(debug=True)







