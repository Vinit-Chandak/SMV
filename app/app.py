from flask import Flask, redirect,request,render_template,jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
from flask_wtf import Form
from sqlalchemy import ForeignKey
from wtforms import DateField
from geopy.geocoders import Nominatim
import requests
import datetime
import psycopg2
from send_email import send_email
import plotly.graph_objs as go
from plotly.offline import plot
from flask import flash
from plotly.subplots import make_subplots
import geonamescache

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
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()

    city_names = [city['name'] for city in cities.values()]
    city_names = sorted(city_names)

    return render_template('base.html',city_names = city_names)


@app.route('/cities/', methods=['POST'])
def cities():
    state = request.form['state']

    cur.execute("SELECT City FROM Cities WHERE state=%s", (state,))
    cities = [row[0] for row in cur.fetchall()]
    return render_template('base_city.html', cities=cities)


@app.route('/weather/', methods=['POST'])
def weather():
    if request.method == 'POST':
        state = request.form['state']
        city = request.form['city']
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(city + ',' + state)
        latitude = location.latitude
        longitude = location.longitude
        if location:
            print("Latitude:", latitude)
            print("Longitude:", longitude)

        appid = '890d5f0a482da702345baf8788dd5e9a'
        weather_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={appid}&units=metric&alerts=true'
        response = requests.get(weather_url)
        global my_dict
        my_dict = response.json()

        timestamp1= my_dict['current']['dt']
        dt_obj1 = datetime.datetime.fromtimestamp(timestamp1)
        date_time1 = dt_obj1.strftime("%d/%m/%Y %H:%M")
        my_dict['current']['dt']=date_time1
        time_str = date_time1
        date, time = time_str.split(' ')

        timestamp2= my_dict['current']['sunrise']
        dt_obj2 = datetime.datetime.fromtimestamp(timestamp2)
        date_time2 = dt_obj2.strftime("%H:%M")
        my_dict['current']['sunrise']=date_time2

        timestamp3= my_dict['current']['sunset']
        dt_obj3 = datetime.datetime.fromtimestamp(timestamp3)
        date_time3 = dt_obj3.strftime("%H:%M")
        my_dict['current']['sunset']=date_time3
    
    return render_template('weather.html',my_dict=my_dict,date=date,time=time)

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

    # used to convert the given city and state into latitude and longitude
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
            alert_details = weather_data['alerts'][0] 
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

            flash(f"You have been registered for weather alerts.", "success")

        elif 'deregister_email' in request.form:
            # Handle deregistration
            email = request.form['deregister_email']

            # Remove data from the database
            weather_alert = WeatherAlerts.query.filter_by(email=email).first()
            if weather_alert:
                db.session.delete(weather_alert)
                db.session.commit()
                flash(f"You have been deregistered from weather alerts.", "success")
            else:
                flash(f"{email} is not registered for weather alerts.", "danger")

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
    avg_temps = db.relationship('Average_Temperature', back_populates='state_rel')
    state_co2 = db.relationship('state_co2', back_populates='state_rel')


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
    
class Sealevel(db.Model):
    __tablename__ = 'sealevel'
    state = db.Column(db.String(30), ForeignKey('states.state'), primary_key=True)
    sea_shore_city = db.Column(db.String(30), ForeignKey('cities.city'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), primary_key=True)
    linear_trend = db.Column(db.Numeric(4, 3), default=None)
    high_conf = db.Column(db.Numeric(4, 3), default=None)
    low_conf = db.Column(db.Numeric(4, 3), default=None)
    monthly_msl = db.Column(db.Numeric(4, 3), default=None)

    state_rel = db.relationship('States', backref=db.backref('sealevels', lazy=True))
    city_rel = db.relationship('Cities', backref=db.backref('sealevels', lazy=True))

    def to_dict(self):
        return {
            'state': self.state,
            'sea_shore_city': self.sea_shore_city,
            'year': self.year,
            'month': self.month,
            'linear_trend': self.linear_trend,
            'high_conf': self.high_conf,
            'low_conf': self.low_conf,
            'monthly_msl': self.monthly_msl
        }
    
class Rainfall(db.Model):
    __tablename__ = 'rainfall'
    subdivision = db.Column(db.String(50), ForeignKey('state_subdivision.subdivision'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    january = db.Column(db.Numeric(5, 1), default=None)
    february = db.Column(db.Numeric(5, 1), default=None)
    march = db.Column(db.Numeric(5, 1), default=None)
    april = db.Column(db.Numeric(5, 1), default=None)
    may = db.Column(db.Numeric(5, 1), default=None)
    june = db.Column(db.Numeric(5, 1), default=None)
    july = db.Column(db.Numeric(5, 1), default=None)
    august = db.Column(db.Numeric(5, 1), default=None)
    september = db.Column(db.Numeric(5, 1), default=None)
    october = db.Column(db.Numeric(5, 1), default=None)
    november = db.Column(db.Numeric(5, 1), default=None)
    december = db.Column(db.Numeric(5, 1), default=None)
    annual = db.Column(db.Numeric(5, 1), default=None)
    january_february = db.Column(db.Numeric(5, 1), default=None)
    march_may = db.Column(db.Numeric(5, 1), default=None)
    june_september = db.Column(db.Numeric(5, 1), default=None)
    october_december = db.Column(db.Numeric(5, 1), default=None)

    def to_dict(self):
        return {
            'subdivision': self.subdivision,
            'year': self.year,
            'january': self.january,
            'february': self.february,
            'march': self.march,
            'april': self.april,
            'may': self.may,
            'june': self.june,
            'july': self.july,
            'august': self.august,
            'september': self.september,
            'october': self.october,
            'november': self.november,
            'december': self.december,            
            'annual': self.annual,
            'january_february': self.january_february,
            'march_may': self.march_may,
            'june_september': self.june_september,
            'october_december': self.october_december
        }    

#AQI
def get_state_values_aqi():
    AQIstates = db.session.query(AQI.state.distinct().label("state")).all()
    result = []
    for row in AQIstates:
        result.append(row.state)     
    return result

def get_city_values_for_selected_states_aqi(selectedStateArray):
    cities = db.session.query(AQI.city.distinct().label("city")).filter(AQI.state.in_(selectedStateArray)).all()
    result = []
    for city in cities:
        result.append(city.city)     
    return result

def get_aqi_for_cities_in_given_date_range():
    aqis = AQI.query.filter(AQI.city.in_(session.get('selectedCities')), AQI.date >= session.get('startDate'), AQI.date <= session.get('endDate'))
    result = []
    for aqi in aqis:
        if(aqi != None):
            result.append(aqi.to_dict())                  
    return result

@app.route('/aqis')
def aqi_data():
    form = DateForm()
    states = get_state_values_aqi()
    return render_template('index.html', all_states=states,form=form)

@app.route("/ajax_states",methods=["POST","GET"])
def ajax_states():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        #print(selectedStates)
        selectedStates = selectedStates.split(",")
        cities=get_city_values_for_selected_states_aqi(selectedStates)
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
        result = get_aqi_for_cities_in_given_date_range()
        data = pd.DataFrame.from_records(result)
        if('aqi' in metrics):
            figaqi = px.line(result, x='date', y='aqi', color='city', hover_data=['aqi_bucket'])
            figaqi.update_traces(mode='markers+lines')
            figaqi.show()
        if('pm10' in metrics):
            figpm10 = px.line(result, x='date', y='pm10', color='city', hover_data=['aqi_bucket'])
            figpm10.update_traces(mode='markers+lines')
            figpm10.show()
        if('pm2_5' in metrics):
            fig2_5 = px.line(result, x='date', y='pm2_5', color='city', hover_data=['aqi_bucket'])
            fig2_5.update_traces(mode='markers+lines')
            fig2_5.show() 
    return jsonify(metrics=metrics)

#SeaLevel
def get_state_values_sealevel():
    SLstates = db.session.query(Sealevel.state.distinct().label("state")).all()
    result = []
    for row in SLstates:
        result.append(row.state)     
    return result

def get_city_values_for_selected_states_sealevel(selectedStateArray):
    cities = db.session.query(Sealevel.sea_shore_city.distinct().label("city")).filter(Sealevel.state.in_(selectedStateArray)).all()
    result = []
    for city in cities:
        result.append(city.city)     
    return result

def getyearsfromselectedcities(selectedCityArray):
    sealevels = Sealevel.query.filter(Sealevel.sea_shore_city.in_(selectedCityArray))
    result = []
    for sealevel in sealevels:
        if(sealevel.year.__str__() not in result):
            result.append(sealevel.year.__str__()) 
    result.sort()  
    return result

def get_sealevel_for_cities_for_given_year_month(years, months):    
    sealevels = Sealevel.query.filter(Sealevel.sea_shore_city.in_(session.get('selectedCities')), Sealevel.year.in_(years), Sealevel.month.in_(months))
    result = []
    for sealevel in sealevels:
        if(sealevel != None):
            result.append(sealevel.to_dict())                  
    return result

@app.route('/sealevel')
def sealevel_data():
    form = DateForm()
    states = get_state_values_sealevel()
    return render_template('sealevel.html',
                       all_states=states,form=form)

@app.route("/ajax_states_sealevel",methods=["POST","GET"])
def ajax_states_sealevel():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        #print(selectedStates)
        selectedStates = selectedStates.split(",")
        cities=get_city_values_for_selected_states_sealevel(selectedStates)
        cities_list = ''
        for city in cities:
            cities_list += '<option value="{}">{}</option>'.format(city, city)
    return jsonify(cities_list=cities_list)

@app.route("/ajax_cities_sealevel",methods=["POST","GET"])
def ajax_cities_sealevel():
    if request.method == 'POST':
        selectedCities = request.form['selectedCities']
        print(selectedCities)
        selectedCities = selectedCities.split(",")
        session['selectedCities'] = selectedCities
        years = getyearsfromselectedcities(selectedCities)
        years_list = ''
        for year in years:
            years_list += '<option value="{}">{}</option>'.format(year, year)
    return jsonify(years_list=years_list)

@app.route("/ajax_years_sealevel",methods=["POST","GET"])
def ajax_years_sealevel():
    if request.method == 'POST':
        years = request.form['selectedYears']
        years = years.split(",")
        months = request.form['selectedMonths']
        months = months.split(",")
        result = get_sealevel_for_cities_for_given_year_month(years, months)
        data = pd.DataFrame.from_records(result)
        data["monthly_msl"] = pd.to_numeric(data["monthly_msl"], downcast="float")
        if len(years) > 1:
            data = data.groupby(['year','sea_shore_city'])['monthly_msl'].mean().reset_index()
            x_column = 'year'
        else:
            x_column = 'month'

        figaqi = px.line(data, x=x_column, y='monthly_msl', color='sea_shore_city')
        figaqi.show()
    return jsonify(years=years)


#rainfall
def get_state_values_rainfall():
    Rstates = db.session.query(Rainfall.subdivision.distinct().label("state")).all()
    result = []
    for row in Rstates:
        result.append(row.state)     
    return result

def get_subdivision_values_for_selected_states_rainfall(selectedStateArray):
    subdivisions = db.session.query(Rainfall.subdivision.distinct().label("subdivision")).filter(Rainfall.subdivision.in_(selectedStateArray)).all()
    result = []
    for subdivision in subdivisions:
        result.append(subdivision.subdivision)     
    return result

def getyearsfromselectedsubdivisions(selectedSubdivisionArray):
    rainfalls = Rainfall.query.filter(Rainfall.subdivision.in_(selectedSubdivisionArray))
    result = []
    for rainfall in rainfalls:
        if(rainfall.year.__str__() not in result):
            result.append(rainfall.year.__str__())     
    return result

def get_rainfall_for_subdivisions_for_given_year(years):    
    rainfalls = Rainfall.query.filter(Rainfall.subdivision.in_(session.get('selectedSubdivisions')), Rainfall.year.in_(years))
    result = []
    for rainfall in rainfalls:
        if(rainfall != None):
            result.append(rainfall.to_dict())                  
    return result


@app.route('/rainfall')
def rainfall_data():
    form = DateForm()
    states = get_state_values_rainfall()
    return render_template('rainfall.html',
                       all_states=states,form=form)

@app.route("/ajax_states_rainfall",methods=["POST","GET"])
def ajax_states_rainfall():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        #print(selectedStates)
        selectedStates = selectedStates.split(",")
        subdivisions=get_subdivision_values_for_selected_states_rainfall(selectedStates)
        subdivisions_list = ''
        for subdivision in subdivisions:
            subdivisions_list += '<option value="{}">{}</option>'.format(subdivision, subdivision)
            print(subdivision)
    return jsonify(subdivisions_list=subdivisions_list)

@app.route("/ajax_subdivisions_rainfall",methods=["POST","GET"])
def ajax_subdivisions_rainfall():
    if request.method == 'POST':
        selectedSubdivisions = request.form['selectedSubdivisions']
        print(selectedSubdivisions)
        selectedSubdivisions = selectedSubdivisions.split(",")
        session['selectedSubdivisions'] = selectedSubdivisions
        years = getyearsfromselectedsubdivisions(selectedSubdivisions)
        years_list = ''
        for year in years:
            years_list += '<option value="{}">{}</option>'.format(year, year)
    return jsonify(years_list=years_list)

@app.route("/ajax_years_rainfall",methods=["POST","GET"])
def ajax_years_rainfall():
    if request.method == 'POST':
        years = request.form['selectedYears']
        years = years.split(",")
        months = request.form['months']
        result = get_rainfall_for_subdivisions_for_given_year(years)
        data = pd.DataFrame.from_records(result)
        figaqi = px.line(data, x='year', y=months, color='subdivision')
        figaqi.show()
    return jsonify(years=years)


#Average Temperature
class Average_Temperature(db.Model):
    __tablename__ = 'average_temperature'
    state = db.Column(db.String, db.ForeignKey('states.state'), primary_key=True)
    month = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    average_temperature = db.Column(db.Float)
    average_temperature_uncertainty = db.Column(db.Float)
    state_rel = db.relationship('States', back_populates='avg_temps')

    def to_dict(self):
        return {
            'state': self.state,
            'month': self.month,
            'year': self.year,
            'average_temperature': self.average_temperature,
            'average_temperature_uncertainty': self.average_temperature_uncertainty
        }

def get_state_values_avg_temp():
    avg_temp_states = db.session.query(Average_Temperature.state.distinct().label("state")).all()
    result = []
    for row in avg_temp_states:
        result.append(row.state)     
    return result

def get_year_values_for_selected_states_avg_temp(selectedStatesArray):
    years = db.session.query(Average_Temperature.year.distinct().label("year")).filter(Average_Temperature.state.in_(selectedStatesArray)).all()
    result = []
    for year in years:
        result.append(year.year)  
    result.sort()   
    return result

def get_month_values_for_selected_states_and_years_avg_temp(selectedYearsArray):
    if 'all' in selectedYearsArray:
        months = db.session.query(Average_Temperature.month.distinct().label("month")).all()
    else:
        months = db.session.query(Average_Temperature.month.distinct().label("month")).filter(Average_Temperature.year.in_(selectedYearsArray)).all()
    result = []
    month_name_to_number = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    for month in months:
        result.append(month.month)
    result.sort(key=lambda month: month_name_to_number[month])
    return result


def get_avg_temp_for_states_in_given_year_and_month():
    if "all" in session.get('selectedYears'):
        session['selectedYears'] = get_year_values_for_selected_states_avg_temp(session.get('selectedStates'))

    avg_temps = Average_Temperature.query.filter(Average_Temperature.state.in_(session.get('selectedStates')), Average_Temperature.year.in_(session.get('selectedYears')), Average_Temperature.month.in_(session.get('selectedMonths')))
    result = []
    for avg_temp in avg_temps:
        if(avg_temp != None):
            result.append(avg_temp.to_dict())                  
    return result

@app.route('/temperature')
def avg_temp_data():
    form = DateForm()
    states = get_state_values_avg_temp()
    return render_template('avg_temp.html', all_states=states)

@app.route("/ajax_states_avg_temp",methods=["POST","GET"])
def ajax_states_avg_temp():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        #print(selectedStates)
        selectedStates = selectedStates.split(",")
        years=get_year_values_for_selected_states_avg_temp(selectedStates)
        years_list = ''
        session['selectedStates'] = selectedStates
        for year in years:
            years_list += '<option value="{}">{}</option>'.format(year, year)
    return jsonify(years_list=years_list)

@app.route("/ajax_years_avg_temp",methods=["POST","GET"])
def ajax_years_avg_temp():
    if request.method == 'POST':
        selectedYears = request.form['selectedYears']
        #print(selectedYears)
        selectedYears = selectedYears.split(",")
        months=get_month_values_for_selected_states_and_years_avg_temp(selectedYears)
        months_list = ''
        session['selectedYears'] = selectedYears
        limit_month_dropdown = 'all' in selectedYears or len(selectedYears) > 1

        for month in months:
            months_list += '<option value="{}">{}</option>'.format(month, month)
    return jsonify(months_list=months_list, limit_month_dropdown=limit_month_dropdown)

import plotly.graph_objs as go
import plotly.offline


@app.route("/ajax_plot_avg_temp", methods=["POST", "GET"])
def ajax_metrics_avg_temp():
    if request.method == 'POST':
        selectedMonths = request.form['selectedMonths']
        selectedMonths = selectedMonths.split(",")
        session['selectedMonths'] = selectedMonths
        
        if 'all' in selectedMonths:
            months = get_month_values_for_selected_states_and_years_avg_temp(session.get('selectedYears'))
            session['selectedMonths'] = months
        
        result = get_avg_temp_for_states_in_given_year_and_month()
        data = pd.DataFrame.from_records(result)

        # if the user has selected more than two years, group the data by year and calculate the mean temperature for each year
        if len(session['selectedYears']) > 1:
            data = data.groupby(['year','state'])[['average_temperature', 'average_temperature_uncertainty']].mean().reset_index()
            print(data)
            x_column = 'year'
        else:
            print(data)
            x_column = 'month'
        
        figtemp = px.line(data, x=x_column, y='average_temperature', color='state', hover_data=['average_temperature_uncertainty'])
        figtemp.update_traces(mode='markers+lines')
        figtemp.show()
    return jsonify(selectedMonths=selectedMonths)


#State CO2
class state_co2(db.Model):
    __tablename__ = 'state_co2'
    state = db.Column(db.String(30),db.ForeignKey('states.state'), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    co2_emissions = db.Column(db.Numeric(10,2))
    state_rel = db.relationship('States', back_populates='state_co2')
    def to_dict(self):
        return {
            'state': self.state,
            'year': self.year,
            'co2_emissions': self.co2_emissions
        }

def get_state_values_state_co2():
    co2_states = db.session.query(state_co2.state.distinct().label("state")).all()
    result = []
    for row in co2_states:
        result.append(row.state)     
    #print(result)
    return result

def get_year_values_for_selected_states_state_co2(selectedStatesArray):
    years = db.session.query(state_co2.year.distinct().label("year")).filter(state_co2.state.in_(selectedStatesArray)).all()
    result = []
    for year in years:
        result.append(year.year)
    result.sort()
    return result

def get_co2_for_states_in_given_year_state_co2():
    co2_emissions = state_co2.query.filter(state_co2.state.in_(session.get('selectedStates')), state_co2.year.in_(session.get('selectedYears')))
    result = []
    for co2_emission in co2_emissions:
        if(co2_emission != None):
            result.append(co2_emission.to_dict())                  
    return result

@app.route('/state_co2')
def co2_data():
    states = get_state_values_state_co2()
    return render_template('state_co2.html', all_states=states)

@app.route("/ajax_states_state_co2",methods=["POST","GET"])
def ajax_states_state_co2():
    if request.method == 'POST':
        selectedStates = request.form['selectedStates']
        selectedStates = selectedStates.split(",")
        #print(selectedStates)
        years=get_year_values_for_selected_states_state_co2(selectedStates)
        #print(years)
        years_list = ''
        session['selectedStates'] = selectedStates
        for year in years:
            years_list += '<option value="{}">{}</option>'.format(year, year)
    return jsonify(years_list=years_list)

@app.route("/ajax_plot_state_co2",methods=["POST","GET"])
def ajax_years_state_co2():
    if request.method == 'POST':
        selectedYears = request.form['selectedYears']
        #print(selectedYears)
        selectedYears = selectedYears.split(",")
        if 'all' in selectedYears:
            years = get_year_values_for_selected_states_state_co2(session.get('selectedStates'))
            session['selectedYears'] = years
        else:
            session['selectedYears'] = selectedYears
        result = get_co2_for_states_in_given_year_state_co2()
        data = pd.DataFrame.from_records(result)
        #print(data)
        figco2 = px.line(data, x='year', y='co2_emissions', color='state')
        figco2.update_traces(mode='markers+lines')
        figco2.show()
    return jsonify(selectedYears=selectedYears)


#India CO2
class co2(db.Model):
    __tablename__ = 'co2'
    year = db.Column(db.Integer, primary_key=True)
    population = db.Column(db.Numeric(10))
    gdp = db.Column(db.Numeric(14))
    cement_co2_per_capita = db.Column(db.Numeric(10,3))
    co2_including_luc_per_capita = db.Column(db.Numeric(10,3))
    co2_per_capita = db.Column(db.Numeric(10,3))
    coal_co2_per_capita = db.Column(db.Numeric(10,3))
    consumption_co2_per_capita = db.Column(db.Numeric(10,3))
    energy_per_capita = db.Column(db.Numeric(10,3))
    flaring_co2_per_capita = db.Column(db.Numeric(10,3))
    gas_co2_per_capita = db.Column(db.Numeric(10,3))
    ghg_excluding_lucf_per_capita = db.Column(db.Numeric(10,3))
    ghg_per_capita = db.Column(db.Numeric(10,3))
    land_use_change_co2_per_capita = db.Column(db.Numeric(10,3))
    def to_dict(self):
        return {
            'year': self.year,
            'population': self.population,
            'gdp': self.gdp,
            'cement_co2_per_capita': self.cement_co2_per_capita,
            'co2_including_luc_per_capita': self.co2_including_luc_per_capita,
            'co2_per_capita': self.co2_per_capita,
            'coal_co2_per_capita': self.coal_co2_per_capita,
            'consumption_co2_per_capita': self.consumption_co2_per_capita,
            'energy_per_capita': self.energy_per_capita,
            'flaring_co2_per_capita': self.flaring_co2_per_capita,
            'gas_co2_per_capita': self.gas_co2_per_capita,
            'ghg_excluding_lucf_per_capita': self.ghg_excluding_lucf_per_capita,
            'ghg_per_capita': self.ghg_per_capita,
            'land_use_change_co2_per_capita': self.land_use_change_co2_per_capita
        }

def get_co2_data():
    co2_emissions = co2.query.all()
    print(co2_emissions)
    result = []
    for co2_emission in co2_emissions:
        if(co2_emission != None):
            emission_dict = co2_emission.to_dict()
            emission_dict['population'] = float(emission_dict['population'])
            result.append(emission_dict)
    return result

@app.route("/co2_animation")
def co2_animation():
    co2_data = get_co2_data()
    df = pd.DataFrame.from_records(co2_data)
    df['population'] = df['population'].to_numpy()
    print(df['population'].describe())
    
    # create a line plot with hover data
    fig = px.line(df, x="year", y="co2_per_capita", hover_data=df.columns)
    
    # update layout
    fig.update_layout(
        title='Per-capita CO2 Emissions in India',
        height=800,
        yaxis=dict(title='CO2 Per Capita'),
        xaxis=dict(title='Year'),
        autosize=True
    )

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render_template('india_co2.html', plot_div=plot_div)


#corelation 
def avg_temp_state_co2_for_states_in_given_year():
    co2_emissions = state_co2.query.filter(state_co2.state.in_(session.get('selectedStates')), state_co2.year.in_(session.get('selectedYears')))
    result = []
    for co2_emission in co2_emissions:
        if(co2_emission != None):
            result.append(co2_emission.to_dict())   
    data1 = pd.DataFrame.from_records(result)
    print("Columns in data1: ", data1.columns)
    avg_temp = Average_Temperature.query.filter(Average_Temperature.state.in_(session.get('selectedStates')), Average_Temperature.year.in_(session.get('selectedYears')))
    result = []
    for temp in avg_temp:
        if(temp != None):
            result.append(temp.to_dict())
    data = pd.DataFrame.from_records(result)
    print("Columns in data: ", data.columns)
    data = data.groupby(['year','state'])[['average_temperature', 'average_temperature_uncertainty']].mean().reset_index()
    # Merge dataframes on state and year
    df = data1.merge(data, on=['state', 'year'])
    return df

@app.route("/state_co2_temp")
def state_co2_temp():
    states = get_state_values_state_co2()
    return render_template('statecotempcorrelation.html', all_states=states)

@app.route("/ajax_plot_state_co2_avg_temp", methods=["POST", "GET"])
def ajax_plot_state_co2_avg_temp():
    if request.method == 'POST':
        selectedYears = request.form['selectedYears']
        selectedYears = selectedYears.split(",")
        if 'all' in selectedYears:
            years = get_year_values_for_selected_states_state_co2(session.get('selectedStates'))
            session['selectedYears'] = years
        else:
            session['selectedYears'] = selectedYears
        df = avg_temp_state_co2_for_states_in_given_year()
        print(df)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        states = df['state'].unique()
        for state in states:
            df_state = df[df['state'] == state]
            fig.add_trace(
                go.Scatter(x=df_state['year'], y=df_state['co2_emissions'], mode='lines+markers', name=f'{state} CO2 Emissions'),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=df_state['year'], y=df_state['average_temperature'], mode='lines+markers', name=f'{state} Average Temperature'),
                secondary_y=True,
            )
        fig.update_layout(
            title_text='CO2 Emissions vs Average Temperature',
            xaxis_title='Year',
            yaxis_title='CO2 Emissions',
            yaxis2_title='Average Temperature',
        )
        fig.show()

    return jsonify(df=df.to_dict(orient='records'))

@app.route('/')
def index():
    send_weather_alerts()
    return render_template('landingpage.html')
    
if __name__ == "__main__":
    app.run(debug=True)