import logging
import os
import sys
import time
from processing.ProcessingResource import ProcessingResource

logger = logging.getLogger()
# Set log_level to logging.DEBUG to write log files with json contents
# Warning: This will produce a lot of data in production systems
log_level = logging.INFO
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

processor = ProcessingResource()
attempt = 0    # Current attempt
# Timeout in seconds between retries
timeout = int(os.environ['TIMEOUT']) if "TIMEOUT" in os.environ else 10
# Maximum amount of retires before exiting
max_retries = int(os.environ['MAX_RETRIES']) if "MAX_RETRIES" in os.environ else 30

while attempt <= max_retries:
    try:
        attempt += 1
        logger.info("Querying task queue. Attempt ({}/{})".format(attempt, max_retries))
        task = processor.getNewTask()
        if task is None:
            logger.info("No new embedding task available")
            sleeptime = timeout
        else:
            attempt = 0
            sleeptime = 0
            logger.info("Process new embedding task")
            processor.processTask(task)
    except Exception as e:
        logger.error("Exception while processing: {}".format(str(e)))
        sleeptime = timeout
    finally:
        if attempt >= max_retries:
            logger.info("Maximum number of attempts exceeded. Exiting.")
            break
        # Query task queue after timeout again
        logger.info("Next attempt in {} seconds".format(timeout))
        time.sleep(sleeptime)
