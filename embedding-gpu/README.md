GPU-accelerated Embedding-Component using CUDA working in interaction with the load balancer component

Basic usage  

Note: The component has shared text_preprocessing code. Building needs to be done from the project root
```bash
docker build . -f embedding-gpu/Dockerfile -t embedding-gpu
docker run --runtime nvidia --rm -it embedding-gpu
```

Change variables

```
-e CHUNK_SIZE=50
-e BALANCER_AUTHORIZATION_SECRET=YWVuaXF1YWRpNWNlaXJpNmFlbTZkb283dXphaVF1b29oM3J1MWNoYWlyNHRoZWUzb2huZ2FpM211bGVlM0VpcAo=
-e BALANCER_SENDRESULT_URL=http://localhost/sendTaskResult
-e BALANCER_GETTASK_URL=http://localhost/getTask
-e TIMEOUT=10
-e MAX_RETRIES=12
```
