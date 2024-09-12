# FROM ubuntu:jammy
FROM python:3.11-slim

# RUN apt update && \
#     apt upgrade -y && \
#     apt install -y python3-pip

COPY . /aithena_services_src

RUN pip3 install -e /aithena_services_src --no-cache-dir
ENV AITHENA_SERVICES_CONFIG_PATH=/mnt/config/config.json

EXPOSE 80

CMD ["fastapi", "run", "/aithena_services_src/api/main.py", "--port", "80"]