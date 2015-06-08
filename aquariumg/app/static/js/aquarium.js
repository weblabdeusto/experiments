function inIframe () {
    try {
        return window.self !== window.top;
    }catch (e) {
        return true;
    }
}

var poll = function poll(){

    $.ajax({ url:"/labs/aquariumg/poll", datatype: 'json', success : function(data) {
        if (data["error"]) {
            console.log('Error detected');
            if (!data["auth"]) {
                console.log('Not authenticated');
                window.location.replace(BACK_URL);
            }
        }
    }
    });
}

$(document).ready(function(){

    $("#food").click(function(){
        $.ajax({ url : "/labs/aquariumg/feed", datatype: 'json', success : function(data) {
            console.log(data["hours"]);
            if (data["error"]) {
                if(data["auth"]){
                    $("#fish-fed-block").hide();
                    $("#already-fed-block").show();
                    $("#already-fed-number").html(data["hours"]);
                    $("#already-light-block").hide();
                    $("#light-block").hide();
                }
                else{
                    window.location.replace(BACK_URL);
                } 
            }
            else {
                $("#already-fed-block").hide();
                $("#fish-fed-block").show();
                $("#already-light-block").hide();
                $("#light-block").hide();
            }
          }
        });
    });

    $("#light").click(function(data){
    $.ajax({ url : "/labs/aquariumg/light", datatype: 'json', success : function(data) {
        console.log(data);
        if (data["error"]) {
            if (data["auth"]) {
                $("#light-block").hide();
                $("#already-light-block").show();
                $("#already-fed-block").hide();
                $("#fish-fed-block").hide();
            } else {
                window.location.replace(BACK_URL);
        }
        else {
            $("#already-light-block").hide();
            $("#light-block").show();
            $("#already-fed-block").hide();
            $("#fish-fed-block").hide();
        }
      }
    });

    });

    $("#bfinish").click(function(){
        $.get("/labs/aquariumg/logout");
        window.location.replace(BACK_URL);
    });

    

    if (inIframe()) {
        $("#nav1").hide()
        $("#bfinish").show()
    }else {
        $("#nav1").show()
        $("#bfinish").hide()
    }
    var polling = setInterval(poll, 4000); 
});
