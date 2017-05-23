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
			"-ar", "44100"
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
			"-hls_start_number_source", "epoch",
			"-hls_segment_filename", "static/live_%d.ts",
			"-hls_flags", "omit_endlist",
			"-hls_playlist_type", "event",
			"static/live.m3u8"
		],
		stderr=subprocess.PIPE
	)
	match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2}),", data.stderr.decode("utf-8"))
	return 3600 * int(match.group(1)) + 60 * int(match.group(2)) + int(match.group(3)) + 0.01 * int(match.group(4))
	
def padding():
	duration = 2.04
	playlist = """
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:1
#EXT-X-MEDIA-SEQUENCE:%d
#EXT-X-PLAYLIST-TYPE:EVENT
#EXTINF:%f,
silent.ts
	""" % (time.time(), duration)
	
	with open("static/live.m3u8", "w") as file:
		file.write(playlist.strip())
	
	return duration

que = []
def enqueue(f):
	que.append(f)
	
def __livecasting():
	while True:
		if len(que) == 0:
			t = padding()
		else:
			t = ts(que.pop(0))
		
		time.sleep(max(2, t))
	
def livecasting():
	for f in glob.glob("static/live_*.ts"):
		os.remove(f)
		
	threading.Thread(target=__livecasting).start()
	