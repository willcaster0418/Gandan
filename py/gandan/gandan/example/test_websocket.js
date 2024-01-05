const {WebSocket} = require("ws")

const pubsub = process.argv[2]
const topic = process.argv[3]
console.log(pubsub, topic)

ws = new WebSocket(`ws://127.0.0.1:8889/${pubsub}/${topic}`)

var i = 0;
ws.on("open", ()=>{
	console.log("연결됨")
	if(pubsub == "pub" || pubsub == "PUB"){
		setInterval(function(){
			ws.send(`DATATEST ${i}`);
			i = i + 1;
			console.log("send")
		}, 100)
	}
	ws.on("message", (event)=>{
		//console.log(event.toJSON());
		//console.log(event.length);
		console.log(event.toString("utf-8",0));
	})
	ws.on("error", (err)=>{
		console.log(err);
	})
})
