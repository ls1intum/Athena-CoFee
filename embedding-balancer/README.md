Service runs on port 8000

Balances load for embedding requests to underlying processing nodes

the following API-route will be available after start:
[http://localhost:8000/embed](http://localhost:8000/embed) or [http://localhost/embed](http://localhost/embed) if being run in combination with traefik and the docker-compose file.

Input example JSON for POST on http://localhost/embed

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

