from flask import Flask , request
from Adafruit_IO import MQTTClient
import psycopg2
from datetime import datetime
from notify_run import Notify
import pytz
import requests
import json

hostname = 'ec2-54-163-246-5.compute-1.amazonaws.com'
username = 'ccwbkzomgaturz'
password = '86103e1ac176041a672dd0ac069edeee94780fa94a49162f80b18a0cef599af8'
database = 'd9uvpss3s3f0k'

ADAFRUIT_IO_KEY = 'a8ce257319334cd29630749102997271'
ADAFRUIT_IO_USERNAME = 'rajgurusmit'

FEED_ID = 'door'
FEED_ID_2 = 'update'
FEED_ID_3 = 'home'

notify = Notify(endpoint='https://notify.run/x0SrlFJiAOhrHTlW')

app = Flask(__name__)

myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )

cur = myConnection.cursor()

# home function
def home(isHome):
    home_feed_list = ['tubelight','fan','monitor1','monitor2','bias']
    value = ''
    if(isHome):
        value = 'ON'
    else:
        value = 'OFF'
    
    URL = "https://room-automation.herokuapp.com/setFeed"
    for feed in home_feed_list:
        PARAMS = {'feed':feed,'value':value}
        req = requests.post(url = URL, json = PARAMS)
        
    client.publish('activate', "True", ADAFRUIT_IO_USERNAME)
    
# Msg send on door open
def msg():
	d = datetime.now()
	print(d.strftime("%H:%M:%S - %d %b %y"))
	HerokuTime = pytz.utc
	IST = pytz.timezone("Asia/Kolkata")
	d = HerokuTime.localize(d)
	d = d.astimezone(IST)
	s = d.strftime("%H:%M:%S - %d %b %y")
	notify.send("Door Opened at " + s)


# Define callback functions which will be called when certain events happen.
def connected(client):
	# Connected function will be called when the client is connected to Adafruit IO.
	# This is a good place to subscribe to feed changes.  The client parameter
	# passed to this function is the Adafruit IO MQTT client so you can make
	# calls against it easily.
	print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID_2))
	# Subscribe to changes on a feed named DemoFeed.
	client.subscribe(FEED_ID_2)
	client.subscribe(FEED_ID)
	client.subscribe(FEED_ID_3)

def disconnected(client):
	# Disconnected function will be called when the client disconnects.
	print('Disconnected from Adafruit IO!')
	sys.exit(1)

def message(client, feed_id, payload):
	# Message function will be called when a subscribed feed has a new value.
	# The feed_id parameter identifies the feed, and the payload parameter has
	# the new value.
	if(feed_id == FEED_ID_3):
                home(payload=="True")
	if(payload == "Open"):
		if(feed_id == FEED_ID):
			msg()
		else:
			print("Feed Not Used")
		client.publish(FEED_ID, "Closed", ADAFRUIT_IO_USERNAME)
	print('Feed {0} received new value: {1}'.format(feed_id, payload))

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_background()

@app.route('/')
def rebound():
	cur.execute("select * from feeds;")
	table = "<br />id , feed , value , port<br />"
	resp = cur.fetchall()
	if(resp == []):
		return "Welcome to the Room-Automation Api.<br />The table is empty.<br />Add a feed."
	for id,feed,value,port in resp:
		table = table + str(id) + " , " + feed + " , " + value + " , " + str(port) + "<br />"
	return "Welcome to the Room-Automation Api.<br />" + table 

@app.route('/setFeed', methods=['POST'])
def setFeed():
	data = ""
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		myConnection.commit()
		data = "{\"New data\":True}"
	else:
		print("Updating feed of " + request.json['feed'] + " to the value of " + request.json['value'])
		cur.execute("update feeds set value = %s where feed = %s;",(request.json['value'],request.json['feed']))
		myConnection.commit()
		data = "{\"updated data\":True}"
	response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    	)
	return response

@app.route('/setPort', methods=['POST'])
def setPort():
	data=""
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		myConnection.commit()
		client.publish(FEED_ID_2, "True", ADAFRUIT_IO_USERNAME)
		data = "{\"New data\":True}"
	else:
		print("Updating feed of " + request.json['feed'] + " to the port of " + request.json['port'])
		cur.execute("update feeds set port = %s where feed = %s;",(request.json['port'],request.json['feed']))
		myConnection.commit()
		client.publish(FEED_ID_2, "True", ADAFRUIT_IO_USERNAME)
		data = "{\"updated data\":True}"
	response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    	)
	return response

@app.route('/getValue', methods=['POST'])
def getValue():
	data=""
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		resp = cur.fetchall()
		myConnection.commit()
		data = "{\"value\":\"OFF\"}"
	else:
		cur.execute("select value from feeds where id = " + str(resp[0][0]) + ";")
		resp = cur.fetchall()
		print("Getting feed of " + request.json['feed'] + " with the value of " + resp[0][0])
		myConnection.commit()
		data = "{\"value\" : \"" + str(resp[0][0]) + "\"}"
	response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    	)
	return response

@app.route('/getPort', methods=['POST'])
def getPort():
	data=""
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		resp = cur.fetchall()
		myConnection.commit()
		data = "{\"value\":\"OFF\"}"
	else:
		cur.execute("select port from feeds where id = " + str(resp[0][0]) + ";")
		resp = cur.fetchall()
		print("Getting feed of " + request.json['feed'] + " with the port of " + resp[0][0])
		myConnection.commit()
		data = "{\"port\" : \"" + str(resp[0][0]) + "\"}"
	response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    	)
	return response

@app.route('/get', methods=['POST'])
def get():
	data=""
	cur.execute("select * from feeds;")
	resp = cur.fetchall()
	data = {'list':resp}
	response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    	)
	return response

if __name__ == '__main__':
	app.debug = True
	app.run()
