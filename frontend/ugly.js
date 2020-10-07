let ws_uri = "ws://54.91.87.192:8765";
let ws = new WebSocket(ws_uri);

ws.onmessage = function (message) {
    let resp = JSON.parse(message.data);
    switch (resp.action) {
        case 'logon':
            document.getElementById('logon_div').style.display = 'none';
            document.getElementById('room_div').style.display = 'block';
            document.getElementById('room_log').value = resp.history.join("\n");
            break;
        case 'append':
            document.getElementById('room_log').value += "\n" + resp.message;
            break;
        case 'error':
            console.error(message);
    }
};

function logon(){
    let room = document.getElementById('room').value;
    let name = document.getElementById('name').value;
    let req = {'action': 'logon', 'room': room, 'name': name};
    ws.send(JSON.stringify(req));
}

function roll(){
    let request = document.getElementById('dice').value;
    let req = {'action': 'roll', 'request': request};
    ws.send(JSON.stringify(req));
}

console.log('ready');