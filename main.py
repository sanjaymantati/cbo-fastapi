from fastapi import FastAPI
import uvicorn
import os

from controller import api_router
from apscheduler.schedulers.background import BackgroundScheduler
import time

from service.cbo_detection_service import CBODetectionService


"""GET ENVIRONMENT VARIABLES"""
PORT = int(os.environ.get("PORT"))



async def load_start_up_apps():
    """Configure Clients"""

if __name__ == "__main__":
    app = FastAPI()
    app.include_router(api_router)
    app.add_event_handler("startup", load_start_up_apps)


    # Define your periodic task
    def my_scheduled_job():
        print(
            f"Scheduled job executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


    detection_service = CBODetectionService()
    # Create scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(detection_service.do_inference, 'interval', minutes=10)
    scheduler.start()
    detection_service.do_inference()

    @app.on_event("shutdown")
    def shutdown_event():
        scheduler.shutdown()
        print("Scheduler shut down")

    port_no = 80
    uvicorn.run(app, host="0.0.0.0", port=PORT)
