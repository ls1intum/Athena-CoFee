from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/tracking")
async def root():
    return {"message": "Hello World!"}

@app.post("/tracking/feedback/{feedback_id}")
async def testPost(feedback_id: int, request: Request):
    body = await request.json()
    print(body)
    return {"id": feedback_id, "body": body}
