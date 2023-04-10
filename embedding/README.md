# Embedding Service

## Start locally (without Docker)

Locally, the service runs on port 8003. To start it,

*   first, run the following command for some preparations:
    ```bash
    make
    ```
    This will create a virtual environment and install all dependencies.

*   After that, configure the used virtual environment:
    ```bash
    source venv/bin/activate
    ```
    If you use an IDE, you can also configure the virtual environment there.
    In PyCharm, you can even go to `File > Open`, choose the embedding folder
    and then choose the `Attach` option.

*   Then, you can start the embedding server using `python start.py` or using your IDE.

## Start with Docker

Use the `docker-compose.yml` file from the parent directory
to start the embedding service (and all others) with Docker.

## Options

Configurable environment variables:

*   `BALANCER_QUEUE_FREQUENCY`
*   `BALANCER_GETTASK_URL`
*   `CHUNK_SIZE`
*   `BALANCER_SENDRESULT_URL`

## API

The following API-routes will be available after start:
<http://localhost:8002/trigger>

Input example JSON for POST on http://localhost:8001/embed

```json
{
  "courseId" : "1234",
  "blocks": [
    {
    "id" : 1,
    "text" : "This is the first text block."
    },
    {
    "id" : 2,
    "text" : "and this is the second one"
    }
  ]
 }
```

Input example JSON for POST on http://localhost:8001/upload

```json
{
  "courseId" : "1234",
  "fileName" : "file.pdf",
  "fileData" : "a21s5d5sqa354a34575"
 }
```
