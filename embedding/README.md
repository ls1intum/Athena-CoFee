Service runs on port 8002/embed

Note: In Artemis 8080 is written in configs

gunicorn src.app


Input example JSON for POST

```json
{
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
