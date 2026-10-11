"""HTTP front for the laya agent-task-classifier. POST /classify {text, earlier?} -> {label, probabilities}."""
import json
import os

import laya
from fastapi import FastAPI
from huggingface_hub import hf_hub_download
from pydantic import BaseModel

MODEL = os.environ.get("MODEL_ID", "kumarabd1996/agent-task-classifier")
agent = laya.load(MODEL, device="cpu")
questions = json.load(open(hf_hub_download(MODEL, "questions.json")))

app = FastAPI()


class Req(BaseModel):
    text: str
    earlier: str | None = None  # the request being continued, if any


@app.post("/classify")
def classify(r: Req):
    # continuation format the model was trained on
    state = f"Earlier request: {r.earlier}\nNew request: {r.text}" if r.earlier else r.text
    a = agent.predict(state, questions)["answers"]["loop"]
    return {"label": a["choice"], "probabilities": a["probabilities"]}


@app.get("/healthz")
def healthz():
    return {"ok": True}
