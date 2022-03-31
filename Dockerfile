FROM python:3.9

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./fix-yaml /app/fix-yaml

ENV PYTHONPATH=/app

CMD ["python", "-m", "fix-yaml"]