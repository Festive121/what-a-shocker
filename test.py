from fastapi import FastAPI
import threading

app = FastAPI()

class WebsiteLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_user = None
    
    def __enter__(self):
        self.lock.acquire()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.current_user = None
        self.lock.release()

website_lock = WebsiteLock()

@app.get("/website")
async def website():
    with website_lock as lock:
        if lock.current_user is not None:
            return {"message": "Only one user is allowed on the website at a time."}
        
        lock.current_user = "user_id_here"
        
        # Process the request
        # ...
        return {"message": "Welcome to the website!"}
