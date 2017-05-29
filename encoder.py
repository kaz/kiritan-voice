# coding: UTF-8

import os
import re
import time
import glob
import logging
import threading
import traceback
import subprocess

# FFMPEGでファイルをMP3にエンコード
def mp3(file):
	logging.info("Encoding WAV to MP3")
	
	data = subprocess.run(
		[
			"ffmpeg",
			"-i", file, "-vn",
			"-acodec", "libmp3lame",
			"-ab", "128k",
			"-ac", "2",
			"-ar", "44100",
			"pipe:1.mp3"
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL
	)
	return data.stdout

# FFMPEGでファイルをMPEG-TSにエンコード（中身はMP3）
def ts(file):
	logging.info("Encoding WAV to MPEG-TS")
	
	data = subprocess.run(
		[
			"ffmpeg",
			"-i", file, "-vn",
			"-acodec", "libmp3lame",
			"-ab", "128k",
			"-ac", "2",
			"-ar", "44100",
			"-f", "hls",
			"-hls_time", "2",
			"-hls_list_size", "0",
			"-start_number", str(int(time.time() * 1000)),
			"-hls_segment_filename", "static/live%d.ts",
			"pipe:1.m3u8"
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL
	)
	
	# 出力されたプレイリストをパースして返す
	playlist = data.stdout.decode("utf-8")
	playlist = playlist[playlist.rfind("#EXTM3U"):]
	
	# Tuple (再生時間, ファイルパス)
	return re.findall(r"#EXTINF:([\d.]+),\s+(\S+)", playlist)

# ライブストリーミングキューに追加
que = []
def enqueue(f):
	que.append(f)

# ライブプレイリストを更新
tsl = []
seq = 0
def __livecasting():
	global seq
	
	while True:
		try:
			if len(que) != 0:
				# キューにデータがあればプレイリストに追加
				tsl.extend(ts(que.pop(0)))
			else:
				# キューが空なら無音ファイルを配信
				while len(tsl) < 3:
					tsl.append(("2.04", "silent.ts"))
			
			# TS 1つ分だけ休憩する
			time.sleep(float(tsl[0][0]))
			tsl.pop(0)
			seq += 1
		except:
			logging.error(traceback.format_exc())

# サーバ起動
def livecasting():
	# 古い配信データを削除
	for f in glob.glob("static/live*"):
		os.remove(f)
		
	threading.Thread(target=__livecasting).start()

# ライブプレイリストを生成
def playlist():
	pl = [
		"#EXTM3U",
		"#EXT-X-VERSION:3",
		"#EXT-X-TARGETDURATION:3",
		"#EXT-X-MEDIA-SEQUENCE:%d" % seq
	]
	
	for ts in tsl[:5]:
		pl.append("#EXTINF:%s," % ts[0])
		pl.append("#EXT-X-DISCONTINUITY")
		pl.append("/static/%s" % ts[1])
		
	return "\n".join(pl)
