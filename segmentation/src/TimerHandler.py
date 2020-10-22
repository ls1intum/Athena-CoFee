from logging import getLogger
from src.ProcessingResource import ProcessingResource
import os
import threading

process_lock = threading.Lock()     # Lock to prevent multiple calculations and restart during calculation
# Interval to query task queue (in seconds)
try:
    timer_frequency = int(os.environ['BALANCER_QUEUE_FREQUENCY']) if "BALANCER_QUEUE_FREQUENCY" in os.environ else 600
except Exception:
    timer_frequency = 600
timer_thread: threading.Thread      # Object holding the Timer-Thread
timer_lock = threading.Lock()       # Lock to prevent multiple invocations of restarting the Timer-Thread at once


class TimerThread(threading.Thread):
    __logger = getLogger(__name__)

    def __init__(self, sleep_interval=1):
        super().__init__()
        self._kill = threading.Event()
        self._interval = sleep_interval

    def run(self):
        self.__logger.info("Timer-Thread started (Frequency " + str(self._interval) + "s)")
        processor = ProcessingResource()

        while True:
            try:
                # Prevent being blocked by restartTimerThread() function
                if process_lock.acquire(timeout=5):
                    self.__logger.info("Querying task queue")
                    task = processor.getNewTask()
                    if task is None:
                        self.__logger.info("No new segmentation task available")
                        process_lock.release()
                        # Query task queue after timeout again
                        is_killed = self._kill.wait(self._interval)
                    else:
                        self.__logger.info("Process new segmentation task")
                        result = processor.processTask(task)
                        processor.sendBackResults(result, task["jobId"])
                        process_lock.release()
                        # Query task queue again without waiting after processing
                        is_killed = self._kill.wait(0)
                else:
                    self.__logger.error("Could not acquire process_lock")
                    # Query task queue after timeout again
                    is_killed = self._kill.wait(self._interval)
            except Exception as e:
                self.__logger.error("Exception while processing: {}".format(str(e)))
                process_lock.release()
                # Query task queue after timeout again
                is_killed = self._kill.wait(self._interval)

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            # wake up and handle
            #is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

        self.__logger.info("Timer-Thread stopped")

    def stop(self):
        self._kill.set()


class TimerHandler:
    __logger = getLogger(__name__)

    def startTimerThread(self):
        global timer_thread
        timer_thread = TimerThread(sleep_interval=timer_frequency)
        timer_thread.daemon = True     # Thread gets killed if main thread exits
        timer_thread.start()

    def stopTimerThread(self):
        global timer_thread
        timer_thread.stop()
        timer_thread.join()

    def restartTimerThread(self):
        # Prevent unnecessary restarts
        if process_lock.acquire(False):
            if timer_lock.acquire(False):
                self.__logger.info("Restarting timer")
                self.stopTimerThread()
                self.startTimerThread()
                timer_lock.release()
            else:
                self.__logger.info("Timer restart already requested.")
            process_lock.release()
        else:
            self.__logger.info("Calculation running. No need to restart timer.")
