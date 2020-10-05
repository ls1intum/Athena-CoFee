Service runs on port 8001

```bash
uvicorn --port 8001 --host 0.0.0.0 --reload src.main:app
```

Note: In Artemis 8080 is written in configs

Configurable environment variables:

  - BALANCER\_QUEUE\_FREQUENCY
  - BALANCER\_GETTASK\_URL
  - BALANCER\_SENDRESULT\_URL
