FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY showcase.py .
COPY dashboard/ dashboard/

RUN pip install --no-cache-dir -e "."

EXPOSE 8080

CMD ["python", "showcase.py"]
