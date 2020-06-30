import json
import base64

from fastapi import FastAPI, Request
from jwt import decode
from .database.Connection import Connection
from os import environ

app = FastAPI()


@app.get("/tracking")
async def root():
    return {"message": "Hello World!"}


@app.post("/tracking/feedback/{feedback_id}")
async def testPost(feedback_id: int, request: Request):
    feedback = await request.json()
    jwt_token = request.headers.get('x-athene-tracking-authorization')
    secret_base64 = environ['JWT_SECRET_BASE64']
    encoded_jwt_token = decode(jwt_token, base64.b64decode(secret_base64), verify=True, algorithms=['HS256'])
    if (encoded_jwt_token.get('result_id')) != feedback.get('results')[0].get('id'):
        return {"message": "You are not authorized!"}
    conn = Connection()
    try:
        conn.insert_document('feedback', feedback)
    except Exception as e:
        return {"message": "Saving in the database did not work!"}
    return {"id": feedback_id}
