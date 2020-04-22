This service validates the correctness of automatic feedback for text blocks with an adapted BLEU (Bilingual Evaluation Understudy) algorithm and responds with a number between 0-100.
  
Runs on localhost:8080/validate

To test it locally, follow these steps: 
1. Clone repository and change to working directory 
2. `docker build -t [image_name] .`
3. `docker run -it -p8080:8080 [image_name]`

To test API with cURL : 
4. Open new terminal 
5. `curl --header "Content-Type: application/json" \ 
    --request POST \ 
    --data @[.json file, example can be found in request_body.json] \
    http://localhost:8080/validate 
6. Inspect result ( {"confidence": [Number]} ) 