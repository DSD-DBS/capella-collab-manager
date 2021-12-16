ARG BASE_IMAGE=buildpack-deps:bullseye
FROM BASE_IMAGE
RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    python3 \
    python3-pip

# Create techuser with UID
RUN useradd -l -m -u 1001000000 techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser


RUN ln -s $(which python3) /usr/bin/python
