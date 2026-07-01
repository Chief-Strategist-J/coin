FROM python:3.10-slim

WORKDIR /app

COPY chain/ /app/chain/
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

ENTRYPOINT ["python3", "-m", "chain.rpc.api.acp_adapter"]
