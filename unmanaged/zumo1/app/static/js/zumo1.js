
/**
 * FILE MANAGER
 */

function File(name,demo){
    this.name = name;
    this.active = false;
    this.demo = demo;

    if(demo){
        this.div = $("#"+name);
    }
    else{
        this.div = $("#user-"+name);
    }

    this.div.click(function(){
        console.log(name + " setting active");
        file_manager.setActive(name,demo);
    });

    this.div.mouseover(function(){
        this.style.backgroundColor = '#EEE';
    });

    this.div.mouseout(function(){
        this.style.backgroundColor = 'white';
    });
}

function FileManager(){

    this.demo_files = [];
    this.user_file = null;
    this.blockly_file = null;

    this.init = function(){
        for(var i=0;i<DEMO_FILES.length;i++){
            this.demo_files.push(new File(DEMO_FILES[i],true))
        }
        console.log(USER_BLOCKLY_FILE);
        if(USER_FILE!="None"){
            this.user_file = new File(USER_FILE,false);
            this.setActive(USER_FILE,false);
        }

        if(USER_BLOCKLY_FILE!="None"){
            this.blockly_file = new File(USER_BLOCKLY_FILE,false);
            console.log(this.blockly_file);
            if(USER_FILE=='None')
                this.setActive(USER_BLOCKLY_FILE,false);
        }
        if(USER_FILE=="None" && USER_BLOCKLY_FILE=="None"){
            if(this.demo_files.length>=1){
                this.setActive(this.demo_files[0].name,true);
            }
        }
    };

    this.setActive = function(name,demo){
        for(var i=0;i<this.demo_files.length;i++){
            if(this.demo_files[i].active==true){
                this.demo_files[i].active=false;
                this.demo_files[i].div.css("font-size", "100%");
            }
            if (this.user_file!=null){
                this.user_file.active = false;
                this.user_file.div.css("font-size", "100%");
            }
            if (this.blockly_file!=null){
                this.blockly_file.active = false;
                this.blockly_file.div.css("font-size", "100%");
            }
            if(demo){
                if(this.demo_files[i].name==name){
                    this.demo_files[i].active=true;
                    this.demo_files[i].div.css("font-size", "150%");
                }
            }
            else{
                if(this.user_file != null){
                    if(this.user_file.name==name){
                        this.user_file.active = true;
                        this.user_file.div.css("font-size", "150%");
                        return;
                    }
                }
                if(this.blockly_file != null){
                    if(this.blockly_file.name==name){
                        this.blockly_file.active = true;
                        this.blockly_file.div.css("font-size", "150%");
                    }
                }
            }
        }
    };

    this.loadFile = function(file){

        console.log(file);

        var status_div = $("#output");

        status_div.html("<p>Preparing...</p>");

        var file_data = {
            'name': file.name,
            'demo': file.demo
        };

        var callback = function(data){
            console.log(data);
            if(!data['success']){
                console.log('Error!');
                status_div.html("<p>No time for loading code...</p>");
            }
        };

        $.ajax({
            url:"/labs/zumoline/loadbinary",
            type: "POST",
            data: file_data,
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };

    this.eraseMemory = function(){

        //$("#stop-btn").prop( "disabled", true );
        $("#launch-btn").prop( "disabled", true );
        $("#btn-A").prop( "disabled", true );
        $("#btn-B").prop( "disabled", true );
        $("#btn-C").prop( "disabled", true );
        $("#send-data").prop( "disabled", true );
        var status_div = $("#output");

        status_div.html("<p>Starting validation</p>");


        var callback = function(data, status, request){
            console.log(data);

        };

        $.ajax({
            url:"/labs/zumoline/eraseflash",
            type: "POST",
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };
}

//Buttons

var turnOn = function(btn_id){

    var callback = function(data) {
            console.log(data);
        };

        $.get("/labs/zumoline/buttonon/"+ btn_id ,callback);
};

var turnOff = function(btn_id){

    var callback = function(data) {
            console.log(data);
        };

        $.get("/labs/zumoline/buttonoff/"+ btn_id ,callback);
};

$(document).ready(function(){

    file_manager = new FileManager();
    file_manager.init();
    var serialDiv = $('#serial-monitor');
    var status_div = $("#output");
    var launch_btn = $("#launch-btn");

    //SOCKET MANAGEMENT
    namespace = ''; // change to an empty string to use the global namespace

    setTimeout(function() {

        try {

            // the socket.io documentation recommends sending an explicit package upon connection
            // this is specially important when using the global namespace   + ':' + location.port + namespace
            window.socket = io.connect('http://130.206.138.16',
                {path: "/labs/zumoline/socket.io", 'multiplex': false,'transports':['polling']})
                .on('connect', function () {
                    console.log('connecteeed');
                });


        } catch (ex) {
            console.log("Captured exception");
            console.log(ex);
        }

        socket.on('General', function (msg) {

            console.log('recived: ' + msg.data);
            if (msg.data == 'ready') {
                launch_btn.prop("disabled", false);
                $("#btn-A").prop( "disabled", false );
                $("#btn-B").prop( "disabled", false );
                $("#btn-C").prop( "disabled", false );
                $("#send-data").prop( "disabled", false );
                status_div.html("<p>Ready!!</p>")
            }
            else {
                serialDiv.append('<p>General: ' + msg.data + '</p>');
                serialDiv.scrollTop(serialDiv.children().length * 1000);
            }
        });

        socket.on('reconnect', function () {
            console.log('reconnecteeeeed');
        });

        socket.on('connect_failed', function () {
            console.log('connection failed');
        });

        socket.on('connect_error', function () {
            console.log('connection error');
        });

        socket.on('error', function () {
            console.log('ERRORRRRRR');
        });

        socket.on('Serial event', function (msg) {
            console.log(msg.data);
            if (msg.data == 'ready') {
                console.log('READYYYY');
                launch_btn.prop("disabled", false);
                $("#btn-A").prop( "disabled", false );
                $("#btn-B").prop( "disabled", false );
                $("#btn-C").prop( "disabled", false );
                $("#send-data").prop( "disabled", false );
                status_div.html("<p>Ready!!</p>")
            }
            else{
                var messages = msg.data.split("\n");
                for (var i = 0; i <= messages.length; i++) {
                    if (messages[i] != undefined) {
                        serialDiv.append('<p>' + messages[i] + '</p>');
                        serialDiv.scrollTop(serialDiv.children().length * 1000)
                    }
                }
            }

        });

        $("#button_finish").click(function () {

            socket.emit('disconnect request');
            var callback = function (data) {
                window.location.replace(BACK_URL);
            };

            $.ajax({
                url: "/labs/zumoline/logout",
                datatype: "json",
                success: callback
            });

        });

        $('#send-data').click(function () {

            var value = $('#serial-dada').val();
            console.log(value);

            var params = {'content':value};

            var callback = function (data) {
                console.log(data);
            };

            $.post(
                "/labs/zumoline/sendserial",
                params,
                callback,
                "json"
            );

        });

        $('#start-serial').click(function (event) {
            socket.emit('Serial start');
            return false;
        });

        $('#close-serial').click(function (event) {
            socket.emit('Serial close');
            return false;
        });

        launch_btn.click(function(){

            launch_btn.prop( "disabled", true );
            $("#btn-A").prop( "disabled", true );
            $("#btn-B").prop( "disabled", true );
            $("#btn-C").prop( "disabled", true );
            $("#send-data").prop( "disabled", true );

            if(file_manager.user_file!=null){
                if(file_manager.user_file.active){
                    file_manager.loadFile(file_manager.user_file);
                    return;
                }
            }
            if(file_manager.blockly_file!=null){
                if(file_manager.blockly_file.active){
                    file_manager.loadFile(file_manager.blockly_file);
                    return;
                }
            }

            for(var i=0;i<file_manager.demo_files.length;i++) {
                if (file_manager.demo_files[i].active) {
                    file_manager.loadFile(file_manager.demo_files[i]);
                    break;
                }
            }
        });

    }, 1000);

    var btn_A_div =  $("#btn-A");
    var btn_B_div =  $("#btn-B");
    var btn_C_div =  $("#btn-C");

    btn_A_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_A_div.mousedown(function(){
        $(this).attr("src", "/labs/zumoline/static/img/A-on.png");
        turnOn('A');
    });
    btn_A_div.mouseup(function(){
        $(this).attr("src", "/labs/zumoline/static/img/A-off.png");
        turnOff('A');
    });
    btn_A_div.mouseout(function(){
        $(this).attr("src", "/labs/zumoline/static/img/A-off.png");
        turnOff('A');
    });

    btn_B_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_B_div.mousedown(function(){
        $(this).attr("src", "/labs/zumoline/static/img/B-on.png");
        turnOn('B');
    });
    btn_B_div.mouseup(function(){
        $(this).attr("src", "/labs/zumoline/static/img/B-off.png");
        turnOff('B');
    });
    btn_B_div.mouseout(function(){
        $(this).attr("src", "/labs/zumoline/static/img/B-off.png");
        $(this).attr("src", "/labs/zumoline/static/img/B-off.png");
        turnOff('B');
    });

    btn_C_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_C_div.mousedown(function(){
        $(this).attr("src", "/labs/zumoline/static/img/C-on.png");
        turnOn('C');
    });
    btn_C_div.mouseup(function(){
        $(this).attr("src", "/labs/zumoline/static/img/C-off.png");
        turnOff('C');
    });
    btn_C_div.mouseout(function(){
        $(this).attr("src", "/labs/zumoline/static/img/C-off.png");
        turnOff('C');
    });


});

