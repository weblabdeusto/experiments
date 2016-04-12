
/*
*  FILE LOADER
 */


function update_progress(status_url, status_div) {
    var _this = this;
    // send GET request to status URL
    $.getJSON(status_url, function(data) {

        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        if(_this.last_status!=data['status']){
            status_div.html("<p>" + data['status']+"</p>");
            _this.last_status = data['status'];
        }
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                var result = data['result']
                // show result
                for(var i=0;i<result.length;i++){
                    status_div.html("<p>" + result+"</p>");
                }
                if(i>1){
                    status_div.html("<p style='color:red'>Error loading binary!</p>");
                }

                $("#launch-btn").prop( "disabled", false );
                $("#stop-btn").prop( "disabled", false );
            }
            else {
                // something unexpected happened
                status_div.html("<p>" + data['state']+"</p>");
                $("#launch-btn").prop( "disabled", false );
                $("#stop-btn").prop( "disabled", false );
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, status_div);
            }, 500);
        }
    });
}

/**
 * FILE MANAGER
 */

function File(name,demo){
    this.name = name;
    this.active = false;
    this.demo = demo;
    this.div = $("#"+name);

    this.div.click(function(){
        manager.setActive(name);
    });

    this.div.mouseover(function(){
        this.style.backgroundColor = '#EEE';
    });

    this.div.mouseout(function(){
        this.style.backgroundColor = 'white';
    });
}

function Manager(){

    this.demo_files = [];
    this.user_file = null;

    this.init = function(){
        for(var i=0;i<DEMO_FILES.length;i++){
            this.demo_files.push(new File(DEMO_FILES[i],true))
        }
        if(USER_FILE!="None"){
            this.user_file = new File(USER_FILE,false);
            this.setActive(USER_FILE);
        }
        else{
            if(this.demo_files.length>=1){
                this.setActive(this.demo_files[0].name);
            }
        }
    };

    this.setActive = function(name){
        for(var i=0;i<this.demo_files.length;i++){
            if(this.demo_files[i].active==true){
                this.demo_files[i].active=false;
                this.demo_files[i].div.css("font-size", "100%");
            }
            if (this.user_file!=null){
                this.user_file.active = false;
                this.user_file.div.css("font-size", "100%");
            }
            if(this.demo_files[i].name==name){
                this.demo_files[i].active=true;
                this.demo_files[i].div.css("font-size", "150%");
            }
            if(this.user_file != null){
                if(this.user_file.name==name){
                    this.user_file.active = true;
                    this.user_file.div.css("font-size", "150%");
                }
            }
        }
    };

    this.loadFile = function(file){

        console.log(file);

        $("#launch-btn").prop( "disabled", true );
        $("#stop-btn").prop( "disabled", true );
        var status_div = $("#output");

        status_div.html("<p>Loading binary</p>");

        var file_data = {
            'name': file.name,
            'demo': file.demo
        };

        var callback = function(data, status, request){
            console.log(data);
            status_url = request.getResponseHeader('Location');
            console.log('HELLOOOO');
            console.log(status_url);
            update_progress(status_url, status_div);
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

        status_div.html("<p>Stopping</p>");


        var callback = function(data, status, request){
            console.log(data);
            status_url = request.getResponseHeader('Location');
            console.log(status_url);
            update_progress(status_url, status_div);
        };

        $.ajax({
            url:"/erasebinary",
            type: "POST",
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };
}

$(document).ready(function(){

    manager = new Manager();
    manager.init();

    $("#launch-btn").click(function(){
        if(manager.user_file!=null){
            if(manager.user_file.active){
                manager.loadFile(manager.user_file);
                return;
            }
        }

        for(var i=0;i<manager.demo_files.length;i++) {
            if (manager.demo_files[i].active) {
                manager.loadFile(manager.demo_files[i]);
                break;
            }
        }

    });
    $("#stop-btn").click(function(){
        manager.eraseMemory();
    });

});

