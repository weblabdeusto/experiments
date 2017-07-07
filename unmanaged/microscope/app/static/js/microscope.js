
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

    $.ajax({url:"/labs/flies/poll",
            datatype: 'json',
            success : callback
    });
};


var checkPosition = function(absolute,desired){


    desired.x = Math.round(desired.x*10)/10;
    desired.y = Math.round(desired.y*10)/10;
    desired.z = Math.round(desired.z*10)/10;
    console.log("abs:");
    console.log(absolute);
    console.log("des: ");
    console.log(desired);
    if(absolute.x!=desired.x || absolute.y!= desired.y || absolute.z!=desired.z){
        disable_controlls();
    }
    else{
        activate_controlls();
    }
};

var disable_controlls = function(){
    $("#button_back").prop('disabled', true);
    $("#button_front").prop('disabled', true);
    $("#button_left").prop('disabled', true);
    $("#button_right").prop('disabled', true);


};

var activate_controlls = function(){
    $("#button_back").prop('disabled', false);
    $("#button_front").prop('disabled', false);
    $("#button_left").prop('disabled', false);
    $("#button_right").prop('disabled', false);
};

function sample_manager(activeSample,samples, controller){

    this.currentSample = activeSample;
    this.samples = samples;
    this.controller = controller;

    this.workingDistance = 0;

    console.log(this.workingDistance);

    function position(){
        this.x = 0;
        this.y = 0;
        this.z = 0;
    }

    this.relativePosition = new position();

    this.init = function(){

        //this.controller.autohome();

        var z_dist = parseFloat(samples[this.currentSample].height + this.controller.workingDistance);
        var params = {
            x:samples[this.currentSample].min_x,
            y:samples[this.currentSample].min_y,
            z:z_dist,
            current_sample: this.currentSample
        };
        $("#z_position_in").val(this.controller.workingDistance);
        this.controller.move_all(params);


        $("#btn_sample"+(this.currentSample+1).toString()).addClass('btn-success').removeClass('btn-primary');

    };

    this.changeSample = function(newSample){
        console.log(typeof this.controller.inPosition);

        if(this.controller.inPosition) {
            $("#btn_sample" + (this.currentSample + 1).toString()).addClass('btn-primary').removeClass('btn-success');
            this.currentSample = newSample;
            $("#btn_sample" + (this.currentSample + 1).toString()).addClass('btn-success').removeClass('btn-primary');

            var params = {
                x: samples[newSample].min_x,
                y: samples[newSample].min_y,
                z: samples[newSample].height + this.controller.workingDistance,
                current_sample: -1
            };


            this.controller.move_all(params);

        }
    };

    this.move = function(options){

        this.controller.move(options);
    }
}


function microscopeController(samples){

    function position(){
        this.x = 0;
        this.y = 0;
        this.z = 60.2;
    }

    this.absolutPosition = new position();
    this.desiredPosition = new position();
    this.workingDistance = MAG_DIST_RATIO[20];
    this.inPosition = true;


    this.move = function(options) {

        console.log(options.dist);

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
        var dist = parseFloat(options.dist);
        dist= Math.round(dist*10)/10;
        if(options.axis=='x'){
            if(options.direction=='back'){
                if(this.absolutPosition.x > samples[options.current_sample].min_x){
                    if((this.desiredPosition.x - dist) < samples[options.current_sample].min_x)
                        dist = this.desiredPosition.x - samples[options.current_sample].min_x;
                    this.desiredPosition.x -= dist;
                }

            }
            else
            {
                if(this.absolutPosition.x < samples[options.current_sample].max_x){
                    if((this.desiredPosition.x + dist) > samples[options.current_sample].max_x)
                        dist = samples[options.current_sample].max_x - this.desiredPosition.x;
                    this.desiredPosition.x += dist;
                }

            }
        }
        else if(options.axis=='y'){
            if(options.direction=='back'){
                if(this.absolutPosition.y > samples[options.current_sample].min_y){
                    if((this.desiredPosition.y - dist) < samples[options.current_sample].min_y)
                        dist = this.desiredPosition.y - samples[options.current_sample].min_y;
                    this.desiredPosition.y -= dist;
                }

            }
            else
            {
                if(this.absolutPosition.y < samples[options.current_sample].max_y){
                    if((this.desiredPosition.y + dist) > samples[options.current_sample].max_y)
                        dist = samples[options.current_sample].max_y - this.desiredPosition.y;
                    this.desiredPosition.y += dist;
                }

            }
        }
        else{
            if(options.direction=='back'){
                if(this.absolutPosition.y > samples[options.current_sample].height){
                    if((this.desiredPosition.z - dist) < samples[options.current_sample].height)
                        dist = this.desiredPosition.z - samples[options.current_sample].height;
                    this.desiredPosition.z -= dist;
                }

            }
            else
            {
                this.desiredPosition.z += dist;
            }
        }

        params = {'axis' : options.axis, 'direction' : options.direction, 'dist' : dist, 'current_sample':options.current_sample};

        $.ajax({ type: "POST",
    //            url: '/move',
                url: '/labs/flies/move',
                data: params,
                success: callback,
                dataType: "json"
       });
    };

    this.move_all = function(options) {

        var newx;
        var newy;
        var newz;

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
        if(options.current_sample!=-1){
            if(options.x<= samples[options.current_sample].min_x)
                newx = samples[options.current_sample].min_x;
            else if(options.x>= samples[options.current_sample].max_x)
                newx = samples[options.current_sample].max_x;
            else
                newx = options.x;

            if(options.y<= samples[options.current_sample].min_y)
                newy = samples[options.current_sample].min_y;
            else if(options.y>= samples[options.current_sample].max_y)
                newy = samples[options.current_sample].max_y;
            else
                newy = options.y;

            if(options.z<= samples[options.current_sample].height)
                newz = samples[options.current_sample].height;
            else
                newz = options.z;
        }
        else{
            newx = options.x;
            newy = options.y;
            newz = options.z;
        }
        this.desiredPosition.x = options.x;
        this.desiredPosition.y = options.y;
        this.desiredPosition.z = options.z;

        console.log("DESIRED POSITION: ");
        console.log(this.desiredPosition);

        params = {
            'x' : newx,
            'y' : newy,
            'z' : newz,
            'current_sample': options.current_sample
        };

        $.ajax({ type: "POST",
                url: '/labs/flies/moveall',
                data: params,
                success: callback,
                dataType: "json"
        });
    };

    this.autohome = function(){
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

        $.ajax({url:"/labs/flies/autohome",
                datatype: 'json',
                success : callback
        });
    };

}



$(document).ready(function(){

    var controller = new microscopeController(SAMPLES);

    var manager = new sample_manager(CURRENT_SAMPLE,SAMPLES,controller);
    manager.init();

    $("#magnification_bar").on("change", function(){
        console.log(this.value);

        $("#magnification_value").html(this.value);
        console.log($('input[name=auto_manual]:checked').val());
        if($('input[name=auto_manual]:checked').val()!="manual"){
            var desired_dist = MAG_DIST_RATIO[this.value];
            console.log(typeof(desired_dist));
            $("#z_position_in").val(desired_dist);
            if(desired_dist > manager.relativePosition.z){
                var distance = desired_dist - manager.relativePosition.z;
                var direction = "forward"
            }
            else{
                var distance = manager.relativePosition.z - desired_dist;
                var direction = "back"
            }
            controller.workingDistance = desired_dist;
            console.log(distance);
            manager.move({
                axis : 'z',
                direction : direction,
                dist : distance,
                current_sample : manager.currentSample
            });
        }


    });

    $("#z_position_in").bind('keyup mouseup', function () {

        if(this.value > manager.relativePosition.z){
            var distance = this.value - manager.relativePosition.z;
            var direction = "forward"
        }
        else{
            var distance = manager.relativePosition.z - this.value;
            var direction = "back"
        }

        controller.workingDistance = parseFloat(this.value);

        console.log(distance);
        manager.move({
            axis : 'z',
            direction : direction,
            dist : distance,
            current_sample : manager.currentSample
        });
    });

    $('input[type=radio][name=auto_manual]').change(function() {
        if (this.value == 'automatic') {

            $("#z_position_in").prop('disabled', true);
            var desired_dist = parseFloat(MAG_DIST_RATIO[parseInt($('#magnification_bar').val())]);
            $("#z_position_in").val(desired_dist);

            if(desired_dist > manager.relativePosition.z){
                var distance = desired_dist - manager.relativePosition.z;
                var direction = "forward"
            }
            else{
                var distance = manager.relativePosition.z - desired_dist;
                var direction = "back"
            }
            controller.workingDistance = desired_dist;
            console.log(distance);
            manager.move({
                axis : 'z',
                direction : direction,
                dist : distance,
                current_sample : manager.currentSample
            });
        }
        else if (this.value == 'manual') {
            $("#z_position_in").prop('disabled', false);
        }
    });

     //tab box code

    $('.tabs .tab-links a').on('click', function(e)  {
        var currentAttrValue = $(this).attr('href');
            // Show/Hide Tabs
        $('.tabs ' + currentAttrValue).show().siblings().hide();
            // Change/remove current tab to active
        $(this).parent('li').addClass('active').siblings().removeClass('active');

        e.preventDefault();
    });

    $("#btn_sample1").click(function(){
        manager.changeSample(0);
    });

    $("#btn_sample2").click(function(){
        manager.changeSample(1);
    });

    $("#btn_sample3").click(function(){
        manager.changeSample(2);
    });

    $("#btn_sample4").click(function(){
        manager.changeSample(3);
    });

    $("#btn_sample5").click(function(){
        manager.changeSample(4);
    });

    $("#btn_sample6").click(function(){
        manager.changeSample(5);
    });

    $("#button_finish").click(function(){
        $.get("/labs/microscope/logout");
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
        var option = $('#XYresolution').find(":selected").text();
        manager.move({
            axis : 'x',
            direction : 'back',
            dist : option,
            current_sample : manager.currentSample
        });
    });
    $("#button_right").click(function() {
        var option = $('#XYresolution').find(":selected").text();
        manager.move({
            axis : 'x',
            direction : 'forward',
            dist : option,
            current_sample : manager.currentSample
        });
    });
    $("#button_back").click(function() {
        var option = $('#XYresolution').find(":selected").text();
        manager.move({
            axis : 'y',
            direction : 'back',
            dist : option,
            current_sample : manager.currentSample
        });
    });
    $("#button_front").click(function() {
        var option = $('#XYresolution').find(":selected").text();
        manager.move({
            axis : 'y',
            direction : 'forward',
            dist : option,
            current_sample : manager.currentSample
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
            //////TODO change image url:
            $('#pphoto').attr("src", "http://weblab.deusto.es/labs/flies/static/img/partial.jpg?timestamp=" + new Date().getTime())
        };

        $.ajax({url:"/labs/flies/photo",
            datatype: 'json',
            success : callback
        });
    });

    $("#btn_config").click(function(){

        var callback = function(data){
            console.log(data);
            if(!data["success"]){
                console.log("Error updating configuration");
                if (!data["auth"]) {
                    console.log('Not authenticated');
                    window.location.replace(BACK_URL);
                }
            }
        };
        var sample1_enabled = ($("input[name=enable1]").filter(":checked").val() === 'true');
        var height1 = parseFloat($("#height1").val());

        var sample2_enabled = ($("input[name=enable2]").filter(":checked").val() === 'true');
        var height2 = parseFloat($("#height2").val());

        var sample3_enabled = ($("input[name=enable3]").filter(":checked").val() === 'true');
        var height3 = parseFloat($("#height3").val());

        var sample4_enabled = ($("input[name=enable4]").filter(":checked").val() === 'true');
        var height4 = parseFloat($("#height4").val());

        var sample5_enabled = ($("input[name=enable5]").filter(":checked").val() === 'true');
        var height5 = parseFloat($("#height5").val());

        var sample6_enabled = ($("input[name=enable6]").filter(":checked").val() === 'true');
        var height6 = parseFloat($("#height6").val());

        var params = {'sample1' : {'enabled': sample1_enabled,'height': height1},
                      'sample2' : {'enabled': sample2_enabled,'height': height2},
                      'sample3' : {'enabled': sample3_enabled,'height': height3},
                      'sample4' : {'enabled': sample4_enabled,'height': height4},
                      'sample5' : {'enabled': sample5_enabled,'height': height5},
                      'sample6' : {'enabled': sample6_enabled,'height': height6}
        };

        $.ajax({type: "POST",
                url: '/labs/flies/updateconf',
                data: params,
                success: callback,
                dataType: "json"
        });

    });


    if (!!window.EventSource) {
        var source = new EventSource('/labs/flies/position_stream');
        source.onmessage = function(e) {
            console.log("UPDATEDDDDDDD!!!!!!!");
            var parts = e.data.split(':');
            $('#x_position').html((parts[0]-manager.samples[manager.currentSample].min_x).toFixed(1));
            $('#y_position').html((parts[1]-manager.samples[manager.currentSample].min_y).toFixed(1));
            $('#z_position').html((parts[2]-manager.samples[manager.currentSample].height).toFixed(1));
            controller.inPosition = (parts[3] == 'True');
            controller.absolutPosition.x = parts[0];
            controller.absolutPosition.y = parts[1];
            controller.absolutPosition.z = parts[2];
            manager.relativePosition.x = (parts[0]-manager.samples[manager.currentSample].min_x).toFixed(1);
            manager.relativePosition.y = (parts[1]-manager.samples[manager.currentSample].min_y).toFixed(1);
            manager.relativePosition.z = (parts[2]-manager.samples[manager.currentSample].height).toFixed(1);

        }
    }

    var polling = setInterval(poll, 4000);
//    var checker = setInterval(checkPosition,600,controller.absolutPosition,controller.desiredPosition);
});
