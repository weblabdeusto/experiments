/**
 * Created by gabi on 17/07/16.
 */
/**
 * Created by gabi on 29/02/16.
 */
var poll = function() {
    var callback = function(data) {
        if (data["error"]) {
            console.log('Error detected');
        }
        if (!data["auth"]) {
            console.log('Not authenticated');
            window.location.replace(BACK_URL);
        }

    };

    $.ajax({url:BASE_URL+"/poll",
            datatype: 'json',
            success : callback
    });
};



$(document).ready(function(){

    $("#button_finish").click(function(){

        var callback = function(data) {

            window.location.replace(BACK_URL);
        };

        $.ajax({
            url: BASE_URL + "/logout",
            datatype: "json",
            success: callback
        });

    });
    var polling = setTimeout(setInterval(poll, 4000),5000);
});