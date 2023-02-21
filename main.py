import RPi.GPIO as GPIO
import time
import subprocess
import secrets
import asyncio
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import HTMLResponse

app = FastAPI()
security = HTTPBasic()

app.openapi = {"info": {"title": "Remote Shock", "verison": "1.0.0"}}
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"jack is so cool"
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"i, ian salyer agree"
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
async def read_current_user(response: Response, str = Depends(get_current_username)):
    response.headers["Location"] = "/home"
    response.status_code = 302

@app.get("/home", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/run")
async def run(response: Response):
    result = subprocess.run(["python", "script.py"], capture_output=True)
    response.headers["Location"] = "/"
    response.status_code = 302

@app.get("/runit")
def runit(response: Response):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)

    GPIO.output(18, True)
    time.sleep(1)
    GPIO.output(18, False)
    return {"message": "ran it"}    

@app.get("/test")
async def test():
    return {"message": "test"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app --host 0.0.0.0 --port 8000")
