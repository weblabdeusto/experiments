
//! Displays a floating red alert box which will fade out
//! in a few seconds.
function displayErrorMessage(msg) {
    displayMessage(msg, "alert-danger")
}


//! Displays a floating alert box which will fade out
//! in a few seconds.
//!
//! @param msg Message to show in the alert box.
//! @param alertclass Class or classes to place in the alert box style.
//! It can be, for instance, any bootstrap alert class, such as alert-danger,
//! alert-success or alert-info.
//! @param time: Time to wait until it automatically fades. Optional. 3000 by default.
//! If it is 0 it will never fade.
function displayMessage(msg, alertclass, time)
{
    if(time == undefined)
        time = 3000;

    // set the message to display: none to fade it in later.
    var message = $('<div class="alert ' + alertclass + ' alert-dismissable errormessage" style="display: none;">');
    // a close button
    var close = $('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times</button>');
    message.append(close); // adding the close button to the message
    message.append(msg); // adding the error response to the message
    // add the message element to the body, fadein, wait 3secs, fadeout

    if(time > 0)
        message.appendTo($('body')).fadeIn(300).delay(3000).fadeOut(500);
    else
        message.appendTo($('body')).fadeIn(300);
}


//! Constructs a TimerManager.
//! @param timer_id: ID of the HTML tag for the timer.
TimerDisplayer = function (timer_id) {

    // Below the WARNING_THRESHOLD the value will be displayed in red.
    var WARNING_THRESHOLD = 30;

    var $timer = $("#" + timer_id);
    var _value = 0; // Value of the timer in seconds.
    var _countdownInterval = null;

    //! Hides the timer.
    //!
    this.hide = function () {
        $timer.hide();
    }

    //! Shows the timer.
    //!
    this.show = function () {
        $timer.show();
    }

    //! Starts counting down to zero automatically.
    //! @param timeChangedCallback: Callback that receives the time left as a parameter. It is called frequently
    //! but not necessarily every second. May be null.
    //! @see stopCountDown
    //!
    this.startCountDown = function (timeChangedCallback) {

        // Just in case it is already running.
        this.stopCountDown();

        _countdownInterval = setInterval(function () {
            if (_value > 0) {
                this.setTimeLeft(_value - 1);
                if (timeChangedCallback != null)
                    timeChangedCallback(_value);
            }
            else
                this.stopCountDown();
        }.bind(this), 1000);
    }


    //! Stops running the countdown.
    //! @see startCountDown
    //!
    this.stopCountDown = function () {
        if (_countdownInterval != null) {
            clearInterval(_countdownInterval);
        }
        _countdownInterval = null;
    }

    //! Updates the displayed text.
    //!
    this._updateDisplay = function () {
        var sec_num = _value;
        var hours = Math.floor(sec_num / 3600);
        var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
        var seconds = sec_num - (hours * 3600) - (minutes * 60);

        if (hours < 10) {
            hours = "0" + hours;
        }
        if (minutes < 10) {
            minutes = "0" + minutes;
        }
        if (seconds < 10) {
            seconds = "0" + seconds;
        }
        var time = hours + ':' + minutes + ':' + seconds;

        $timer.text(time);

        if (sec_num < WARNING_THRESHOLD) {
            $timer.css("color", "red");
        } else {
            $timer.css("color", "black");
        }
    }

    //! Sets the time that the timer has left.
    //! @param time New time in seconds.
    this.setTimeLeft = function (time) {
        if (time < 0)
            time = 0;

        _value = time;
        this._updateDisplay();
    }

}; // end-of TimerDisplayer


// Camera refresher. It takes the id of the image to refresh as an argument.
// When you want to start refreshing, just call start(). To stop refreshing, just call
// stop().
CameraRefresher = function (img_id) {

    var INTERVAL = 500; // Seconds to wait between image changes.

    var $img = $("#" + img_id);
    var _url;
    var _refreshingTimeout = null;


    //! Carry out initialization.
    //
    this._init = function () {
        // Ensure that the specified image exists.
        if ($img.length != 1) {
            console.error("[CameraRefresher]: The element with the tag " + img_id + " could not be found in the DOM");
            throw "Element not found";
        }
    }

    //! Sets the URL to load.
    //!
    this.setURL = function (url) {
        _url = url;
    }

    //! Refreshes the camera. If the automatic refresher has been
    //! started through start(), then this method is invoked
    //! periodically.
    this.refresh = function () {
        if (_url == undefined || _url == null)
            _url = $img.attr("src");
        $img.attr("src", this._get_timestamped_url(_url));
    };

    this._get_timestamped_url = function (url) {
        if (url.search("\\?") != -1) {
            return url + "&__ts=" + new Date().getTime();
        } else {
            return url + "?__ts=" + new Date().getTime();
        }
    };

    this._onLoad = function () {
        _refreshingTimeout = setTimeout(this.refresh.bind(this), INTERVAL);
    };

    //! Sets the number of milliseconds to wait after each image load.
    //!
    this.setInterval = function (interval) {
        INTERVAL = interval;
    }

    //! Gets the number of milliseconds to wait after each image load.
    //!
    this.getInterval = function () {
        return INTERVAL;
    }


    //! Initialization.
    this.showPlaceholder = function () {
        $img.attr("src", "img/video_placeholder.png");
    };

    //! Starts refreshing the specified URL.
    //!
    //! @param url URL to refresh. A timestamp will be appended to each request to avoid caching issues.
    //! Can be undefined or null. If undefined or null, the current image source will be used as the URL
    //! to refresh.
    this.start = function (url) {

        // If null or empty we will use the previous URL.
        if (url == undefined || url == null || url.length == 0) {
            url = $img.attr("src");
        }

        // Stop the previous refresher if it's active.
        this.stop();


        // Register the image loaded listener.
        $img.on("load", function () {
            this._onLoad();
        }.bind(this));

        _url = url;

        this.refresh();
    };

    //! Stops refreshing.
    //!
    this.stop = function () {

        // Remove the load listener.
        $img.off("load");

        if (_refreshingTimeout != null) {
            clearTimeout(_refreshingTimeout);
            _refreshingTimeout = null;
        }
    };


    // Call the ctor
    this._init();
}; // end-of CameraRefresher


$(document).ready(function(){
    timerDisplayer = new TimerDisplayer("timer");
    timerDisplayer.setTimeLeft(TIME_LEFT);
    timerDisplayer.startCountDown();
    var FIRST_CAMERA_URL = "https://cams.weblab.deusto.es/webcam/proxied.py/zumoline";
    cameraRefresher = new CameraRefresher("cam");
    cameraRefresher.start(FIRST_CAMERA_URL);


});