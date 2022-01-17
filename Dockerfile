ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/se-base-image

RUN pip install fastapi uvicorn
EXPOSE 80
COPY . /backend

WORKDIR /backend
RUN pip install .

CMD ["uvicorn", "t4cclient.__main__:app", "--host", "0.0.0.0", "--port", "80"]
