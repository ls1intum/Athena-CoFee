import uvicorn


def start():
    uvicorn.run("src.main:app", host="127.0.0.1", port=8003, reload=True, reload_dirs=["src"])


if __name__ == "__main__":
    start()
