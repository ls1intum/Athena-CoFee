import sys
import logging
from fastapi import FastAPI, Request, Response, BackgroundTasks
from src.TimerHandler import TimerHandler
from src import UploadingResource
from src.feedback import FeedbackCommentRequest

logger = logging.getLogger()
# Set log_level to logging.DEBUG to write log files with json contents
# Warning: This will produce a lot of data in production systems
log_level = logging.INFO
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
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
