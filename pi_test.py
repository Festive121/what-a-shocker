import RPi.GPIO as GPIO
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
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

    async def monitor_pin(response):
        current_status = GPIO.input(10)
        while True:
            if GPIO.input(10) != current_status:
                current_status = GPIO.input(10)
                await response.write("data: {}\n\n".format(current_status))
            await asyncio.sleep(1)

    # Start the monitor_pin function as a background task
    response = StreamingResponse(monitor_pin, media_type="text/event-stream")
    background_tasks.add_task(monitor_pin, response)

    # Return the HTML page
    return html_content

if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.105', port=8000)
