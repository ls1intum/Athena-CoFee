import sys
import logging
from fastapi import FastAPI, Request, Response, BackgroundTasks
from src.TimerHandler import TimerHandler
from src import UploadingResource
from src.feedback import FeedbackCommentRequest

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Start timer-thread on application startup
timer_handler = TimerHandler()
timer_handler.startTimerThread()

app = FastAPI()
app.include_router(UploadingResource.router)
app.include_router(FeedbackCommentRequest.router)


@app.post("/trigger")
async def trigger(request: Request, response: Response, background_tasks: BackgroundTasks):
    logger.info("Trigger received")
    # Restart Timer-Thread if needed to query for new Task instantly (will not stop a currently running computation)
    background_tasks.add_task(timer_handler.restartTimerThread)
    return {'Trigger received'}
