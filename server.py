# coding: UTF-8

import flask
import encoder
import kiritan

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	return flask.render_template('index.html')

@app.route('/mp3', methods=['GET', 'POST'])
def gen_mp3():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None:
		return 'plz specify `text`'
	
	return flask.Response(
		response=encoder.mp3(kiritan.talk(text)),
		mimetype="audio/mp3"
	)
	
@app.route('/say', methods=['GET', 'POST'])
def say():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None:
		return 'plz specify `text`'
		
	encoder.enqueue(kiritan.talk(text))
	return "ok"
	
if __name__ == '__main__':
	encoder.livecasting()
	app.run(host='0.0.0.0', port=80, debug=False)
	