# classifier

HTTP service for [`kumarabd1996/agent-task-classifier`](https://huggingface.co/kumarabd1996/agent-task-classifier),
a fine-tuned laya model that labels a request by the agent-loop shape it demands
(conversation, companion, learn, diagnose, research, produce, transact, stabilize, plan — taxonomy v2;
v1's eleven labels are in the model repo's history).

CPU only, ~3 GB RAM, ~0.3 s/query. Weights are baked into the image, so it starts offline.

```
docker run -p 8000:8000 ghcr.io/realnighthawk/classifier:latest

curl localhost:8000/classify -H 'content-type: application/json' \
  -d '{"text":"Continue the bulk update","earlier":"What are my biggest categories?"}'
# {"label":"conversation","probabilities":{...}}
```

- `POST /classify` `{text, earlier?}` — `earlier` is the request being continued.
- `GET /healthz`
- Build another checkpoint: `docker build --build-arg MODEL_ID=<hf repo> --build-arg MODEL_REVISION=<commit sha> .`
  (`MODEL_REVISION` is pinned in the Dockerfile; bumping it is also what refreshes CI's cached weights layer.)

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

## Triage (shadow mode)

A second checkpoint, [`kumarabd1996/agent-triage-classifier`](https://huggingface.co/kumarabd1996/agent-triage-classifier), says what to do with a
request (`answer`, `ask`, `start_task`, `schedule`, `act`, `unsure`) rather than what shape it has. Same pod, same rules as the classifier: baked in at
a pinned commit (`TRIAGE_MODEL_REVISION` in the Dockerfile), no token, offline at runtime. Set `TRIAGE_MODEL_ID` empty to run without it.

```
curl localhost:8000/triage -H 'content-type: application/json' -d '{"text":"remind me to call Sam at 5pm tomorrow"}'
# {"decision":"schedule","probabilities":{...}}
```

`/healthz` reports `triage: true|false`. Roughly 2 GB more memory; the infra chart's `classifier.resources` is sized for both.
