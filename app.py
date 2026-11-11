"""HTTP front for the laya agent-task-classifier. POST /classify {text, earlier?} -> {label, probabilities}."""
import json
import os

import laya
from fastapi import FastAPI, HTTPException
from huggingface_hub import hf_hub_download
from pydantic import BaseModel

from state import state_for

MODEL = os.environ.get("MODEL_ID", "kumarabd1996/agent-task-classifier")
REVISION = os.environ.get("MODEL_REVISION")  # set in the image; unset runs main
agent = laya.load(MODEL, device="cpu", revision=REVISION)
questions = json.load(open(hf_hub_download(MODEL, "questions.json", revision=REVISION)))

# Shadow-mode triage model (agent-harness docs/components/task-start.md): what to do with a request, not what shape it has. Baked in from its own
# HF repo at a pinned commit like the classifier; an empty TRIAGE_MODEL_ID runs without it and /triage answers 503.
TRIAGE_MODEL = os.environ.get("TRIAGE_MODEL_ID", "")
triage_agent = triage_questions = None
if TRIAGE_MODEL:
    TRIAGE_REVISION = os.environ.get("TRIAGE_MODEL_REVISION")
    triage_agent = laya.load(TRIAGE_MODEL, device="cpu", revision=TRIAGE_REVISION)
    triage_questions = json.load(open(hf_hub_download(TRIAGE_MODEL, "questions.json", revision=TRIAGE_REVISION)))

app = FastAPI()


class Req(BaseModel):
    text: str
    earlier: str | None = None  # the request being continued, if any


@app.post("/classify")
def classify(r: Req):
    a = agent.predict(state_for(r.text, r.earlier), questions)["answers"]["loop"]
    return {"label": a["choice"], "probabilities": a["probabilities"]}


@app.post("/triage")
def triage(r: Req):
    if triage_agent is None:
        raise HTTPException(status_code=503, detail="this image has no triage model")
    a = triage_agent.predict(state_for(r.text, r.earlier), triage_questions)["answers"]["decision"]
    return {"decision": a["choice"], "probabilities": a["probabilities"]}


@app.get("/healthz")
def healthz():
    return {"ok": True, "triage": triage_agent is not None}
