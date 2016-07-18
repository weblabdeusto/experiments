/**
 * Created by gabi on 17/07/16.
 */
$(document).ready(function(){
//SOCKET MANAGEMENT
    namespace = ''; // change to an empty string to use the global namespace

    try {

        // the socket.io documentation recommends sending an explicit package upon connection
        // this is specially important when using the global namespace   + ':' + location.port + namespace
        if (DEBUG) {
            window.socket = io.connect('http://' + document.domain + ':' + location.port,
                {path: BASE_URL+"/socket.io", 'multiplex': false, 'transports': ['polling']})
                .on('connect', function () {
                    console.log('connected');
                });
        }
        else {
            window.socket = io.connect('https://' + document.domain + ':' + location.port,
                {path: BASE_URL+"/socket.io", 'multiplex': false, 'transports': ['polling']})
                .on('connect', function () {
                    console.log('connected');
                });
        }


    } catch (ex) {
        console.log("Captured exception");
        console.log(ex);
    }

    socket.on('General', function (msg) {

        console.log('recived: ' + msg.data);
    });

    socket.on('reconnect', function () {
        console.log('reconnecteeeeed');
    });

    socket.on('connect_failed', function () {
        console.log('connection failed');
    });

    socket.on('connect_error', function () {
        console.log('connection error');
    });

    socket.on('error', function () {
        console.log('error');
    });
});
