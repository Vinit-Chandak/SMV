from flask import Flask, redirect,request,render_template,jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
from flask_wtf import Form
from wtforms import DateField
from geopy.geocoders import Nominatim
import requests
import datetime
import psycopg2

from send_email import send_email

# Init App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

username = "group_13"
password = "QcNtcHm7Hmqg9q"
dbname = "group_13"
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@10.17.50.91:5432/{dbname}"

my_dict={5:2,7:6}
def emptyDic(data):
    mydict={}
    mydict=data
    return mydict

def get_db_connection():
    conn =  psycopg2.connect(
        host="10.17.50.91",
        port="5432",
        database="group_13",
        user="group_13",
        password="QcNtcHm7Hmqg9q"
    )
    return conn

try:
    conn = get_db_connection()
    print("Connection to the database established successfully!")
except:
    print("Error: Unable to establish a connection to the database.")

cur=conn.cursor()





#Weather Forecast
@app.route('/weatherstart')
def weatherstart():
    cur.execute("SELECT * from States;")
    Average_Temperature=[row[0] for row in cur.fetchall()]
    return render_template('base.html',Average_Temperature = Average_Temperature)


@app.route('/cities/', methods=['POST'])
def cities():
    state = request.form['state']
    cur.execute("SELECT City FROM Cities WHERE state=%s", (state,))
    cities = [row[0] for row in cur.fetchall()]
    return render_template('base_city.html', cities=cities)


@app.route('/weather/', methods=['POST'])
def weather():
    city = request.form['cities']
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(city)
    latitude = location.latitude
    longitude = location.longitude
    print("Latitude:", latitude)
    print("Longitude:", longitude)

    appid = '890d5f0a482da702345baf8788dd5e9a'
    weather_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={appid}&units=metric'
    response = requests.get(weather_url)
    global my_dict
    my_dict = response.json()
    print(my_dict)
    timestamp1= my_dict['current']['dt']
    dt_obj1 = datetime.datetime.fromtimestamp(timestamp1)
    date_time1 = dt_obj1.strftime("%d/%m/%Y %H:%M")
    my_dict['current']['dt']=date_time1

    timestamp2= my_dict['current']['sunrise']
    dt_obj2 = datetime.datetime.fromtimestamp(timestamp2)
    date_time2 = dt_obj2.strftime("%H:%M")
    my_dict['current']['sunrise']=date_time2

    timestamp3= my_dict['current']['sunset']
    dt_obj3 = datetime.datetime.fromtimestamp(timestamp3)
    date_time3 = dt_obj3.strftime("%H:%M")
    my_dict['current']['sunset']=date_time3
    
    return render_template('weather.html',my_dict=my_dict)

@app.route('/final/', methods=['POST'])
def final():
    final = request.form['weather']
    d=dict(my_dict)
    if final == 'daily':
        for y in my_dict['daily']:
            timestamp= y['dt']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            date_string = dt_object.strftime('%d/%m/%Y')
            y['dt'] = date_string

            timestamp1= y['sunrise']
            dt_object1 = datetime.datetime.fromtimestamp(timestamp1)
            date_string1 = dt_object1.strftime('%m/%Y')
            y['sunrise'] = date_string1

            timestamp2= y['sunset']
            dt_object2 = datetime.datetime.fromtimestamp(timestamp2)
            date_string2 = dt_object2.strftime('%m/%Y')
            y['sunset'] = date_string2
        return render_template('daily.html',my_dict=my_dict)
    
    if final == 'minutely':
        for y in my_dict['minutely']:
            timestamp= y['dt']
            dt_obj = datetime.datetime.fromtimestamp(timestamp)
            date_time = dt_obj.strftime("%d/%m/%Y %H:%M")
            y['dt']=date_time
        return render_template('minutely.html',my_dict=my_dict)
    
    if final == 'hourly':
        for y in my_dict['hourly']:
            timestamp= y['dt']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            formatted_date = dt_object.strftime("%d/%m/%Y %H")
            y['dt']=formatted_date
        return render_template('hourly.html',my_dict=my_dict)



db = SQLAlchemy(app)


#Weather Alerts
class WeatherAlerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    state = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(30), nullable=False)


OPENWEATHERMAP_API_KEY = "890d5f0a482da702345baf8788dd5e9a"

def fetch_weather_data(city, state):

    geocode_url = "https://api.openweathermap.org/geo/1.0/direct"
    location = f"{city},{state}"
    paramsgeo = {
        'q': location,
        'appid': OPENWEATHERMAP_API_KEY
    }
    responsegeo = requests.get(geocode_url, params=paramsgeo)
    geodata = responsegeo.json()
    base_url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': geodata[0]['lat'],
        'lon': geodata[0]['lon'],    
        'appid': OPENWEATHERMAP_API_KEY,
        'exclude': 'current,minutely,hourly,daily',
    }
    response = requests.get(base_url, params=params)
    return response.json()

def is_weather_alert(weather_data):
    return 'alerts' in weather_data

def send_weather_alerts():
    weather_alerts = WeatherAlerts.query.all()

    for alert in weather_alerts:
        weather_data = fetch_weather_data(alert.city, alert.state)

        if is_weather_alert(weather_data):
            alert_details = weather_data['alerts'][0]  # Assuming there's only one alert
            alert_subject = f"Weather Alert: {alert_details['event']}"
            alert_body = f"There is a weather alert in {alert.city}, {alert.state}.\n\nEvent: {alert_details['event']}\nDescription: {alert_details['description']}"
            send_email(alert_subject, alert_body, alert.email)


@app.route('/weather_alerts', methods=['GET', 'POST'])
def weather_alerts():
    if request.method == 'POST':
        if 'email' in request.form:
            # Handle registration
            name = request.form['name']
            email = request.form['email']
            state = request.form['state']
            city = request.form['city']

            # Insert data into the database
            weather_alert = WeatherAlerts(name=name, email=email, state=state, city=city)
            db.session.add(weather_alert)
            db.session.commit()

        elif 'deregister_email' in request.form:
            # Handle deregistration
            email = request.form['deregister_email']

            # Remove data from the database
            weather_alert = WeatherAlerts.query.filter_by(email=email).first()
            if weather_alert:
                db.session.delete(weather_alert)
                db.session.commit()

        return redirect(url_for('weather_alerts'))

    return render_template('weather_alerts.html')



#AQI, PM2_5, PM10
class DateForm(Form):
    startdate = DateField('Pick a Date', format="%m/%d/%Y")
    enddate = DateField('Pick a Date', format="%m/%d/%Y")

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

def getaqiforcitiesingivendaterange():
    aqis = AQI.query.filter(AQI.city.in_(session.get('selectedCities')), AQI.date >= session.get('startDate'), AQI.date <= session.get('endDate'))
    result = []
    for aqi in aqis:
        if(aqi != None):
            result.append(aqi.to_dict())                  
    return result

@app.route('/stateslist')
def list_states():
    print("Entering /states route")
    states = States.query.all()
    print(f"Fetched {len(states)} states from the database")
    result = ""
    for state in states:
        result += f"{state.state} - {state.capital}<br>"
    return result

@app.route('/citieslist')
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
    form = DateForm()
    states = getstatevalues()
    return render_template('index.html',
                       all_states=states,form=form)

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
        session['selectedCities'] = selectedCities
    return jsonify(selectedCities=selectedCities)

@app.route("/ajax_dates",methods=["POST","GET"])
def ajax_dates():
    if request.method == 'POST':
        startDate = request.form['startdate']
        session['startDate'] = startDate
        endDate =  request.form['enddate']
        session['endDate'] = endDate
    return jsonify(startDate=startDate)

@app.route("/ajax_metrics",methods=["POST","GET"])
def ajax_metrics():
    if request.method == 'POST':
        metrics = request.form['selectedMetrics']
        metrics = metrics.split(",")
        result = getaqiforcitiesingivendaterange()
        data = pd.DataFrame.from_records(result)
        if('aqi' in metrics):
            figaqi = px.line(result, x='date', y='aqi', color='city')
            figaqi.show()
        if('pm10' in metrics):
            figpm10 = px.line(result, x='date', y='pm10', color='city')
            figpm10.show()
        if('pm2_5' in metrics):
            fig2_5 = px.line(result, x='date', y='pm2_5', color='city')
            fig2_5.show() 
    return jsonify(metrics=metrics)

from datetime import datetime as dt

def format_datetime(value, output_format='%Y-%m-%d %H:%M:%S'):
    input_formats = ['%d/%m/%Y %H:%M', '%H:%M']
    for input_format in input_formats:
        try:
            return dt.strptime(value, input_format).strftime(output_format)
        except ValueError:
            pass
    raise ValueError(f"Unable to parse timestamp '{value}'")

app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def index():
    send_weather_alerts()
    return render_template('landingpage.html')
    
if __name__ == "__main__":
    app.run(debug=True)