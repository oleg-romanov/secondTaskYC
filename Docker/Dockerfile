FROM python:3.10-slim

WORKDIR /app
RUN pip install boto3 Pillow requests sanic ydb
COPY ./index.py .
CMD [ "python", "index.py" ]
