from flask import Flask, render_template, request
from flask_socketio import SocketIO
from lib import cognitiveservices_wrapper as cg
import json

from flask import Flask 
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232'
socketio = SocketIO(app)


@app.route('/')
def index():
	# result = cg.translation_continuous()
	result = cg.translation_once_from_mic()

	# result = '{"Duration":11700000,"Offset":25500000,"RecognitionStatus":"Success","Text":"Tell me everything.","Translation":{"TranslationStatus":"Success","Translations":[{"Language":"de","Text":"Sagen Sie mir alles."},{"Language":"pt","Text":"Conte-me tudo."},{"Language":"zh-Hans","Text":"告诉我一切"}]}}'
	socketio.send(json.loads(result)['Translation']['Translations'], broadcast=True)
	return render_template('index.html')


@app.route('/translation')
def translation():
	language = request.args.get('language', default = 'de', type = str)
	return render_template('translation.html', language=language)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)

if __name__ == '__main__':
	socketio.run(app)



