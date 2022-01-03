ARG BASE_IMAGE=debian:bullseye
FROM $BASE_IMAGE
RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    python3 \
    python3-pip \
    unzip && rm -rf /var/lib/apt/lists/*

# Create techuser with UID
ARG UID=1001
RUN useradd -l -m -u $UID techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser

RUN ln -s $(which python3) /usr/bin/python
