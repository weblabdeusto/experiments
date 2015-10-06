var first = true;

function inIframe () {
    try {
        return window.self !== window.top;
    }catch (e) {
        return true;
    }
}

var poll = function poll(){

    $.ajax({ url:"/labs/aquariumg/poll", datatype: 'json', success : function(data) {
        console.log(data);
        if (data["error"]) {
            console.log('Error detected');
            if (!data["auth"]) {
                console.log('Not authenticated');
                console.log(BACK_URL);
                window.location.replace(BACK_URL);
            }
        }
        else{
            if(data["needFood"]){
                console.log(data["lastFood"]);
                console.log('Food needed');
                seconds = parseInt(data["lastFood"]);
                hours = Math.floor(seconds/(3600)).toString();
                seconds = seconds % (3600);
                minutes = Math.floor(seconds/60).toString();
                seconds = (seconds % 60).toString();

                $("#fish-fed-block").hide();
                $("#already-fed-block").hide();
                $("#fish-needfed-block").show();
                $("#already-needfed-hours").html(hours);
                $("#already-needfed-minutes").html(minutes);
                $("#already-needfed-seconds").html(seconds);
            }
            else{
                if (first){
                    $("#fish-fed-block").show();
                    $("#already-fed-block").hide();
                    $("#fish-needfed-block").hide();
                }
            }
            if(data["lightOn"]){
                if(data["manualOn"]){
                    $("#light").hide();
                    if(first) {
                        timerDisplayer2.setTimeLeft(37);
                        timerDisplayer2.startCountDown();
                    }
                    $("#light-on-block").show();
                    $("#light-off-block").hide();
                    $("#light-info-block").hide();
                }
                else{
                    $("#light-on-block").hide();
                    $("#light-off-block").hide();
                    $("#light-info-block").show();
                    $("#light").hide();
                }
            }
            else{
                $("#light").show();
                $("#light-on-block").hide();
                $("#light-off-block").show();
                $("#light-info-block").hide();
            }
            first = false;
        }
    }
    });
};

$(document).ready(function () {

    var FIRST_CAMERA_URL = "http://cams.weblab.deusto.es/webcam/proxied.py/fishtank1";
    var STATUS_UPDATES_FREQUENCY = 2500;

    var augmentedViewEnabled = true; // To indicate in which mode we are.
    var cameraRefresher; // To help refresh the main cameras.

    var statusUpdaterTimer; //

    cameraRefresher = new CameraRefresher("cam_img");
    cameraRefresher.start(FIRST_CAMERA_URL);

    timerDisplayer2 = new TimerDisplayer("timer2");

    $("#mjpeg").click(function() {
        cameraRefresher.stop();
        $("#cam_img").attr("src", "http://cams.weblab.deusto.es/webcam/fishtank1/video.mjpeg");
        $("#jpg").show();
        $("#mjpeg").hide();
                });
    $("#jpg").click(function() {
        $("#cam_img").attr("src", "http://cams.weblab.deusto.es/webcam/proxied.py/fishtank1");
        cameraRefresher.start(FIRST_CAMERA_URL);
        $("#jpg").hide();
        $("#mjpeg").show();
    });

    $("#food").click(function(){
//        $.get("/labs/aquariumg/food", function(data, status){
//            if(data=='Fail'){
//                window.location.replace("https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=aquariumg");
//            }
//            else{  
//                alert(data);
//            }
//        });
        $.ajax({ url : "/labs/aquariumg/feed", datatype: 'json', success : function(data) {
            if (data["error"]) {
                if(data["auth"]){
                    console.log(data["seconds"]);
                    seconds = 7200 - parseInt(data["seconds"]);

                    hours = Math.floor(seconds/(3600)).toString();
                    seconds = seconds % (3600);
                    minutes = Math.floor(seconds/60).toString();
                    seconds = (seconds % 60).toString();

                    $("#fish-needfed-block").hide();
                    $("#fish-fed-block").hide();
                    $("#already-fed-block").show();
                    $("#already-fed-hours").html(hours);
                    $("#already-fed-minutes").html(minutes);
                    $("#already-fed-seconds").html(seconds);
                }
                else{
                    window.location.replace(BACK_URL);
                } 
            }
            else {
                $("#fish-needfed-block").hide();
                $("#already-fed-block").hide();
                $("#fish-fed-block").show();
            }
          }
        });
    });

    $("#light").click(function(data){

        $.ajax({ url : "/labs/aquariumg/light", datatype: 'json', success : function(data) {
            console.log(data);
            if (data["error"]) {
                if (data["auth"]) {
                    $("#light-on-block").hide();
                    $("#light-off-block").hide();
                    $("#light-info-block").show();
                } else {
                    window.location.replace(BACK_URL);
                }
            }
            else {
                $("#light").hide();
                timerDisplayer2.setTimeLeft(60);
                timerDisplayer2.startCountDown();
                setTimeout(function(){
                    $("#light-on-block").hide();
                    $("#light-off-block").show();
                    $("#light-info-block").hide();
                    $("#light").show();
                },60000);
                $("#light-on-block").show();
                $("#light-off-block").hide();
                $("#light-info-block").hide();
            }
          }
        });

    });

    $("#bfinish").click(function(){
        $.get("/labs/aquariumg/logout");
        window.location.replace(BACK_URL);
    });

    poll();
    var polling = setInterval(poll, 4000);
});
