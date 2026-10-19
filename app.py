"""HTTP front for the laya agent-task-classifier. POST /classify {text, earlier?} -> {label, probabilities}."""
import json
import os

import laya
from fastapi import FastAPI
from huggingface_hub import hf_hub_download
from pydantic import BaseModel

from state import state_for

MODEL = os.environ.get("MODEL_ID", "kumarabd1996/agent-task-classifier")
REVISION = os.environ.get("MODEL_REVISION")  # set in the image; unset runs main
agent = laya.load(MODEL, device="cpu", revision=REVISION)
questions = json.load(open(hf_hub_download(MODEL, "questions.json", revision=REVISION)))

app = FastAPI()


class Req(BaseModel):
    text: str
    earlier: str | None = None  # the request being continued, if any


@app.post("/classify")
def classify(r: Req):
    a = agent.predict(state_for(r.text, r.earlier), questions)["answers"]["loop"]
    return {"label": a["choice"], "probabilities": a["probabilities"]}


@app.get("/healthz")
def healthz():
    return {"ok": True}
