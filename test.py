from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
import threading

app = FastAPI()

# Initialize a lock
lock = threading.Lock()

# Dependency to enforce one user at a time
async def one_user_at_a_time(request: Request):
    with lock:
        if one_user_at_a_time.current_user is not None:
            raise HTTPException(status_code=423, detail="Only one user is allowed on the website at a time.")
        
        one_user_at_a_time.current_user = "user_id_here"
        response = await request.app.router.handle_request(request)
        one_user_at_a_time.current_user = None
        return response
one_user_at_a_time.current_user = None

# Custom route class that uses the one_user_at_a_time dependency
class OneUserAtATimeRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()
        async def new_route_handler(request: Request):
            return await one_user_at_a_time(request)
        return new_route_handler or original_route_handler

# Add the custom route class to the app
app.router.route_class = OneUserAtATimeRoute

@app.get("/website")
async def website():
    # Process the request
    # ...
    return {"message": "Welcome to the website!"}
