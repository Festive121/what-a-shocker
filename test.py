import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/shutdown")
def shutdown():
    os.kill(os.getpid(), 9)