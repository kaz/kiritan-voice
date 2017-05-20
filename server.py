# coding: UTF-8

import flask
import subprocess

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None:
		return 'plz specify `text`'
		
	completed = subprocess.run(
		['python', 'talk.py', text],
		encoding='ascii',
		stdout=subprocess.PIPE,
		timeout=30
	)
	
	return flask.send_from_directory('./', completed.stdout.strip())
	
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)
