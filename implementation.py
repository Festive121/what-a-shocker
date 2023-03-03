# uvicorn main:app --host 192.168.1.105 --port 8000
# cloudflared tunnel --config /home/shack/.cloudflared/config.yaml run

import asyncio
import RPi.GPIO as GPIO
import secrets
import subprocess
import time
import uvicorn
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from typing import Callable
from uuid import UUID, uuid4

# ----- vvv ----- #
ip = "192.168.1.160"
# ----- ^^^ ----- #

class CustomRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            await self.lock.acquire()
            response: Response = await original_route_handler(request)
            self.lock.release()
            return response

        return custom_route_handler

app = FastAPI()
security = HTTPBasic()

app.openapi = {"info": {"title": "Remote Shock", "verison": "1.0.0"}}
app.router.route_class = CustomRoute
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
async def read_current_user(request: Request, response: Response, str = Depends(get_current_username)):
    client = request.client.host

    if client == ip:
        response.headers["Location"] = "/home"
        response.status_code = 302
    else:
        return templates.TemplateResponse("unathorized.html", {"request": request})
        

@app.get("/home", response_class=HTMLResponse)
async def read_item(request: Request):    
    client = request.client.host

    if client == ip:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return templates.TemplateResponse("unathorized.html", {"request": request})
    

@app.get("/run")
def runit(response: Response):
    if auth:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, True)
        time.sleep(1)
        GPIO.output(18, False)
        response.headers["Location"] = "/"
        response.status_code = 302
    else:
        return PlainTextResponse(content="UNAUTHORIZED")


if __name__ == "__main__":
    uvicorn.run(app, host='192.168.1.105', port=8000)
