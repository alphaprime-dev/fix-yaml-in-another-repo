FROM python:3.9

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./bump-k8s-manifests /app/bump-k8s-manifests

ENV PYTHONPATH=/app

CMD ["python", "-m", "bump-k8s-manifests"]