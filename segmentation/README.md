# Segmentation Service

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

*   Then, you can start the segmentation server using `python start.py` or using your IDE.

## Start with Docker

Use the `docker-compose.yml` file from the parent directory
to start the embedding service (and all others) with Docker.

## Options

Configurable environment variables:

*   `BALANCER_QUEUE_FREQUENCY`
*   `BALANCER_GETTASK_URL`
*   `BALANCER_SENDRESULT_URL`
