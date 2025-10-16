var ajaxRequestQueue = [];
var ajaxRequestRunning = false;

var vidNormal, vidFlipped, gbVidNormal, gbVidFlipped, printPreview, countdown, footer;
var boothStatus = -1;

function ajax(url, success, fail, always, binary) {
    var request = new XMLHttpRequest();
    if (binary === true)
        request.responseType = "arraybuffer";
    request.open('GET', url, true);
    request.timeout = 3000;

    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            var next = ajaxRequestQueue.shift();
            if (next) {
                setTimeout(function(){next.send()}, 10);
            } else
                ajaxRequestRunning = false;
            if (request.status >= 200 && request.status < 400) {
                if (typeof success !== 'undefined')
                    if (binary === true)
                        success(new Uint8Array(request.response));
                    else
                        success(JSON.parse(request.responseText));
            } else {
                if (typeof fail !== 'undefined')
                    fail();
            }
            if (typeof always !== 'undefined')
                always();
        }
    };

    if (ajaxRequestRunning)
        ajaxRequestQueue.push(request);
    else {
        ajaxRequestRunning = true;
        request.send();
    }
}

function pollStatus() {
    ajax("/status?" + (new Date()).getTime(),
    function(data) { //success
        newStatus = (boothStatus != data["status"]);
        document.body.classList.remove("status"+boothStatus);
        boothStatus = data["status"];
        document.body.classList.add("status"+boothStatus);
        switch(boothStatus) {
            case 0: //Idle
                if (newStatus) {
                    instructions.classList.remove("active");
                    countdown.classList.remove("active");
                    vidNormal.classList.remove("blocked");
                    vidFlipped.classList.remove("blocked");
                    gbVidNormal.classList.remove("blocked");
                    gbVidFlipped.classList.remove("blocked");
                    printPreview.classList.remove("active");
                    showRandom();
                    footer.innerHTML = "<span class=\"green\">Grün</span> drücken um zu starten.";
                }
                break;
            case 1: //Instructions
                if (newStatus) {
                    instructions.classList.add("active");
                    countdown.classList.remove("active");
                    vidNormal.classList.remove("active");
                    vidFlipped.classList.remove("active");
                    gbVidNormal.classList.remove("active");
                    gbVidFlipped.classList.remove("active");
                    printPreview.classList.remove("active");
                    vidNormal.classList.add("blocked");
                    vidFlipped.classList.add("blocked");
                    gbVidNormal.classList.add("blocked");
                    gbVidFlipped.classList.add("blocked");
                    footer.innerHTML = "<span class=\"green\">grün</span>: Start<span class=\"red\" style=\"margin-left: 4em\">rot</span>: Abbrechen";
                }
                break;
            case 2: //Countdown
                if (newStatus) {
                    footer.innerHTML = "Macht euch bereit...";
                    countdown.classList.add("active");
                    instructions.classList.remove("active");
                    vidNormal.classList.remove("active");
                    vidFlipped.classList.remove("active");
                    gbVidNormal.classList.remove("active");
                    gbVidFlipped.classList.remove("active");
                    printPreview.classList.remove("active");
                    vidNormal.classList.add("blocked");
                    vidFlipped.classList.add("blocked");
                    gbVidNormal.classList.add("blocked");
                    gbVidFlipped.classList.add("blocked");
                }
                countdown.innerHTML = Math.ceil(data["timeRef"] - Date.now()/1000.0);
                break;
            case 3: //Recording
                if (newStatus) {
                    footer.innerHTML = "Aufnahme läuft!";
                    countdown.classList.add("active");
                }
                countdown.innerHTML = Math.ceil(data["timeRef"] + data["duration"] - Date.now()/1000.0);
                break;
            case 4: //Downloading
                if (newStatus) {
                    footer.innerHTML = "Vorschau wird erzeugt...";
                    countdown.classList.add("active");
                }
                countdown.innerHTML = Math.ceil(data["timeRef"] + data["finish"] - Date.now()/1000.0);
                break;
            case 5: //Decision Keep
                if (newStatus) {
                    vidNormal.classList.remove("blocked");
                    vidFlipped.classList.remove("blocked");
                    gbVidNormal.classList.remove("blocked");
                    gbVidFlipped.classList.remove("blocked");
                    showPreview();
                    footer.innerHTML = "<span class=\"green\">grün</span>: Aufnahme behalten<br /><span class=\"red\">rot</span>: Aufnahme verwerfen";
                    countdown.classList.remove("active");
                }
                break;
            case 6: //Decision Print
                if (newStatus) {
                    vidNormal.classList.add("blocked");
                    vidFlipped.classList.add("blocked");
                    gbVidNormal.classList.add("blocked");
                    gbVidFlipped.classList.add("blocked");
                    showPrintPreview();
                    footer.innerHTML = "<span class=\"green\">grün</span>: Erinnerung drucken<br /><span class=\"red\">rot</span>: Nicht drucken";
                    countdown.classList.remove("active");
                }
                break;
            case 7: //Error
                if (newStatus) {
                    footer.innerHTML = "Sorry, es gab ein Problem und ich versuche es selbst zu beheben. Wenn es immer wieder auftaucht oder diese Meldung in einer Minute nicht verschwindet, müsst ihr wohl Sebastian holen...";
                    instructions.classList.remove("active");
                    countdown.classList.remove("active");
                    vidNormal.classList.remove("active");
                    vidFlipped.classList.remove("active");
                    gbVidNormal.classList.remove("active");
                    gbVidFlipped.classList.remove("active");
                    printPreview.classList.remove("active");
                    vidNormal.classList.add("blocked");
                    vidFlipped.classList.add("blocked");
                    gbVidNormal.classList.add("blocked");
                    gbVidFlipped.classList.add("blocked");
                }
                break;
            default:
                console.log("Dafuck?");
        }
    },
    function () { //fail
    },
    function () { //always
        setTimeout(pollStatus, 100);
    });
}

function flipPreview(nextVideo, oldVideo, gbNextVideo, gbOldVideo) {
    nextVideo.currentTime = 0;
    gbNextVideo.currentTime = 0;
    nextVideo.classList.add("active");
    gbNextVideo.classList.add("active");
    oldVideo.classList.remove("active");
    gbOldVideo.classList.remove("active");
    nextVideo.play();
    gbNextVideo.play();
}

function flipRandom(nextVideo, oldVideo, gbNextVideo, gbOldVideo) {
    nextVideo.classList.add("active");
    gbNextVideo.classList.add("active");
    oldVideo.classList.remove("active");
    gbOldVideo.classList.remove("active");
    nextVideo.play();
    gbNextVideo.play();
    let t = (new Date()).getTime();
    oldVideo.src = "/random?i=" + t;
    oldVideo.load()
    gbOldVideo.src = "/randomGB?i=" + t;
    gbOldVideo.load()
}

function vidNormalEnded() {
    if (boothStatus == 0) {//idle, show randoms
        flipRandom(vidFlipped, vidNormal, gbVidFlipped, gbVidNormal);
    } else if (boothStatus == 5) {//Decision, showing preview
        flipPreview(vidFlipped, vidNormal, gbVidFlipped, gbVidNormal);
    }
}

function vidFlippedEnded() {
    if (boothStatus == 0) {//idle, show randoms
        flipRandom(vidNormal, vidFlipped, gbVidNormal, gbVidFlipped);
    } else if (boothStatus == 5) {//Decision, showing preview
        flipPreview(vidNormal, vidFlipped, gbVidNormal, gbVidFlipped);
    }
}

function showPreview() {
    url = "/preview?" + (new Date()).getTime();
    vidNormal.src = url;
    vidNormal.load();
    vidFlipped.src = url;
    vidFlipped.load();
    url = "/previewGB?" + (new Date()).getTime();
    gbVidNormal.src = url;
    gbVidNormal.load();
    gbVidFlipped.src = url;
    gbVidFlipped.load();
    vidNormal.classList.add("active");
    vidFlipped.classList.remove("active");
    gbVidNormal.classList.add("active");
    gbVidFlipped.classList.remove("active");
    printPreview.classList.remove("active");
    vidNormal.play();
    gbVidNormal.play();
}

function showPrintPreview() {
    url = "/printpreview?" + (new Date()).getTime();
    printPreview.src = url;
    printPreview.classList.add("active");
    vidNormal.classList.remove("active");
    vidFlipped.classList.remove("active");
    gbVidNormal.classList.remove("active");
    gbVidFlipped.classList.remove("active");
}

function showRandom() {
    let t = (new Date()).getTime();
    vidNormal.src = "/random?i=2" + t;
    vidNormal.load();
    vidFlipped.src = "/random?i=1" + t;
    vidFlipped.load();
    gbVidNormal.src = "/randomGB?i=2" + t;
    gbVidNormal.load();
    gbVidFlipped.src = "/randomGB?i=1" + t;
    gbVidFlipped.load();
    vidNormal.classList.add("active");
    vidFlipped.classList.remove("active");
    gbVidNormal.classList.add("active");
    gbVidFlipped.classList.remove("active");
    printPreview.classList.remove("active");
    vidNormal.play();
    gbVidNormal.play();
}

var debounceTime = 0
function onKey(event) {
    now = (new Date()).getTime();
    if (now < debounceTime)
        return;
    debounceTime = now + 500;
    if (event.key == " ") {
        ajax('/control?cmd=ok');
    } else if (event.key === "Escape") {
        ajax('/control?cmd=abort');
    }
}

function ready(fn) {
    if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading") {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function() {
    vidNormal = document.getElementById("vidNormal");
    vidFlipped = document.getElementById("vidFlipped");
    gbVidNormal = document.getElementById("gbVidNormal");
    gbVidFlipped = document.getElementById("gbVidFlipped");
    vidNormal.addEventListener('ended', vidNormalEnded, false);
    vidFlipped.addEventListener('ended', vidFlippedEnded, false);
    printPreview = document.getElementById("printPreview");
    countdown = document.getElementById("countdown");
    footer = document.getElementById("footer");
    pollStatus();
    document.onkeydown = onKey;
});
