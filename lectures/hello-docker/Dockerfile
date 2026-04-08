# Base image
FROM ubuntu:latest

# Avoid prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install nano + python3 + pip
RUN apt-get update && \
    apt-get install -y nano python3 python3-pip && \
    apt-get clean

# Install pandas
RUN pip3 install pandas

# Keep container running
ENTRYPOINT ["tail", "-f", "/dev/null"]