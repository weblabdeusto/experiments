
$(document).ready(function(){
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
        serialDiv.append('<p>General: ' + msg.data+'</p>');
        serialDiv.scrollTop(serialDiv.children().length*1000)
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
        socket.emit('Serial event', {room: 'Serial', data: $('#serial-data').val()});
        return false;
    });
    $('#close-serial').click(function(event) {
        socket.emit('close');
        return false;
    });
});