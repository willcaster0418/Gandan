## PUB/SUB 구조의 Middleware입니다.

## RAW TCP 통신 및 Websocket을 지원하며, 상호간 연결도 편리하게 가능합니다.

## DOCKER BUILD
- docker build -t pubsub . -f ./example/mw.dockerfile
- docker run -it -d -p 8080:8080 --name pubsub pubsub
- docker exec -it pubsub /bin/bash
