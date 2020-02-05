from enum import Enum
from datetime import datetime
from .file import LogFormat, FileSystem, File
from colorama import init, Fore, Back, Style
from queue import Queue
from . import threading as _threading
import time, sys

def Now(): return datetime.now()
def Time(): return Now().strftime("%H:%H:%S")
def Date(): return Now().strftime("%d/%m/%Y")

class LogType(Enum):

	Info = (Fore.GREEN, Fore.WHITE, Back.BLACK)
	Install = (Fore.CYAN, Fore.LIGHTBLUE_EX, Back.BLACK)
	Warn = (Fore.LIGHTRED_EX, Fore.YELLOW, Back.BLACK)
	Error = (Fore.LIGHTRED_EX, Fore.LIGHTRED_EX, Back.BLACK)
	Debug = (Fore.LIGHTMAGENTA_EX, Fore.LIGHTGREEN_EX, Back.BLACK)
	Exit = (Fore.LIGHTWHITE_EX, Fore.WHITE, Back.BLACK)

	@staticmethod
	def fromString(string: str = ""):
		string = string.lower()
		if string == "info": return LogType.Info
		elif string == "install": return LogType.Install
		elif string == "warn": return LogType.Warn
		elif string == "error": return LogType.Error
		elif string == "debug": return LogType.Debug
		elif string == "exit": return LogType.Exit
		else: return None

	def __str__(self):
		return f"{self.name}"

class Log:

	@staticmethod
	def AllLogs():
		return Log.Logs().data

	@staticmethod
	def LogFile():
		return File.GetOrCreate(FileSystem, "logs")

	@staticmethod
	def Logs():
		logs = LogFormat.loadFrom(Log.LogFile())
		if logs is None or type(logs) != LogFormat: logs = LogFormat()
		return logs

	@staticmethod
	def fromString(string: str = ""):
		if string is None or type(string) != str or len(string) < 26: return None
		else:
			try:
				tIndex = 2
				tTmp = None
				while tTmp is None:
					tIndex += 1
					tTmp = LogType.fromString(string[1:tIndex])
				l = Log(tTmp, string[tIndex + 23:].encode("utf-8").decode("unicode_escape"), False)
				l.date = string[tIndex + 2:tIndex + 12]
				l.time = string[tIndex + 13:tIndex + 21]
				return l
			except ValueError: return None

	def __init__(self, logType: LogType = LogType.Info, info: str = "", save: bool = True):
		if logType is None or type(logType) != LogType: logType = LogType.Info
		if info is None or type(info) != str: info = "No Log Information Passed To Log"
		self.logType = logType
		self.raw_info = info
		# Sanitize input for escape characters
		self.protected_info = info.replace("\a", "\\a").replace("\b", "\\b").replace("\t", "\\t").replace("\n", "\\n").replace("\v", "\\v").replace("\f", "\\f").replace("\r", "\\r")
		self.date = Date()
		self.time = Time()

		if save: self.save()

	def post(self):
		LoggingPrintQueue.put(self)
		return self

	def save(self):
		LoggingSaveQueue.put(self)
		return self

	@property
	def colored(self):
		return self._colored(self.protected_info)

	@property
	def raw_colored(self):
		return self._colored(self.raw_info)

	def _colored(self, text: str = ""):
		colors = self.logType.value[:]
		return f"{colors[2]}{Fore.WHITE}{Style.BRIGHT}[{colors[0]}{self.logType.name}{Fore.WHITE}] \
{self.date} {self.time}{Fore.CYAN}: {colors[1]}{text}{Style.RESET_ALL}"

	def __str__(self):
		return f"[{self.logType.name}] {self.date} {self.time}: {self.protected_info}"

# Queue system
LoggingSaveQueue = Queue(0)
LoggingPrintQueue = Queue(0)

def Finalize():
	# Stop threads
	LoggingSaveThread.stop()
	LoggingPrintThread.stop()

	# Do one final invoke
	Save()
	Prints()

	global LoggingSaveQueue, LoggingPrintQueue

	# Clear queues incase anything else is trying to use them
	LoggingSaveQueue = Queue(0)
	LoggingPrintQueue = Queue(0)

def Save():
	logs = Log.Logs()
	if LoggingSaveQueue.empty(): return
	while not LoggingSaveQueue.empty():
		logs.data.append(LoggingSaveQueue.get())
	logs.write(Log.LogFile())

def Prints():
	while not LoggingPrintQueue.empty():
		if sys.stdout.writable and not sys.stdout.closed:
			sys.stdout.write(LoggingPrintQueue.get().raw_colored + "\n")
		else:
			return

# Threading for queues
LoggingSaveThread = _threading.SimpleThread(Save, True).start()
LoggingPrintThread = _threading.SimpleThread(Prints, True).start()

if __name__ != "__main__":
	init()