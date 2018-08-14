from flask import Flask , request
import psycopg2

hostname = 'ec2-54-163-246-5.compute-1.amazonaws.com'
username = 'ccwbkzomgaturz'
password = '86103e1ac176041a672dd0ac069edeee94780fa94a49162f80b18a0cef599af8'
database = 'd9uvpss3s3f0k'

app = Flask(__name__)

myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )

cur = myConnection.cursor()

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
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		myConnection.commit()
		return "{New data}"
	else:
		print("Updating feed of " + request.json['feed'] + " to the value of " + request.json['value'])
		cur.execute("update feeds set value = %s where feed = %s;",(request.json['value'],request.json['feed']))
		myConnection.commit()
		return "{updated data}"

@app.route('/setPort', methods=['POST'])
def setPort():
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		myConnection.commit()
		return "{New data}"
	else:
		print("Updating feed of " + request.json['feed'] + " to the port of " + request.json['port'])
		cur.execute("update feeds set port = %s where feed = %s;",(request.json['port'],request.json['feed']))
		myConnection.commit()
		return "{updated data}"

@app.route('/getValue', methods=['POST'])
def getValue():
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		resp = cur.fetchall()
		myConnection.commit()
		return "{'value':'OFF'}"
	else:
		cur.execute("select value from feeds where id = " + str(resp[0][0]) + ";")
		resp = cur.fetchall()
		print("Getting feed of " + request.json['feed'] + " with the value of " + resp[0][0])
		myConnection.commit()
		return "{'value' : '" + str(resp[0][0]) + "'}"

@app.route('/getPort', methods=['POST'])
def getPort():
	cur.execute("select id from feeds where feed = '" + request.json['feed'] + "';")
	resp = cur.fetchall()
	if(resp == []):
		print("Adding new feed of " + request.json['feed'] + " to the database")
		cur.execute("insert into feeds(feed) values('" + request.json['feed'] + "');")
		resp = cur.fetchall()
		myConnection.commit()
		return "{'value':'OFF'}"
	else:
		cur.execute("select port from feeds where id = " + str(resp[0][0]) + ";")
		resp = cur.fetchall()
		print("Getting feed of " + request.json['feed'] + " with the port of " + resp[0][0])
		myConnection.commit()
		return "{'port' : '" + str(resp[0][0]) + "'}"

if __name__ == '__main__':
    app.debug = True
    app.run()