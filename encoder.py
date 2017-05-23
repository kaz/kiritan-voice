# coding: UTF-8

import os
import re
import time
import glob
import threading
import subprocess

def mp3(file):
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
		stdout=subprocess.PIPE
	)
	return data.stdout

def ts(file):
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
			"-hls_start_number_source", "epoch",
			"-hls_segment_filename", "static/live_%d.ts",
			"pipe:1.m3u8"
		],
		stdout=subprocess.PIPE
	)
	
	playlist = data.stdout.decode("utf-8")
	playlist = playlist[playlist.rfind("#EXTM3U"):]
	
	return re.findall(r"#EXTINF:([\d.]+),\s+(\S+)", playlist)

que = []
def enqueue(f):
	que.append(f)

tsl = []
seq = 0
def __livecasting():
	global seq
	
	while True:
		if len(que) != 0:
			tsl.extend(ts(que.pop(0)))
		else:
			while len(tsl) < 3:
				tsl.append(("2.04", "silent.ts"))
		
		time.sleep(float(tsl[0][0]))
		tsl.pop(0)
		seq += 1
	
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
	
def livecasting():
	for f in glob.glob("static/live_*.ts"):
		os.remove(f)
		
	threading.Thread(target=__livecasting).start()
	