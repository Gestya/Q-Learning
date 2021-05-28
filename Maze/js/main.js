// ---------------------------------------------------------------------------------------
//      Global variables
// ---------------------------------------------------------------------------------------

var socket = null;
var world = null;
var noisy = Settings.noisy_moving;


// ---------------------------------------------------------------------------------------
//      WebSoclet Event Handlers
// ---------------------------------------------------------------------------------------

function ws_onOpen(event) {
    LOGI('[ws_open] WebSocket is open now.');
}

function ws_onMessage(event) {
    LOGI("[ws_message] " + event.data);
    world.onMessaage(event.data)
}

function ws_onClose(event) {
    if (event.code == 1000)
        LOGI('[ws_close] Connection is closed');
    else
        LOGI('[ws_close] Connection died, code=' + event.code + ' reason="' + event.reason + '"');
}

function ws_onError(event) {
    LOGE('[ws_error] WebSocket error observed: ' + error.message);
}

function ws_send(msg) {
    LOGI('[ws_send] ' + msg);
    socket.send(msg);
}


// ---------------------------------------------------------------------------------------

function init() {
    if (!init_logger())
        return false;

    scene = document.getElementById("scene");
    if (scene == null) {
        alert('Div "scene" not found!');
        return false;
    }
    LOGI('Div "scene" has been found.');

    document.getElementById('noisy').value = noisy

    return true;
}

// ---------------------------------------------------------------------------------------

function main() {
    if (!init())
        return;

    // --- WebSocket -------------------------------------
    LOGI('Create WebSocet-Client...');
    LOGI('. protocol: ' + Settings.ws_protocol);
    LOGI('. host: ' + Settings.ws_host);
    LOGI('. port: ' + Settings.ws_port);
    let addr = Settings.ws_protocol + Settings.ws_host + ':' + Settings.ws_port;

    socket = new WebSocket(addr);

    socket.onopen = function(event) { ws_onOpen(event); }
    socket.onmessage = function(event) { ws_onMessage(event); }
    socket.onclose = function(event) { ws_onClose(event); }
    socket.onerror = function(event) { ws_onError(event); }

    // --- World -----------------------------------------
    world = new World(scene);
    let initial_world_state = world.getWorldState;
    world.start();

    // --- Notify the Server -----------------------------
    setTimeout(function(){ ws_send( initial_world_state ); }, 500);
}

// ---------------------------------------------------------------------------------------

function keyProcessor(event, state) {
    if (world != null)
        world.onKey(event, state);
}

function applyNoisy() {
    let obj = document.getElementById('noisy');
    let value = obj.value;
    if (!isNaN(value)) {
        noisy = obj.value < 0.0 ? 0.0 : (obj.value > 1.0 ? 1.0 : obj.value);
    }
    obj.value = noisy;
}