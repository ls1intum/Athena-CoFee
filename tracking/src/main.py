import json
import base64

from fastapi import FastAPI, Request
from jwt import decode, exceptions
from .database.Connection import Connection
from os import environ

app = FastAPI()


@app.get("/tracking")
async def root():
    return {"message": "Hello World!"}


@app.post("/tracking/result/{result_id}")
async def testPost(result_id: int, request: Request):
    feedback = await request.json()
    jwt_token = request.headers.get('x-athene-tracking-authorization')
    secret_base64 = environ['JWT_SECRET_BASE64']
    try:
        encoded_jwt_token = decode(jwt_token, base64.b64decode(secret_base64), verify=True, algorithms=['HS256'])
        if (encoded_jwt_token.get('result_id')) != feedback.get('results')[0].get('id'):
            return {"message": "Please don't spam manually!"}
    except exceptions as e:
        print(e)
        return {"message": "Your token is not valid!"}
    try:
        conn = Connection()
        conn.insert_document('feedback', feedback)
    except Exception as e:
        print(e)
        return {"message": "Saving in the database did not work!"}
    return {"id": result_id}
