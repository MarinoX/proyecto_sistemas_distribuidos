FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY nodo.py .

CMD ["python", "nodo.py", "6000"]

