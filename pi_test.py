import RPi.GPIO as GPIO
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn

GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, background_tasks: BackgroundTasks):
    # Define the HTML page to return
    html_content = """
        <html>
            <head>
                <title>Pin 10 Monitor</title>
            </head>
            <body>
                <h1>Pin 10 Monitor</h1>
                <p>Status: <span id="status">Inactive</span></p>
            </body>
            <script>
                var statusElement = document.getElementById("status");
                var eventSource = new EventSource("/monitor");
                eventSource.onmessage = function(event) {
                    statusElement.textContent = event.data;
                };
            </script>
        </html>
    """

    async def monitor_pin():
        while True:
            if GPIO.input(10):
                status = "Active"
            else:
                status = "Inactive"
            await asyncio.sleep(1)
            yield status

    # Start the monitor_pin function as a background task
    background_tasks.add_task(monitor_pin)

    # Return the HTML page
    return html_content

@app.get("/monitor")
async def monitor(background_tasks: BackgroundTasks):
    async def pin_stream(response):
        async for status in monitor_pin():
            await response.write("data: {}\n\n".format(status))

    async def monitor_pin():
        while True:
            if GPIO.input(10):
                status = "Active"
            else:
                status = "Inactive"
            await asyncio.sleep(1)
            yield status

    # Start the pin_stream function as a background task
    response = StreamingResponse(pin_stream, media_type="text/event-stream")
    background_tasks.add_task(response.__call__, response)

    # Return the StreamingResponse object
    return response

if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.105', port=8000)
