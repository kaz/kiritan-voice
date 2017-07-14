# coding: UTF-8

import flask
import logging

import encoder
import kiritan
import twitter

app = flask.Flask(__name__)

# ログ設定
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s: %(message)s',
	datefmt='%Y/%m/%d %H:%M:%S'
)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# いろいろ起動
logging.info("Starting livecasting server")
encoder.livecasting()
logging.info("Starting twitter streaming listener")
twitter.listen()

# Webインタフェース
@app.route('/', methods=['GET'])
def index():
	return flask.render_template('index.html')

def get_input_text():
	r = flask.request
	text = r.form['text'] if r.method == "POST" else r.args.get('text', None)
	
	if text == None or text.strip() == "":
		raise '`text` is empty!'
	
	return text

# WAV形式で音声ファイル出力
@app.route('/say.wav', methods=['GET', 'POST'])
def gen_wav():
	return flask.send_file(kiritan.talk(get_input_text()))

# MP3形式で音声ファイル出力
@app.route('/say.mp3', methods=['GET', 'POST'])
def gen_mp3():
	return flask.Response(
		response=encoder.mp3(kiritan.talk(get_input_text())),
		mimetype="audio/mp3",
		headers={"Access-Control-Allow-Origin": "*"}
	)

# HLSプレイヤーを出力
@app.route('/listen', methods=['GET'])
def listen():
	return flask.render_template('hls.html')

# ライブ配信へキューを投げる
@app.route('/say', methods=['GET', 'POST'])
def say():
	encoder.enqueue(kiritan.talk(get_input_text()))
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
	logging.info("Starting HTTP server")
	app.run(host='0.0.0.0', port=8000, debug=False)
