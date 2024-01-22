FROM alpine:3.10

apt-get update -y
apt-get install -y python3
apt-get install -y python3 pip
apt-get install -y gandan >= 0.1.5
  
ENTRYPOINT ["/usr/bin/python3", "-m", "Gandan.gandan", "8080"]
