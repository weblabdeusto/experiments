/**
 * Created by gabi on 17/07/16.
 */


$(document).ready(function(){
    //This timeout is added for ensuring socket connection is performed before user functions are declared
    setTimeout(function(){
        //Add experiment functions here

        //Data sending example
        $("#test-button").click(function(){
            socket.emit('button',{data: 'Example button pushed'});
        });

        //Data reciving example
        socket.on('Controller event',function(msg){
            console.log(msg.data);
        });

    },1000);
});
