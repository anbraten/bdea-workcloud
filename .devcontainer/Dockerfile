FROM mcr.microsoft.com/vscode/devcontainers/python:3.8

RUN apt update && apt install -y default-jdk

WORKDIR /workspace

COPY ./requirements.txt /workspace/

RUN pip install -r ./requirements.txt

ENV PATH="/root/.volta/bin:${PATH}"

# install node
RUN VOLTA_HOME=/bin curl https://get.volta.sh | bash \
    && volta install node \
    && volta install yarn
