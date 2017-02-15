/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true, continue: true */
/*global $, jQuery, alert */

// This file is loaded/run for all mobile interface actions/pages

$(document).ready(function() {

    // Set if we have an idevice
    var is_idevice = navigator.userAgent.toLowerCase().indexOf("ipod") != -1 || 
        navigator.userAgent.toLowerCase().indexOf("ipad") != -1 ||
        navigator.userAgent.toLowerCase().indexOf("iphone") != -1;

    // Set if we have old Android (1/2)
    var is_oldandroid = navigator.userAgent.indexOf("Android 2") != -1 ||
        navigator.userAgent.indexOf("Android 1") != -1;

    // mobile login:
    // if all the boxes were filled in (because they were passed by parameters
    // when the backend constructed the page), submit it automatically
    if ($("#loginform").size() > 0 && $("#username").val() && $("#password").val()) {
        $("#loginform").submit();
    }

    // Complete Tasks:
    // If the user sets a new diary date in the future from the dropdown, post it
    $(".diaryon").change(function() {
        $.mobile.changePage("mobile_post?posttype=dia&on=" + $(this).val() + "&id=" + $(this).attr("data"));
    });

    // View Incident:
    // If the user sets a new incident completed type, post it
    $(".completedtype").change(function() {
        var url = "mobile_post?posttype=vinccomp&ct=" + $(this).val() + "&id=" + $(this).attr("data");
        window.location = url;
    });

    // View Outstanding Test:
    // If the user chooses a test result, post it
    $(".testresult").change(function() {
        $.mobile.changePage("mobile_post?posttype=test&resultid=" + $(this).val() + 
            "&animalid=" + $(this).attr("data-animal") + "&id=" + $(this).attr("data"));
    });

    // If this is a report criteria page, attach the click handler 
    // to the submit button and run the report with the criteria
    $("#submitcriteria").click(function() {
        var post = "";
        $("select, input").each(function() {
            var t = $(this);
            var pname = t.attr("data-post");
            if (!pname) { pname = t.attr("data"); }
            if (!pname) { return; }
            if (t.hasClass("asm-currencybox")) {
                if (post != "") { post += "&"; }
                post += pname + "=" + encodeURIComponent(t.currency("value"));
            }
            else if (t.val()) {
                if (post != "") { post += "&"; }
                post += pname + "=" + encodeURIComponent(t.val());
            }
        });
        window.location = "mobile_report?" + post;    
    });

    // If this is an idevice and the file upload box is
    // disabled, it needs upgrading to iOS6 or better
    if (is_idevice && $("input[type='file']").attr("disabled")) {
        $(".tipios6").show();
    }

    // Use slide transitions for all links
    $("#home a").attr("data-transition", "slide");

});


