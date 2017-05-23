# coding: UTF-8

import flask
import encoder
import kiritan
import twitter
import logging

app = flask.Flask(__name__)

# HLSプレイヤーを出力
@app.route('/', methods=['GET'])
def index():
	return flask.render_template('index.html')

# MP3形式で音声ファイル出力
@app.route('/say.mp3', methods=['GET', 'POST'])
def gen_mp3():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None:
		return 'plz specify `text`'
	
	return flask.Response(
		response=encoder.mp3(kiritan.talk(text)),
		mimetype="audio/mp3"
	)

# ライブ配信へキューを投げる
@app.route('/say', methods=['GET', 'POST'])
def say():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None:
		return 'plz specify `text`'
		
	encoder.enqueue(kiritan.talk(text))
	return "ok"
	
# ライブ配信プレイリスト
@app.route('/live.m3u8', methods=['GET', 'POST'])
def live():
	return flask.Response(
		response=encoder.playlist(),
		mimetype="application/x-mpegURL"
	)
	
# 起動
if __name__ == '__main__':
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s: %(message)s',
		datefmt='%Y/%m/%d %H:%M:%S'
	)
	
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)
	
	logging.info("Starting livecasting server")
	encoder.livecasting()
	logging.info("Starting twitter streaming listener")
	twitter.listen()
	logging.info("Starting HTTP server")
	app.run(host='0.0.0.0', port=80, debug=False)
	