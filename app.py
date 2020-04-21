####This Webpage has referred to https://blog.ruanbekker.com/blog/2018/05/27/web-forms-with-python-flask-and-the-wtforms-module-with-bootstrap/
####for this and the html page

from cassandra.cluster import Cluster
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()


from random import randint
from flask import Flask, render_template, flash, request, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import requests
import time
from time import gmtime, strftime

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

breeze_key = 'a58a9d32742349de8ce48c8ef9ae588a' #breezometer api's key

class ReusableForm(Form):
    Place = TextField('Place:', validators=[validators.required()])
    

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    if request.method == 'POST':

        #Find the latitude and longitude using locationiq  
        Place = request.form['Place']    
        url = "https://us1.locationiq.com/v1/search.php"
        data = {
            'key': 'd259a898fa887a',
            'q': str(Place),
            'format': 'json'
        }

        #get latitude and longitude and store in respective variables
        resp1 = requests.get(url, params=data)
        if resp1.ok:            
            results = resp1.json()[0]
            my_latitude = results['lat']
            my_longitude = results ['lon']
            
        #The weather url
        weather_url_template = "https://api.breezometer.com/weather/v1/current-conditions?lat={latitude}&lon={longitude}&key={YOUR_API_KEY}"
        weather_url = weather_url_template.format(latitude=my_latitude, longitude= my_longitude,YOUR_API_KEY=breeze_key)

        #get the weather data and store in respective variables
        resp = requests.get(weather_url)
        if resp.ok:
            json_data = resp.json()
            Temperature = json_data['data']['temperature']['value']
            Dew = json_data['data']['dew_point']['value']
            Humidity = json_data['data']['relative_humidity']
            Wind = json_data['data']['wind']['speed']['value']
            Time = str(strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
            flash(f'At {Time}\n the weather conditions near {str(Place)} are Temperature: {str(Temperature)}\nDew: {str(Dew)} \nHumidity: {str(Humidity)} \nWind: {str(Wind)}')

            #Insert to weather.stats as per the columns present
            session.execute(f"INSERT INTO weather.stats(place, time,dew,humidity,temperature,wind) VALUES('{Place}','{Time}',{Dew},{Humidity},{Temperature},{Wind});")

        else:
            print(resp.reason)    
    return render_template('index.html', form=form)
    
@app.route("/places", methods=['GET']) #REST api GET method
def profile():
    rows = session.execute( 'Select * From weather.stats') 
    places=[]
    for row in rows:
        places.append(row.place)
    return (str(places))

@app.route('/places',  methods=['POST']) #REST api POST method
def create():
    time = str(strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    session.execute(f"INSERT INTO weather.stats(place, time,dew,humidity,temperature,wind) VALUES('{request.json['Place']}','{time}',{request.json['Dew']},{request.json['Humidity']},{request.json['Temperature']},{request.json['Wind']});")
    return jsonify({'message': 'created: /place/{}'.format(request.json['Place'])}), 201

@app.route('/places',  methods=['PUT']) #REST api PUT method
def update():
    time = str(strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    session.execute(f"UPDATE weather.stats SET time = '{time}',dew = {request.json['Dew']},humidity = {request.json['Humidity']},temperature = {request.json['Temperature']},wind = {request.json['Wind']} WHERE place = '{request.json['Place']}'")
    return jsonify({'message': 'updated: /places/{}'.format(request.json['Place'])}), 200

@app.route('/places',  methods=['DELETE']) #REST api DELETE method
def delete():
    session.execute(f"Delete FROM weather.stats WHERE place = '{request.json['Place']}'")    
    return jsonify({'message': 'deleted: /places/{}'.format(request.json['Place'])}), 200
	    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=443,ssl_context=('cert.pem', 'key.pem'))
    #app.run(host='0.0.0.0',port = 80) <--- to run without https://
