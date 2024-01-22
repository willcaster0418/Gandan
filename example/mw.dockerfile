FROM alpine:3.10

apt-get update -y
apt-get install -y python3
apt-get install -y python3 pip
apt-get install -y gandan
  
ENTRYPOINT ["/bin/bash"]
