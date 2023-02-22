import threading
from fastapi import FastAPI, Request, HTTPException
from fastapi.routing import APIRoute
from starlette.types import Receive, Scope, Send

app = FastAPI()

# Initialize a lock
lock = threading.Lock()

# Dependency to enforce one user at a time
async def one_user_at_a_time(request: Request):
    with lock:
        if one_user_at_a_time.current_user is not None:
            raise HTTPException(status_code=423, detail="Only one user is allowed on the website at a time.")
        
        one_user_at_a_time.current_user = "user_id_here"
        response = await app(request)
        one_user_at_a_time.current_user = None
        return response
one_user_at_a_time.current_user = None

# Custom route class that uses the one_user_at_a_time dependency
class OneUserAtATimeRoute(APIRoute):
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive=receive)
        response = await one_user_at_a_time(request)
        await response(scope, receive, send)

# Add the custom route class to the app
app.router.route_class = OneUserAtATimeRoute

@app.get("/website")
async def website():
    # Process the request
    # ...
    return {"message": "Welcome to the website!"}
