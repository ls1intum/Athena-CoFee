import base64

from fastapi import FastAPI, Request, Response, status
from jwt import decode
from .database.Connection import Connection
from os import environ

app = FastAPI()


@app.post('/tracking/text-exercise-assessment', status_code=201)
async def testPost(request: Request, response: Response):
    feedback = await request.json()
    jwt_token = request.headers.get('x-athene-tracking-authorization')
    secret_base64 = environ['JWT_SECRET_BASE64']
    try:
        encoded_jwt_token = decode(jwt_token, base64.b64decode(secret_base64), verify=True, algorithms=['HS256'])
        if encoded_jwt_token.get('result_id') != feedback.get('participation').get('results')[0].get('id'):
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Please do not spam manually!'}
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'Your token is not valid!'}
    try:
        conn = Connection()
        conn.insert_document('feedback', feedback)
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'message': 'Saving in the database did not work!'}
    return {'Feedback is tracked successfully'}
