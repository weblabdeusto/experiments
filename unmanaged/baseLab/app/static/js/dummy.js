/**
 * Created by gabi on 17/07/16.
 */


$(document).ready(function(){

    //Data sending example
    $("#test-button").click(function(){
        socket.emit('button',{data: 'Example button pushed'});
    });

    //Data reciving example
    socket.on('Controller event',function(msg){
        console.log(msg.data);
    });
});
