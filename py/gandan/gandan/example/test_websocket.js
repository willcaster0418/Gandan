const {WebSocket} = require("ws")

const pubsub = process.argv[2]
const topic = process.argv[3]
console.log(pubsub, topic)

ws = new WebSocket(`ws://127.0.0.1:58080/${pubsub}/${topic}`)

ws.on("open", ()=>{
	console.log("연결됨")
	for(var i = 0 ; i < 5 ; i++){
		ws.send("테스트인걸요")
	}
	ws.on("message", (event)=>{
		console.log(event.toJSON());
		console.log(event.length);
		console.log(event.toString("utf-8",0));
	})
	ws.on("error", (err)=>{
		console.log(err);
	})
})
