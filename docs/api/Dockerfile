FROM python:3.12-slim

WORKDIR /docs
COPY api/requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/docs
COPY ./proto ./proto

ENTRYPOINT ["python", "-m", "api.api"]
