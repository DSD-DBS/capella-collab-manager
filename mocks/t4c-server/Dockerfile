FROM buildpack-deps:bullseye

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 80
COPY . /mock

WORKDIR /mock
RUN pip install .

CMD ["uvicorn", "mock:app", "--host", "0.0.0.0", "--port", "80"]
