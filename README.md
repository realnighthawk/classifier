# classifier

HTTP service for [`kumarabd1996/agent-task-classifier`](https://huggingface.co/kumarabd1996/agent-task-classifier),
a fine-tuned laya model that labels a request by the agent-loop shape it demands
(conversation, diagnose, research, arrange, acquire, execute, make, tend, learn, companion, react).

CPU only, ~3 GB RAM, ~0.3 s/query. Weights are baked into the image, so it starts offline.

```
docker run -p 8000:8000 ghcr.io/realnighthawk/classifier:latest

curl localhost:8000/classify -H 'content-type: application/json' \
  -d '{"text":"Continue the bulk update","earlier":"What are my biggest categories?"}'
# {"label":"conversation","probabilities":{...}}
```

- `POST /classify` `{text, earlier?}` — `earlier` is the request being continued.
- `GET /healthz`
- Build another checkpoint: `docker build --build-arg MODEL_ID=<hf repo> .`

Behind LiteLLM (pass-through):

```yaml
general_settings:
  pass_through_endpoints:
    - path: /classify
      target: http://classifier:8000/classify
```

Scale with replicas, not uvicorn workers (each worker loads its own copy of the model).

## Deploy

Deployed by the `classifier` block of the infra `model` chart (`classifier-svc`, port 8000), and
reached through LiteLLM's `/classify` pass-through route.
