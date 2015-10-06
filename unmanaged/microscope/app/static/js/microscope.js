
function inIframe () {
    try {
        return window.self !== window.top;
    }catch (e) {
        return true;
    }
}

var poll = function() {
    var callback = function(data) {
        if (data["error"]) {
            console.log('Error detected');
        }
        if (!data["auth"]) {
            console.log('Not authenticated');
            window.location.replace(BACK_URL);
        }
    };

//    $.ajax({url:"/poll",
    $.ajax({url:"/labs/flies/poll",
            datatype: 'json',
            success : callback
    });
};

var move = function(options) {

    params = {'axis' : options.axis, 'direction' : options.direction, 'dist' : options.dist};
    var callback = function(data) {
        console.log(data);
        if (!data["success"]) {
            console.log('Error detected');
        }
        if (!data["auth"]) {
            console.log('Not authenticated');
            window.location.replace(BACK_URL);
        }
    };

   $.ajax({ type: "POST",
//            url: '/move',
            url: '/labs/flies/move',
            data: params,
            success: callback,
            dataType: "json"
   });
};

var moveall = function(options) {
//    $.ajax({ url:"/labs/microscope/poll", datatype: 'json', success : function(data) {
    params = {'x' : options.x, 'y' : options.y, 'z' : options.z};
    var callback = function(data) {
        console.log(data);
        if (!data["success"]) {
            console.log('Error detected');
        }
        if (!data["auth"]) {
            console.log('Not authenticated');
            window.location.replace(BACK_URL);
        }
    };

   $.ajax({ type: "POST",
//            url: '/moveall',
            url: '/labs/flies/moveall',
            data: params,
            success: callback,
            dataType: "json"
   });
};

var autohome = function(){
    var callback = function(data) {
        console.log(data);
        if (!data["success"]) {
            console.log('Error detected in autohome');
            if (!data["auth"]) {
                console.log('Not authenticated');
                window.location.replace(BACK_URL);
            }
        }
    };

//    $.ajax({url:"/autohome",
    $.ajax({url:"/labs/flies/autohome",
            datatype: 'json',
            success : callback
    });
};

$(document).ready(function(){

    $("#button_finish").click(function(){
        $.get("/labs/microscope/logout");
//        $.get("/logout");
        window.location.replace(BACK_URL);
    });
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
    $("#button_left").click(function() {
        var option = $('#Xresolution').find(":selected").text();
        move({
            axis : 'x',
            direction : 'back',
            dist : option
        });
    });
    $("#button_right").click(function() {
        var option = $('#Xresolution').find(":selected").text();
        move({
            axis : 'x',
            direction : 'forward',
            dist : option
        });
    });
    $("#button_back").click(function() {
        var option = $('#Yresolution').find(":selected").text();
        move({
            axis : 'y',
            direction : 'back',
            dist : option
        });
    });
    $("#button_front").click(function() {
        var option = $('#Yresolution').find(":selected").text();
        move({
            axis : 'y',
            direction : 'forward',
            dist : option
        });
    });
    $("#button_up").click(function() {
        var option = $('#Zresolution').find(":selected").text();
        move({
            axis : 'z',
            direction : 'forward',
            dist : option
        });
    });
    $("#button_down").click(function() {
        var option = $('#Zresolution').find(":selected").text();
        move({
            axis : 'z',
            direction : 'back',
            dist : option
        });
    });
    $("#autohome").click(autohome);
    $("#set").click(function(){
        moveall({
            x : $('#x_new_position').val(),
            y : $('#y_new_position').val(),
            z : $('#z_new_position').val()
        });
    });

    $("#close_partial").click(function(){
        $('#photoview').hide();
    });

    $("#stop").click(function(){
        var callback = function(data) {
            console.log(data);
            if (!data["success"]) {
                console.log('Error stopping motors');
                if (!data["auth"]) {
                    console.log('Not authenticated');
                    window.location.replace(BACK_URL);
                }
            }
        };

//      $.ajax({url:"/stop_all",
        $.ajax({url:"/labs/flies/stop_all",
            datatype: 'json',
            success : callback
        });
    });

    $("#photo").click(function(){
        var callback = function(data) {
            console.log(data);
            if (!data["success"]) {
                console.log('Error taking photo');
                if (!data["auth"]) {
                    console.log('Not authenticated');
                    window.location.replace(BACK_URL);
                }
            }
            $('#pphoto').attr("src", "http://weblab.deusto.es/labs/flies/static/img/partial.jpg?timestamp=" + new Date().getTime())
        };

//      $.ajax({url:"/stop_all",
        $.ajax({url:"/labs/flies/photo",
            datatype: 'json',
            success : callback
        });
    });


    if (inIframe()) {
        $("#button_finish").show()
        $("#nav1").hide()

    }else {
        $("#button_finish").hide()
        $("#nav1").show()
    }

    if (!!window.EventSource) {
        var source = new EventSource('/labs/flies/position_stream');
        source.onmessage = function(e) {
            var parts = e.data.split(':');
            $('#x_position').html(parts[0]);
            $('#y_position').html(parts[1]);
            $('#z_position').html(parts[2]);
        }
    }

    $('#x_new_position').val(0.0);
    $('#y_new_position').val(0.0);
    $('#z_new_position').val(0.0);
    var polling = setInterval(poll, 4000); 

});
