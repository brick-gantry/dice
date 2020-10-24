let ws_uri = "ws://54.91.87.192:8765";
let ws = null;

(function ws_connect() {
  ws = new WebSocket(ws_uri);
  ws.onmessage = ws_onmessage;
  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.');
    setTimeout(function() {
      ws_connect();
    }, 1000);
  };
  ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
})();

function ws_onmessage(message) {
    try{
        let resp = JSON.parse(message.data);
        eval("action_"+resp.action+"(resp)");
    }catch(err){
        console.error(message);
        throw err;
    }
}

function user_logon(){
    let room = document.getElementById('room').value;
    let name = document.getElementById('name').value;
    let req = {'action': 'logon', 'room': room, 'name': name};
    ws.send(JSON.stringify(req));
}

function user_roll(){
    let dice = document.getElementById('dice').value;
    let purpose = document.getElementById('purpose').value;
    let req = {'action': 'roll', 'dice': dice, 'purpose': purpose};
    ws.send(JSON.stringify(req));
}

function user_create_macro_button(){
    let dice = document.getElementById('dice').value;
    let purpose = document.getElementById('purpose').value;
    let req = {'action': 'create_macro', 'dice': dice, 'purpose': purpose};
    ws.send(JSON.stringify(req));

    // todo create after ack

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
    macro_button.onclick = function(){user_roll(dice, purpose)};
}

function action_logon(resp){
    document.getElementById('logon_div').style.display = 'none';
    document.getElementById('room_div').style.display = 'block';
    document.getElementById('dice_log').value = resp.history.map(h => h.text).join("\n");
    resp.macros.forEach(m => user_create_macro_button(m.dice, m.purpose));
}

function action_append(resp){
    document.getElementById('dice_log').value += "\n" + resp.message;
}

function action_error(resp){
    console.error(resp);
}
