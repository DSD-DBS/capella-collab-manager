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

RUN pip install fastapi uvicorn
EXPOSE 80
COPY . /backend

WORKDIR /backend
RUN pip install .

CMD ["uvicorn", "t4cclient:app", "--host", "0.0.0.0", "--port", "80"]
