/**
 * Created by gabi on 15/03/16.
 */

var editor = ace.edit("editor");

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
        console.log(code);
        editor.setValue(code);
        editor.gotoLine(1);

    }
    workspace.addChangeListener(myUpdateFunction);
});

