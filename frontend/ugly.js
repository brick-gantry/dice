let ws_uri = "ws://54.91.87.192:8765";
let ws = null;

(function connect() {
  ws = new WebSocket(ws_uri);
  ws.onmessage = ws_onmessage;
  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.');
    setTimeout(function() {
      connect();
    }, 1000);
  };
  ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
})();

function ws_onmessage(message) {
    let resp = JSON.parse(message.data);
    switch (resp.action) {
        case 'logon':
            document.getElementById('logon_div').style.display = 'none';
            document.getElementById('room_div').style.display = 'block';
            document.getElementById('dice_log').value = resp.history.map(h => h.text).join("\n");
            resp.macros.forEach(m => create_macro_button(m.dice, m.purpose));
            break;
        case 'append':
            document.getElementById('dice_log').value += "\n" + resp.message;
            break;
        case 'append_chat':
            document.getElementById('chat_log').value += "\n" + resp.message;
            break;
        case 'display_error':
            document.getElementById('dice_log').value += "\n" + resp.error;
            break;
        case 'error':
            console.error(message);
            break;
    }
}

function logon(){
    let room = document.getElementById('room').value;
    let name = document.getElementById('name').value;
    let req = {'action': 'logon', 'room': room, 'name': name};
    ws.send(JSON.stringify(req));
}

function roll(dice, purpose){
    dice = dice || document.getElementById('dice').value;
    purpose = purpose || document.getElementById('purpose').value;
    let req = {'action': 'roll', 'dice': dice, 'purpose': purpose};
    ws.send(JSON.stringify(req));
}

function create_macro_button(dice, purpose){
    dice = dice || document.getElementById('dice').value;
    purpose = purpose || document.getElementById('purpose').value;
    let req = {'action': 'create_macro', 'dice': dice, 'purpose': purpose};
    ws.send(JSON.stringify(req));

    let macros_div = document.getElementById('macros');
    let macro_div = document.getElementById('macro_'+purpose+'_div');
    let macro_button = document.getElementById('macro_' + purpose);
    let macro_delete_button = document.getElementById('macro_' + purpose + '_delete');
    if(!macro_div){
        macro_div = document.createElement('div');
        macro_button = document.createElement('button');
        macro_delete_button = document.createElement('button');
        macro_div.appendChild(macro_button);
        macro_div.appendChild(macro_delete_button);
        macros_div.appendChild(macro_div);
        
        macro_div.id = 'macro_'+purpose+'_div';
        macro_button.id = 'macro_' + purpose;
        macro_delete_button.id = 'macro_' + purpose + '_delete';

        macro_delete_button.innerText = "X";
        macro_delete_button.onclick = function(){
            let req = {'action': 'delete_macro', 'dice': dice, 'purpose': purpose};
            ws.send(JSON.stringify(req));
            macros_div.removeChild(macro_div);
        };
    }
    macro_button.innerText = purpose+" ("+dice+")";
    macro_button.onclick = function(){roll(dice, purpose)};
}
