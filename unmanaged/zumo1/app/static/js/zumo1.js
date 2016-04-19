
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

    this.init = function(){
        for(var i=0;i<DEMO_FILES.length;i++){
            this.demo_files.push(new File(DEMO_FILES[i],true))
        }
        if(USER_FILE!="None"){
            this.user_file = new File(USER_FILE,false);
            this.setActive(USER_FILE,false);
        }
        else{
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

        var callback = function(data, status, request){
            console.log(data);
        };

        $.ajax({
            url:"/loadbinary",
            type: "POST",
            data: file_data,
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };

    this.eraseMemory = function(){

        $("#stop-btn").prop( "disabled", true );
        $("#launch-btn").prop( "disabled", true );
        var status_div = $("#output");

        status_div.html("<p>Starting validation</p>");


        var callback = function(data, status, request){
            console.log(data);

        };

        $.ajax({
            url:"/eraseflash",
            type: "POST",
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };
}

$(document).ready(function(){

    file_manager = new FileManager();
    file_manager.init();

    //SOCKET MANAGEMENT
    namespace = '/zumo_backend'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('Serial data', function(msg) {
        var serialDiv = $('#serial-monitor');
        serialDiv.append('<p>'+msg.data+'</p>');
        serialDiv.scrollTop(serialDiv.children().length*1000)
    });

    socket.on('General', function(msg) {
        var serialDiv = $('#serial-monitor');
        var status_div = $("#output");
        if(msg.data=="startSerial"){
            $("#stop-btn").prop( "disabled", false );
            $("#launch-btn").prop( "disabled", false );
            socket.emit('Serial start');
            status_div.html("<p>Ready</p>");

        }
        else if(msg.data=="stopSerial"){
            status_div.html("<p>Loading binary...</p>");
            $("#stop-btn").prop( "disabled", true );
            $("#launch-btn").prop( "disabled", true );
            $("#serial-monitor").html("");
            socket.emit('close');
        }
        else{
            serialDiv.append('<p>General: ' + msg.data+'</p>');
            serialDiv.scrollTop(serialDiv.children().length*1000)
        }
    });
    // event handler for new connections

    // handlers for the different forms in the page
    // these send data to the server in a variety of ways
     $('#start-serial').click(function(event) {
        socket.emit('Serial start');
        return false;
    });

    $('#send-data').click(function(event) {
        console.log($('#serial-data').val());
        socket.emit('Serial event', {data: $("#serial-dada").val()});
        return false;
    });
    $('#close-serial').click(function(event) {
        socket.emit('close');
        return false;
    });

    $("#launch-btn").click(function(){

        if(file_manager.user_file!=null){
            if(file_manager.user_file.active){
                file_manager.loadFile(file_manager.user_file);
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

    var btn_A_div =  $("#btn-A");
    var btn_B_div =  $("#btn-B");
    var btn_C_div =  $("#btn-C");

    btn_A_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_A_div.mousedown(function(){
       $(this).attr("src", "/static/img/A-on.png");
    });
    btn_A_div.mouseup(function(){
       $(this).attr("src", "/static/img/A-off.png");
    });
     btn_A_div.mouseout(function(){
       $(this).attr("src", "/static/img/A-off.png");
    });

    btn_B_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_B_div.mousedown(function(){
       $(this).attr("src", "/static/img/B-on.png");
    });
    btn_B_div.mouseup(function(){
       $(this).attr("src", "/static/img/B-off.png");
    });
    btn_B_div.mouseout(function(){
       $(this).attr("src", "/static/img/B-off.png");
    });

    btn_C_div.on('dragstart', function(event) { event.preventDefault(); });
    btn_C_div.mousedown(function(){
       $(this).attr("src", "/static/img/C-on.png");
    });
    btn_C_div.mouseup(function(){
       $(this).attr("src", "/static/img/C-off.png");
    });
    btn_C_div.mouseout(function(){
       $(this).attr("src", "/static/img/C-off.png");
    });

});

