/**
 * Created by gabi on 17/07/16.
 */


$(document).ready(function(){
    $("#test-button").click(function(){
        socket.emit('button',{data: 'Example button pushed'});
    });
});
