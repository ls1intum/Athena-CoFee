Service runs on port 8002

```bash
uvicorn --port 8002 --host 0.0.0.0 --reload src.main:app
```

Note: In Artemis 8080 is written in configs

Configurable environment variables:

-  BALANCER\_QUEUE\_FREQUENCY
-  BALANCER\_GETTASK\_URL
-  CHUNK\_SIZE
-  BALANCER\_SENDRESULT\_URL

the following API-routes will be available after start:
[http://localhost:8002/trigger](http://localhost:8002/trigger)


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

