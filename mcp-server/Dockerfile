FROM python:3.11-slim

WORKDIR /app

COPY mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp-server/ .
COPY data/ /data/

EXPOSE 3001

CMD ["python3", "main.py"]
