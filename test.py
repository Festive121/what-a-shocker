import os
import fastapi
import uvicorn
import psutil

    @app.get("/quit")
    def iquit():
        parent_pid = os.getpid()
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):  # or parent.children() for recursive=False
            child.kill()
        parent.kill()