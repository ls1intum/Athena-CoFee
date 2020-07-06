Service runs on port 8000

Balances load for embedding requests to underlying processing nodes

the following API-routes will be available after start:
[http://localhost:8001/embed](http://localhost:8000/embed)  
[http://localhost:8001/upload](http://localhost:8000/upload)

Input example JSON for POST on http://localhost:8000/embed

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


Input example JSON for POST on http://localhost:8000/upload

```json
{
  "courseId" : "1234",
  "fileName" : "file.pdf",
  "fileData" : "a21s5d5sqa354a34575"
 }
```

