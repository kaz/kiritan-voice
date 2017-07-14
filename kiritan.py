# coding: UTF-8

import os
import sys
import time
import hashlib
import logging
import threading
import subprocess

from win32con import *
from win32gui import *
from win32process import *

# 共通設定
waitSec = 0.1
windowName = "VOICEROID＋ 東北きりたん EX"

# WAV生成(排他)
lock = threading.Lock()
def talk(input):
	with lock:
		return generate_wav(input)

# 子ウィンドウの検索
def enum_child_windows(window):
	result = []
	
	def callback(hwnd, param):
		result.append((hwnd, GetClassName(hwnd), GetWindowText(hwnd)))
	
	EnumChildWindows(window, callback, None)
	return result

# VOICELOIDを操作してWAV生成
def generate_wav(inputText):
	# 空文字列は拒否
	inputText = inputText.strip()
	if inputText == "":
		return None
	
	# 出力先ディレクトリ作成
	outdir = "./output/"
	try:
		os.mkdir(outdir)
	except:
		pass
	
	# ファイルが存在してたらやめる
	outfile = os.path.abspath(outdir + hashlib.md5(inputText.encode("utf-8")).hexdigest() + ".wav")
	if os.path.exists(outfile):
		return outfile
	
	logging.info("Generating WAV")
	
	while True:
		# VOICEROIDプロセスを探す
		window = FindWindow(None, windowName) or FindWindow(None, windowName + "*")
		if window:
			break
		
		# 見つからなかったらVOICEROIDを起動
		subprocess.Popen(["C:\Program Files (x86)\AHS\VOICEROID+\KiritanEX\VOICEROID.exe"])
		time.sleep(32 * waitSec)
	
	while True:
		# ダイアログが出ていたら閉じる
		errorDialog = FindWindow(None, "エラー") or FindWindow(None, "注意") or FindWindow(None, "音声ファイルの保存")
		if errorDialog:
			SendMessage(errorDialog, WM_CLOSE, 0, 0)
			time.sleep(waitSec)
		else:
			break
	
	# 最前列に持ってくる
	SetWindowPos(window, HWND_TOPMOST, 0, 0, 0, 0, SWP_SHOWWINDOW | SWP_NOMOVE | SWP_NOSIZE)
	
	# VOICEROID操作(保存ダイアログを出すまで)
	def __req_speech():
		for hwnd, className, windowText in enum_child_windows(window):
			# テキストを入力する
			if className.count("RichEdit20W"):
				SendMessage(hwnd, WM_SETTEXT, 0, inputText)
			
			if windowText.count("音声保存"):
				# 最小化解除
				ShowWindow(window, SW_SHOWNORMAL)
				
				# 保存ボタンを押す
				SendMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, 0)
				SendMessage(hwnd, WM_LBUTTONUP, 0, 0)
	
	# 別スレッドで実行(保存ダイアログを出すとSendMessageがブロックする)
	threading.Thread(target=__req_speech).start()
	
	# 保存ダイアログを探す
	while True:
		dialog = FindWindow(None, "音声ファイルの保存")
		if dialog:
			break
		
		time.sleep(waitSec)
	
	# 保存ボタンを押す
	while FindWindow(None, "音声ファイルの保存"):
		for hwnd, className, windowText in enum_child_windows(dialog):
			# ファイル名を入力
			if className.count("Edit"):
				SendMessage(hwnd, WM_SETTEXT, 0, outfile)
			
			# 保存ボタンを押す
			if windowText.count("保存"):
				SendMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, 0)
				SendMessage(hwnd, WM_LBUTTONUP, 0, 0)
		
		time.sleep(waitSec)
	
	# プログレスダイアログが表示されている間は待つ
	while FindWindow(None, "音声保存"):
		time.sleep(waitSec)
	
	# txtが存在していたら消す
	try:
		os.remove(outfile.replace("wav", "txt"))
	except:
		pass
	
	return outfile
