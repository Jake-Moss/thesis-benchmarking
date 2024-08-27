import multiprocessing as mp
import signal
import time
import sys
import os


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)
