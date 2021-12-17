ARG BASE_IMAGE=ubuntu:focal
FROM $BASE_IMAGE
RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    python3 \
    python3-pip \
    unzip

# Create techuser with UID
RUN useradd -l -m -u 1001000000 techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser

RUN ln -s $(which python3) /usr/bin/python
