FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt && \
    python -m pip install pylatexenc ipykernel jupyter-client jupyter-core

COPY . /app

CMD ["python", "run_demo.py"]
