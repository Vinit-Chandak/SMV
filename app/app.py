from flask import Flask,request,render_template,jsonify
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd

# Init App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

username = "group_13"
password = "QcNtcHm7Hmqg9q"
dbname = "group_13"
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@10.17.50.91:5432/{dbname}"

db = SQLAlchemy(app)

class States(db.Model):
    __tablename__ = 'states'
    state = db.Column(db.String, primary_key=True)
    capital = db.Column(db.String)
    cities = db.relationship('Cities', back_populates='state_rel')
    aqis = db.relationship('AQI', back_populates='state_rel')

class Cities(db.Model):
    __tablename__ = 'cities'
    city = db.Column(db.String, primary_key=True)
    state = db.Column(db.String, db.ForeignKey('states.state'))
    state_rel = db.relationship('States', back_populates='cities')
    aqis = db.relationship('AQI', back_populates='city_rel', overlaps="cities")    

class AQI(db.Model):
    __tablename__ = 'aqi'
    city = db.Column(db.String, db.ForeignKey('cities.city'))
    state = db.Column(db.String, db.ForeignKey('states.state'))
    aqi = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    aqi_bucket = db.Column(db.String)
    pm10 = db.Column(db.Float)
    pm2_5 = db.Column(db.Float)
    city_rel = db.relationship('Cities', back_populates='aqis', overlaps="cities,state_rel")
    state_rel = db.relationship('States', back_populates='aqis')

    def to_dict(self):
        return {
            'city': self.city,
            'state': self.state,
            'aqi': self.aqi,
            'date': self.date,
            'aqi_bucket': self.aqi_bucket,
            'pm10': self.pm10,
            'pm2_5': self.pm2_5
        }

def getstatevalues():
    states = States.query.all()
    result = []
    for state in states:
        result.append(state.state)     
    return result

def getcityvaluesforselectedstates(selectedStateArray):
    cities = Cities.query.filter(Cities.state.in_(selectedStateArray))
    result = []
    for city in cities:
        result.append(city.city)     
    return result

def getaqiforcities(selectedCityArray):
    aqis = AQI.query.filter(AQI.city.in_(selectedCityArray))
    result = []
    for aqi in aqis:
        if(aqi != None):
            #print(f"city: {aqi.city} - aqi: {aqi.aqi} - state: {aqi.state} - date: {aqi.date} - aqi_bucket: {aqi.aqi_bucket} - pm10: {aqi.pm10} - pm2_5: {aqi.pm2_5}")
            result.append(aqi.to_dict())
    data = pd.DataFrame.from_records(result)
    figaqi = px.line(data, x='date', y='aqi', color='city')
    figaqi.show()
    figpm10 = px.line(data, x='date', y='pm10', color='city')
    figpm10.show()
    fig2_5 = px.line(data, x='date', y='pm2_5', color='city')
    fig2_5.show()                 
    return result

@app.route('/states')
def list_states():
    print("Entering /states route")
    states = States.query.all()
    print(f"Fetched {len(states)} states from the database")
    result = ""
    for state in states:
        result += f"{state.state} - {state.capital}<br>"
    return result

@app.route('/cities')
def list_cities():
    print("Entering /cities route")
    cities = Cities.query.all()
    print(f"Fetched {len(cities)} cities from the database")
    result = ""
    for city in cities:
        result += f"{city.city} - {city.state}<br>"
    return result


@app.route('/aqis')
def aqi_data():
    states = getstatevalues()
    return render_template('index.html',
                       all_states=states)
# def list_aqis():
#     print("Entering /aqis route")
#     aqis = AQI.query.all()
#     print(f"Fetched {len(aqis)} aqis from the database")
#     result = ""
#     for aqi in aqis:
#         if(aqi != None):
#             result += f"{aqi.aqi} - {aqi.aqi_bucket} - {aqi.pm10} - {aqi.pm2_5}<br>"
#     return result

@app.route("/ajax_states",methods=["POST","GET"])
def ajax_states():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        #print(selectedStates)
        selectedStates = selectedStates.split(",")
        cities=getcityvaluesforselectedstates(selectedStates)
        cities_list = ''
        for city in cities:
            cities_list += '<option value="{}">{}</option>'.format(city, city)
    return jsonify(cities_list=cities_list)

@app.route("/ajax_cities",methods=["POST","GET"])
def ajax_cities():
    if request.method == 'POST':
        selectedCities = request.form['selectedCities']
        print(selectedCities)
        selectedCities = selectedCities.split(",")
        getaqiforcities(selectedCities)
    return jsonify(selectedCities=selectedCities)

@app.route('/test_connection')
def test_connection():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connection successful"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

@app.route('/')
def index():
    return 'Welcome to the Climate Data Application! <br><br> Visit <a href="/aqis">AQI Data</a> to see the graphs related to AQI and PM'

if __name__ == "__main__":
    app.run(debug=True)