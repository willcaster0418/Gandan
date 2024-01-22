FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN /usr/bin/python3 -m pip install gandan==0.1.5
  
ENTRYPOINT ["/usr/bin/python3", "-m", "gandan.Gandan", "8080"]
