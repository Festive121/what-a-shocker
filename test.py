from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading

app = FastAPI()

# Initialize a lock
lock = threading.Lock()

# Decorator function to enforce one user at a time
def one_user_at_a_time(func):
    def wrapper(*args, **kwargs):
        with lock:
            if wrapper.current_user is not None:
                return JSONResponse(content={"message": "Only one user is allowed on the website at a time."})
            
            wrapper.current_user = "user_id_here"
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.current_user = None
    wrapper.current_user = None
    return wrapper

@app.get("/website")
@one_user_at_a_time
async def website():
    # Process the request
    # ...
    return {"message": "Welcome to the website!"}
