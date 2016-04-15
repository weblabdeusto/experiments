
/*
*  FILE LOADER
 */



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

        status_div.html("<p>Starting validation</p>");

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
            url:"/erasebinary",
            type: "POST",
            datatype: 'application/json;charset=UTF-8',
            success: callback
        });
    };
}

$(document).ready(function(){

    file_manager = new FileManager();
    file_manager.init();

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

});

