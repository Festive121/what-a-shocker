import os
from fastapi import FastAPI
import uvicorn
import psutil
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

app = FastAPI()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if GPIO.input(10) == GPIO.HIGH:
        
@app.get("/quit")
def iquit():
    while True:
        if GPIO.input(10) == GPIO.HIGH:
            parent_pid = os.getpid()
            parent = psutil.Process(parent_pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                child.kill()
            parent.kill()

if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.105', port=8000)