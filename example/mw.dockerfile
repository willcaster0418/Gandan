FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y net-tools
RUN apt-get install -y python3
RUN apt-get install -y pip
COPY ./py/gandan /usr/local/lib/python3.12/dist-packages/
ENTRYPOINT ["/usr/bin/python3", "-m", "gandan.GandanWebSocket", "8080"]