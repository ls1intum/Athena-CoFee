import json

from fastapi import FastAPI, Request
from .database.Connection import Connection

app = FastAPI()


@app.get("/tracking")
async def root():
    return {"message": "Hello World!"}


@app.post("/tracking/feedback/{feedback_id}")
async def testPost(feedback_id: int, request: Request):
    feedback = await request.json()
    conn = Connection()
    try:
        conn.insert_document('feedback', feedback)
    except Exception as e:
        return {"message": "Saving in the database did not work!"}
    return {"id": feedback_id}
