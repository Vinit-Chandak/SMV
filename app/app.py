from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, and_
from sqlalchemy import *


app = Flask(__name__)

# Replace the placeholder values with your actual database credentials
username = "group_13"
password = "QcNtcHm7Hmqg9q"
hostname = "10.17.50.91"
port = "5000"
database_name = "prod"

# Construct the connection string
connection_string = f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}"

# Configure the Flask app to use SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

class States(db.Model):
    __tablename__ = 'states'
    State = db.Column(db.String, primary_key=True)
    cities = db.relationship('Cities', back_populates='state_rel')
    aqis = db.relationship('AQI', back_populates='state_rel')

class Cities(db.Model):
    __tablename__ = 'cities'
    City = db.Column(db.String, primary_key=True)
    State = db.Column(db.String, db.ForeignKey('states.State'))
    state_rel = db.relationship('States', back_populates='cities')
    aqis = db.relationship('AQI', back_populates='city_rel', overlaps="cities")

class State_Subdivision(db.Model):
    __tablename__ = 'state_subdivision'
    State = db.Column(db.String(30), ForeignKey('states.State'), primary_key=True)
    Subdivision = db.Column(db.String(50), primary_key=True)
    
    state_rel = db.relationship('States', backref=db.backref('state_subdivisions', lazy=True))

class State_CO2(db.Model):
    __tablename__ = 'state_co2'
    State = db.Column(db.String(30), ForeignKey('states.State'), primary_key=True)
    Year = db.Column(db.Integer, primary_key=True)
    CO2_Emissions = db.Column(db.Numeric(10, 2), default=None)
    
    state_rel = db.relationship('States', backref=db.backref('state_co2', lazy=True))

class Average_Temperature(db.Model):
    __tablename__ = 'average_temperature'
    State = db.Column(db.String(30), ForeignKey('states.State'), primary_key=True)
    Month = db.Column(db.String(15), primary_key=True)
    Year = db.Column(db.Integer, primary_key=True)
    Average_Temperature = db.Column(db.Numeric(5, 3), default=None)
    Average_Temperature_Uncertainity = db.Column(db.Numeric(5, 3), default=None)
    
    state_rel = db.relationship('States', backref=db.backref('average_temperatures', lazy=True))

class CO2(db.Model):
    __tablename__ = 'co2'
    Year = db.Column(db.Integer, primary_key=True)
    Population = db.Column(db.Numeric(10), default=None)
    Gdp = db.Column(db.Numeric(13), default=None)
    cement_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Co2_including_luc_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Coal_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Consumption_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Energy_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Flaring_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Gas_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Ghg_excluding_lucf_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Ghg_per_capita = db.Column(db.Numeric(10, 3), default=None)
    Land_use_change_co2_per_capita = db.Column(db.Numeric(10, 3), default=None)

class Sealevel(db.Model):
    __tablename__ = 'sealevel'
    State = db.Column(db.String(30), ForeignKey('states.State'), primary_key=True)
    Sea_Shore_City = db.Column(db.String(30), ForeignKey('cities.City'), primary_key=True)
    Year = db.Column(db.Integer, primary_key=True)
    Month = db.Column(db.String(20), primary_key=True)
    Monthly_MSL = db.Column(db.Numeric(4, 3), default=None)
    Linear_Trend = db.Column(db.Numeric(4, 3), default=None)
    High_Conf = db.Column(db.Numeric(4, 3), default=None)
    Low_Conf = db.Column(db.Numeric(4, 3), default=None)

    state_rel = db.relationship('States', backref=db.backref('sealevels', lazy=True))
    city_rel = db.relationship('Cities', backref=db.backref('sealevels', lazy=True))

class Rainfall(db.Model):
    __tablename__ = 'rainfall'
    Subdivision = db.Column(db.String(50), ForeignKey('state_subdivision.Subdivision'), primary_key=True)
    Year = db.Column(db.Integer, primary_key=True)
    January = db.Column(db.Numeric(5, 1), default=None)
    February = db.Column(db.Numeric(5, 1), default=None)
    March = db.Column(db.Numeric(5, 1), default=None)
    April = db.Column(db.Numeric(5, 1), default=None)
    May = db.Column(db.Numeric(5, 1), default=None)
    June = db.Column(db.Numeric(5, 1), default=None)
    July = db.Column(db.Numeric(5, 1), default=None)
    August = db.Column(db.Numeric(5, 1), default=None)
    September = db.Column(db.Numeric(5, 1), default=None)
    October = db.Column(db.Numeric(5, 1), default=None)
    November = db.Column(db.Numeric(5, 1), default=None)
    December = db.Column(db.Numeric(5, 1), default=None)
    Annual = db.Column(db.Numeric(5, 1), default=None)
    January_February = db.Column(db.Numeric(5, 1), default=None)
    March_May = db.Column(db.Numeric(5, 1), default=None)
    June_September = db.Column(db.Numeric(5, 1), default=None)
    October_December = db.Column(db.Numeric(5, 1), default=None)

    subdivision_rel = db.relationship('State_Subdivision', backref=db.backref('rainfalls', lazy=True))

class AQI(db.Model):
    __tablename__ = 'aqi'
    City = db.Column(db.String, db.ForeignKey('cities.City'))
    State = db.Column(db.String, db.ForeignKey('states.State'))
    aqi = db.Column(db.Integer, primary_key=True)
    city_rel = db.relationship('Cities', back_populates='aqis', overlaps="cities,state_rel")
    state_rel = db.relationship('States', back_populates='aqis')


@app.route('/states')
def list_states():
    print("Entering /states route")
    states = States.query.all()
    print(f"Fetched {len(states)} states from the database")
    result = ""
    for state in states:
        result += f"{state.State} - {state.Capital}<br>"
    return result

@app.route('/test_connection')
def test_connection():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connection successful"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

@app.route('/')
def index():
    return 'Welcome to the Climate Data Application! Visit <a href="/states">/states</a> to see the list of states and their capitals.'
    return '<a href="/test_connection">test</a>'


if __name__ == "__main__":
    app.run(debug=True)


