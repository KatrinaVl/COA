FROM python:3.12-slim

WORKDIR /docs
    
COPY analitic_server/requirements.txt .

RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

ENV PYTHONPATH=/docs
COPY ./proto ./proto

COPY analitic_server/start.sh analitic_server/start.sh
RUN chmod +x analitic_server/start.sh

CMD ["bash", "analitic_server/start.sh"]