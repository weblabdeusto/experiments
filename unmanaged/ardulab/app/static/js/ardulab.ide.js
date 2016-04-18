/**
 * Created by gabi on 15/03/16.
 */


//TODO: functions to launch binary on hardware



//------------------------------------//
//------------- COMPILER -------------//
//------------------------------------//

function start_long_task() {
    // add task status elements
    $("#validate-btn").prop( "disabled", true );
    var status_div=$("#console");
    var panel    = $('#fixed-panel');
    status_div.append("<p>Starting validation</p>");
    panel.scrollTop(status_div.children().length*1000);


    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: '/labs/ardulab/compile',
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, status_div);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}

function update_progress(status_url, status_div) {
    var _this = this;
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        var panel    = $('#fixed-panel');
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        if(_this.last_status!=data['status']){
            //status_div.append("<p>" + data['status']+"</p>");
            _this.last_status = data['status'];
            panel.scrollTop(status_div.children().length*1000);
        }
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                var result = data['result'].split("%%%");
                // show result
                for(var i=0;i<result.length;i++){
                    status_div.append("<p>" + result[i]+"</p>");
                }
                if(i>1){
                    status_div.append("<p style='color:red'>Error Compiling!</p>");
                }
                panel.scrollTop(status_div.children().length*1000);
                $("#validate-btn").prop( "disabled", false );
            }
            else {
                // something unexpected happened
                //status_div.append("<p>" + data['state']+"</p>");
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


//------------------------------------//
//---------- FILE MANAGER ------------//
//------------------------------------//

var loadFile = function(file){
};

File = function(name,content,session){
    this.name = name;
    this.content = content;
    this.session = session;
    this.active_file = false;
    this.saved = true;
    this.div = $("#"+name);

    var name = this.name;

    this.session.on("change",function(){
        console.log(name +" changed");
        file_manager.setUnsaved(name);
    });

};

fileManager = function(user_path){

    this.files = [];

    this.active_file = "";
    this.file_cont = $(".files").children().length;
    this.user_path = user_path;
    this.ready=false;

    this.init = function(user_path){
        var user_dir = user_path;
        var _this=this;
        //TODO: init file content with ajax calls
        var f = $(".files");
        this.file_cont =f.children().length;

        var files = f.find(".file-name");

        console.log("init");
        console.log(files);
        for(var i= 0;i<this.file_cont;i++){


            var cont = 0;

            var callback = function(data) {
                var response = data;

                _this.files.push(new File(response.name,response.content, ace.createEditSession(response.content, "ace/mode/c_cpp")));
                if (cont == 0) {
                    _this.setActive(response.name);
                }

                cont = cont + 1;
                console.log(_this.files);
            };
            console.log(files[i].innerHTML);
            $.get("/labs/ardulab/content/" + files[i].innerHTML ,callback);
        }

    };

    this.getSessionValue = function(filename){

        for(var i=0;i<this.files.length;i++){
            if(this.files[i].name==filename){
                return this.files[i].session.getValue();
            }
        }
        return "";
    };

    this.setSaved = function(filename){
        var f = $(".files");
        this.file_cont = f.children().length;
        var files = f.find(".file-name");
        for(var i=0;i<this.files.length;i++) {
            if (this.files[i].name==filename) {
                this.files[i].saved = true;
                for(var j=0;j<this.file_cont;j++){
                    if(files[j].innerHTML==this.files[i].name){
                        if(this.files[i].active_file){
                            //files[j].style = "color:#333;font-size: 150%";
                            files[j].style.color = "#333";
                            files[j].style.fontSize = "150%";
                        }

                        else{
                            //files[j].style = "color:#333;font-size: 100%";
                            files[j].style.color = "#333";
                            files[j].style.fontSize = "100%";
                        }

                        break;
                    }
                }
                break;
            }
        }
    };

    this.setUnsaved = function(filename){
        var f = $(".files");
        this.file_cont = f.children().length;
        var files = f.find(".file-name");

        for(i=0;i<this.files.length;i++) {
            if (this.files[i].name==filename) {
                this.files[i].saved = false;
                for(var j=0;j<this.file_cont;j++){
                    if(files[j].innerHTML==this.files[i].name){
                        if(this.files[i].active_file){
                            //files[j].style = "color:#F00;font-size: 150%";
                            files[j].style.color = "#F00";
                            files[j].style.fontSize = "150%";
                        }

                        else{
                            //files[j].style = "color:#F00;font-size: 100%";
                            files[j].style.color = "#F00";
                            files[j].style.fontSize = "100%";
                        }
                        break;
                    }
                }
                break;
            }
        }
    };


    this.setActive = function(filename){
        var i=0;

        var f = $(".files");
        this.file_cont = f.children().length;
        var files = f.find(".file-name");

        for(i=0;i<this.files.length;i++){
            if(this.files[i].active_file){
                this.files[i].content = this.files[i].session.getValue();
                this.files[i].active_file = false;
                for(var j=0;j<this.file_cont;j++){
                    if(files[j].innerHTML==this.files[i].name){
                        if(this.files[i].saved){
                            //files[j].style = "color: #333;font-size: 100%";
                            files[j].style.color = "#333";
                            files[j].style.fontSize = "100%";
                        }

                        else
                            //files[j].style = "color: #F00;font-size: 100%";
                            files[j].style.color = "#F00";
                            files[j].style.fontSize = "100%";
                        break;
                    }
                }

            }
        }
        for(i=0;i<this.files.length;i++) {

            if (this.files[i].name == filename) {
                editor.setSession(this.files[i].session);
                //editor.setValue(this.files[i].content);
                this.files[i].active_file = true;
                for (j = 0; j < this.file_cont; j++) {
                    if (files[j].innerHTML == this.files[i].name) {
                        if (this.files[i].saved){
                            //files[j].style = "color: #333;font-size: 150%";
                            files[j].style.color = "#333";
                            files[j].style.fontSize = "150%";
                        }
                        else
                            //files[j].style = "color: #F00;font-size: 150%";
                            files[j].style.color = "#F00";
                            files[j].style.fontSize = "150%";
                    break;
                    }
                }
                break;
            }
        }

        editor.gotoLine(1);
    };

    this.getFileContent = function(filename){

        var _this=this;
        var filename = filename;
        //TODO: init file content with ajax calls

        var f = $(".files");

        this.file_cont =f.children().length;

        var files = f.find(".file-name");
        var i=0;
        var callback = function(data) {
            var response = data;
            _this.files.push(new File(response.name ,response.content, ace.createEditSession(response.content, "ace/mode/c_cpp")));

            if(_this.files.length==1){

                _this.setActive(_this.files[0].name);
            }
            console.log(_this.files);
        };

        for (i;i<this.file_cont;i++){
            if(files[i].innerHTML==filename){
                break;
            }
        }
        $.get("/labs/ardulab/content/"+ files[i].innerHTML ,callback);
    };

    this.saveFiles = function(){
        var _this = this;
        var cont = 0;

        for(var i=0;i<this.files.length;i++){
            var params = {'content':this.getSessionValue(this.files[i].name)};

            var callback = function(data){
                console.log(data);
                console.log(_this.files[cont].name+" saved");
                _this.setSaved(_this.files[cont].name);
                cont=cont+1;

            };

            $.post(
                "/labs/ardulab/save/"+file_manager.files[i].name,
                params,
                callback,
                "json"
            );

        }
    };

    this.deleteFileConent = function(filename){
        var _filename = filename;
        var _this=this;
        //TODO: init file content with ajax calls

        var i=0;

        var files = $(".files").find(".file-name");

        for (i;i<this.files.length;i++){
            if(this.files[i].name==_filename){
                if(this.files[i].active_file) {
                    if(this.files.length>1) {
                        if (this.files.length == i+1) {

                            this.setActive(this.files[i - 1].name);
                        }
                        else {
                            this.setActive(this.files[i + 1].name);
                        }
                    }
                    else{
                        this.files = [];
                        editor.setValue("");
                    }
                }
                this.files.splice(i, 1);
                break;
            }
        }
        if(files.length==0){
            editor.setValue("");
            this.files = [];
        }
        console.log(this.files);



    };

    this.addFile = function(filename){
        var _this = this;
        var quote = '"';
        var row_content =
            "<tr class='template-download fade in'>"+
                "<td id='"+filename+"' width='65%' class='file' onclick='loadFile("+ quote.concat(filename.concat(quote)) +")'>"+
                    "<p class='name'>"+
                        "<span class='file-name'>"+ filename +"</span>"+
                    "</p>"+
                "</td>"+
                "<td width='35%'>"+
                    "<a class='btn btn-success' href='data/"+ filename + "' title='"+ filename +"' download='"+ filename +"'>"+
                        "<i class='glyphicon glyphicon-download'></i>"+
                    "</a>"+
                    "<button class='btn btn-danger delete' style='margin-left:4%' data-type='DELETE' data-url='delete/"+filename+"'>"+
                        "<i class='glyphicon glyphicon-trash'></i>"+
                    "</button>"+
                "</td>"+
             "</tr>";

        var callback = function(data){

            console.log(data);

            $("#add-modal").modal('toggle');

            //TODO:Show message to user
            if (data["error"]){
                console.log("Error creating file!")
            }
            else{
                console.log("Ceating new file:");
                console.log(filename);
                $(".files").append(row_content);
                _this.files.push(new File(filename ,"", ace.createEditSession("", "ace/mode/c_cpp")));
                console.log(_this.files);
                if(_this.files.length==1){
                    _this.setActive(filename);
                }
            }


        };

        var url = "/labs/ardulab/newfile/"+ filename;

        $.get(url,callback);
    }
};

var editor = ace.edit("editor");
var file_manager = new fileManager(USER_FOLDER);


$(window).load(function(){

    editor.setTheme("ace/theme/dreamweaver");
    editor.getSession().setMode("ace/mode/c_cpp");
    editor.$blockScrolling = Infinity;
    var init = function(){
        file_manager.init(USER_FOLDER);
    };
    setTimeout(init,500);



    loadFile = function(file_name){
        file_manager.setActive(file_name);
    };

    $("#create-file-btn").click(function(){
        var name = $('[name=file-name]').val();
        var extension = $("#new-file-extension").val();
        var filename = name+"."+extension;
        file_manager.addFile(filename);
    });

    $("#save-btn").click(function(){
        file_manager.saveFiles();
    });

    $("#validate-btn").click(function(){
        start_long_task();
    });


});