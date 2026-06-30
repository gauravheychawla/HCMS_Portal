# ── Unisys HCMS Cloud Portal ──────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY static/ ./static/

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["python", "app.py"]
