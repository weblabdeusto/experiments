function inIframe () {
    try {
        return window.self !== window.top;
    }catch (e) {
        return true;
    }
}

var poll = function poll(){
	$.get("/labs/aquariumg/poll", function(data, status){
            if(data='Fail'){
                window.location.replace("https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=aquariumg");
            }
        });
}

$(document).ready(function(){

    $("#food").click(function(){
        $.get("/labs/aquariumg/food", function(data, status){
            if(data='Fail'){
                window.location.replace("https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=aquariumg");
            }
            else{  
                alert(data);
            }
        });
    });

    $("#light").click(function(){
        $.get("/labs/aquariumg/light", function(data, status){
            if(data='Fail'){
                window.location.replace("https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=aquariumg");
            }
            else{  
                alert(data);
            }
        });
    });

    $("#logout").click(function(){
        $.get("/labs/aquariumg/logout",function(data, status){
            alert(data);
        });
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
