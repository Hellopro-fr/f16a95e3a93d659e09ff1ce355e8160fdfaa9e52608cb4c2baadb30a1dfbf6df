FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN chmod +x init.sh run.sh
RUN ./init.sh

EXPOSE 8502
CMD ["./run.sh"]
