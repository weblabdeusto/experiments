/**
 * Created by gabi on 15/03/16.
 */

var editor = ace.edit("editor");

function start_long_task() {
    // add task status elements
    $("#validate-btn").prop( "disabled", true );
    var status_div=$("#console");
    var panel    = $('#fixed-panel');
    status_div.append("<p>Starting validation</p>");
    panel.scrollTop(status_div.children().length*1000);

    var params = {'content':editor.getValue()};
    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: '/labs/ardublocks/compile',
        data: params,
        dataType: 'json',
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, status_div);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}
//TODO: Show if compiler is busy
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



$(document).ready(function(){

    editor.setTheme("ace/theme/dreamweaver");
    editor.getSession().setMode("ace/mode/c_cpp");
    editor.setReadOnly(true);
    editor.$blockScrolling = Infinity;

    var workspace = Blockly.inject('blocklyDiv',
    {toolbox: document.getElementById('toolbox')});

    Blockly.Arduino.Boards.changeBoard(workspace, "leonardo");

    function myUpdateFunction(event) {
        var code = Blockly.Arduino.workspaceToCode(workspace);
        editor.setValue(code);
        editor.gotoLine(1);

    }
    workspace.addChangeListener(myUpdateFunction);

    $("#validate-btn").click(function(){
       start_long_task();
    });

});
