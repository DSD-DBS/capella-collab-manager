ARG BASE_IMAGE=buildpack-deps:bullseye
FROM $BASE_IMAGE

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    python3 \
    python3-pip \
    unzip \
    libpq-dev \
    docker.io \
    kubernetes-client && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
COPY . /backend

WORKDIR /backend
RUN pip install .

RUN chmod +x /backend/startup.sh
CMD ["/backend/startup.sh"]
