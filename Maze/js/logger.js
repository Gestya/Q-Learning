//---------------------------------------------------------------------------------------
//  Logger
//---------------------------------------------------------------------------------------

const ERROR_LEVEL   = 100;
const WARNING_LEVEL = 50;
const INFO_LEVEL    = 10;
const DEBUG_LEVEL   = 0;

const logger_level  = WARNING_LEVEL;
const hide_logger   = true;


const max_num = 100;
let lines = [];


function init_logger() {
    output = document.getElementById("output");
    if (output == null) {
        alert('Div "output" not found!');
        return false;
    }
    LOGI('Div "output" has been found.');

    if (hide_logger)
        output.style.display = "none";

    LOGE('Logger Test: ERROR_LEVEL.');
    LOGW('Logger Test: WARNING_LEVEL.');
    LOGI('Logger Test: INFO_LEVEL.');
    LOGD('Logger Test: DEBUG_LEVEL.');

    return true;
}


function logging(msg) {
    if (!hide_logger) {
        output.innerHTML = '';
        lines.push(msg);
        if (lines.length > max_num)
            lines.shift();
        lines.forEach(line => output.innerHTML += line);
        output.scrollTop = output.scrollHeight;
    }
}


function LOGE(msg) {
    if (logger_level <= ERROR_LEVEL) {
        console.error("ERROR: " + msg);
        logging(`<p class="error_msg">${msg}</p>`);
    }
}


function LOGW(msg) {
    if (logger_level <= WARNING_LEVEL) {
        console.warn("WARNING: " + msg);
        logging(`<p class="warning_msg">${msg}</p>`);
    }
}


function LOGI(msg) {
    if (logger_level <= INFO_LEVEL) {
        console.log(msg);
        logging(`<p class="info_msg">${msg}</p>`);
    }
}


function LOGD(msg) {
    if (logger_level <= DEBUG_LEVEL) {
        LOGI(msg)
    }
}
