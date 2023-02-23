import os
from fastapi import FastAPI
import uvicorn
import psutil

app = FastAPI()

@app.get("/quit")
def iquit():
    parent_pid = os.getpid()
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):  # or parent.children() for recursive=False
        child.kill()
    parent.kill()
    
if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.105', port=8000)