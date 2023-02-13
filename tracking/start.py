import uvicorn


def start():
    uvicorn.run("src.main:app", host="0.0.0.0", port=8004, reload=True)


if __name__ == "__main__":
    start()
