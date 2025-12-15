FROM python:3.13-alpine

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install C compiler and netcat for database wait
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers \
    netcat-openbsd \
    ffmpeg \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    curl

# upgrade pip
RUN pip install --upgrade pip

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies to reduce image size (optional)
# RUN apk del build-base gcc musl-dev

# copy project
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "src/start_server.py"]
