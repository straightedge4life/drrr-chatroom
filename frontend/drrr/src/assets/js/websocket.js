let host = window.location.host.split(':');
let ws_port = ':8828';
let ws_path = '/chat';
let ws_protocol = 'ws://';
if(host.length > 1){
    host.pop()
}
host = host.join(':');
let ws_host = ws_protocol + host + ws_port + ws_path;
 
let instance = new WebSocket(ws_host);

export default instance


