# ./parallel_commands "uvicorn main:app --host localhost --port 8000" "cloudflared tunnel --config /home/shack/.cloudflared/config.yaml run"

import asyncio
import RPi.GPIO as GPIO
import secrets
import subprocess
import time
import uvicorn
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import HTMLResponse
from typing import Callable
from threading import Thread, Lock
import time
import uuid

SLEEP_TIME_S = 10
TIMEOUT_S = 120

run_lock = Lock()
time_of_last_run = None


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
# home = "/" + str(UUID)
# run = "/" + UUID

app.openapi = {"info": {"title": "Remote Shock", "verison": "1.0.0"}}
app.router.route_class = CustomRoute
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return RedirectResponse("/unauthorized")


@app.get("/unauthorized")
async def unauth(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})


@app.get("/key-url")
async def read_current_user(request: Request, response: Response):
    id = uuid.uuid4()
    home = str(id) + "/home/"

    return RedirectResponse(home)


@app.get("/{id}/home", response_class=HTMLResponse)
async def read_item(id: uuid.UUID, request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def run():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    svo = GPIO.PWM(11, 50)
    svo.start(0)

    svo.ChangeDutyCycle(3)
    time.sleep(.5)
    svo.ChangeDutyCycle(2)
    time.sleep(0.5)
    svo.ChangeDutyCycle(0)

    svo.stop()
    GPIO.cleanup()


@app.get("/run", response_class=HTMLResponse)
def runit(response: Response, request: Request):
    id = uuid.uuid4()
    home = str(id) + "/home/"

    current_time = time.monotonic()
    run_lock.acquire()


run()
time_of_last_run = current_time
run_lock.release()

return RedirectResponse(home)


def run_timer_check():
    while True:
        run_lock.aquire()
        current_time = time.monotonic()
        if time_of_last_run is None or current_time - time_of_last_run > 0.75 * TIMEOUT_S:
            runit()
            time_of_last_run = current_time
        run_lock.release()
        time.sleep(SLEEP_TIME_S)


if __name__ == "__main__":
    background_thread = Thread(target=run_timer_check)
    uvicorn.run(app, host='192.168.1.105', port=8000)
