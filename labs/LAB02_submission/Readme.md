# Lab 2 Submission README

## Student Information
- Name: Amelia Hammer
- Date: 2026-4-2

## Deliverables Included
- `inference_api/Dockerfile`
- `preprocessor/Dockerfile`
- `inference_api/app.py` (with `/health` and `/stats`)
- `sample_classifications_20.jsonl` (first 20 lines from logs)
- `Reflection.md`

## Docker Build Commands Used

### Inference API
```bash
docker build -t congo-inference ./inference_api
```

### Preprocessor
```bash
docker build -t congo-preprocessor ./preprocessor
```

## Docker Run Commands Used

### Inference API Container
```bash
docker run -d --name congo-inference-api -p 8000:8000 -v "$(pwd)/logs:/logs" congo-inference
```

### Preprocessor Container
```bash
docker run -d --name congo-preprocessor -v "$(pwd)/incoming:/incoming" -e API_URL=http://host.docker.internal:8000 congo-preprocessor
```

## Brief Explanation: How the Containers Communicate
[Write 3-6 sentences here.]

Points to cover:
- Which container calls which endpoint.
- How the preprocessor knows where to find the inference API.
- How images and logs persist using mounted host folders.
- Why `localhost` can be tricky inside containers.

## Brief Explanation: How the Containers Communicate

The preprocessor container sends images to the inference API by making HTTP requests to the `/predict` endpoint. It knows where to send those requests because we pass in the API URL using the `API_URL` environment variable (`http://host.docker.internal:8000`). The images are stored in a shared `incoming/` folder that’s mounted from the host into the preprocessor container, and the API writes results to a `logs/` folder that’s also mounted to the host so everything persists. One thing that was important to understand is that `localhost` inside a container doesn’t mean your laptop — it means the container itself. That’s why we had to use `host.docker.internal` so the preprocessor could actually reach the API running on the host.