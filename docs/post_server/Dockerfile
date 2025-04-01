FROM python:3.12-slim

WORKDIR /docs
    
COPY post_server/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/docs
COPY ./proto ./proto

CMD ["bash", "post_server/start.sh"]