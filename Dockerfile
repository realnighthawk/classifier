# docker build -t classifier .
FROM python:3.12-slim
ARG MODEL_ID=kumarabd1996/agent-task-classifier
# The HF commit baked in. Pinned (not "main") so a rebuild is reproducible and, because it is part of the layer
# below, changing it is what makes CI's layer cache fetch new weights.
ARG MODEL_REVISION=226ce32acfbb30aabd22548d1ef667b33af2df1d
# The shadow-mode triage checkpoint (what to do with a request, not its shape), served at /triage. Same rules: public repo, pinned commit.
ARG TRIAGE_MODEL_ID=kumarabd1996/agent-triage-classifier
ARG TRIAGE_MODEL_REVISION=2a3fbb43f445727fed78907fb814af298d94bf0e
ENV HF_HOME=/opt/hf PYTHONUNBUFFERED=1 MODEL_ID=$MODEL_ID MODEL_REVISION=$MODEL_REVISION TRIAGE_MODEL_ID=$TRIAGE_MODEL_ID TRIAGE_MODEL_REVISION=$TRIAGE_MODEL_REVISION
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir "laya[serve]==0.4.1" fastapi uvicorn
# bake weights so pods start offline (public repo, no token)
RUN python -c "import laya,os;from huggingface_hub import hf_hub_download as d;m=os.environ['MODEL_ID'];r=os.environ['MODEL_REVISION'];laya.load(m,device='cpu',revision=r);d(m,'questions.json',revision=r)"
RUN python -c "import laya,os;from huggingface_hub import hf_hub_download as d;m=os.environ['TRIAGE_MODEL_ID'];r=os.environ['TRIAGE_MODEL_REVISION'];laya.load(m,device='cpu',revision=r);d(m,'questions.json',revision=r)"
COPY app.py state.py /app/
WORKDIR /app
RUN useradd --system --uid 10003 clf && chmod -R a+rX /opt/hf
USER clf
ENV HF_HUB_OFFLINE=1
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
