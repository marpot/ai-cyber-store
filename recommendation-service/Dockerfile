FROM python:3.12

WORKDIR /app

# Copy only requirements first for better layer reuse.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package source. We preserve the directory layout so that
# ``from app.X import Y`` works both inside the container and during
# local pytest runs against the mounted volume.
COPY app ./app

# Place the package itself on PYTHONPATH so flat-style imports (used by
# legacy callers) still resolve.
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]