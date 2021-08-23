/*global $, jQuery, alert, moment */

// This file is called by the service handler for the "sign by email" functionality

$(document).ready(function() {

    "use strict";

    let h = [
        '<p><b>' + _("Signing") + ': ' + controller.notes + '</b></p>',
        '<p><a id="reviewlink" href="#">' + _("View Document") + '</a></p>',
        '<div id="review" style="display: none">',
            controller.content,
            '<hr />',
        '</div>',
        '<div id="signature"></div>',
        '<p>',
            '<button id="sig-clear" type="button">' + _("Clear") + '</button>',
            '<button id="sig-sign" type="button">' + _("Sign") + '</button>',
            '<img id="spinner" src="static/images/wait/rolling_black.svg" style="border: 0; display: none" />',
        '</p>',
        '<p>',
            _("Please click the Sign button when you are finished."),
        '</p>',
        '<p>',
        '<input type="checkbox" id="sendsigned" checked="checked" />',
        '<label for="sendsigned">',
            _("Email me a signed copy of the document at {0}").replace("{0}", email),
        '</label>',
        '</p>',
        '<p>',
            _("Once signed, this document cannot be edited or tampered with."),
        '</p>'
    ].join("\n");

    $("body").html(h);

    $("head").append([
        '<style>',
            'button {',
                'padding: 10px;',
                'font-size: 100%;',
            '}',
            '#signature {',
                'border: 1px solid #aaa;',
                'height: 200px;',
                'width: 100%%;',
                'max-width: 500px;',
            '}',
        '</style>'
    ].join("\n"));

    $("#signature").signature({ guideline: true });

    $("#sig-clear").click(function() {
        $("#signature").signature("clear");
    });

    $("#sig-sign").click(function() {
        let formdata = {
            "account":      controller.account,
            "method":       "sign_document",
            "formid":       controller.id, 
            "sig":          $("#signature canvas").get(0).toDataURL("image/png"),
            "signdate":     moment().format("YYYY-MM-DD HH:mm:ss"),
            "email":        controller.email,
            "sendsigned":   $("#sendsigned").is(":checked") ? "on" : ""
        };

        if ($("#signature").signature("isEmpty")) {
            alert("Signature is required");
            return;
        }

        $("button").fadeOut();
        $("#spinner").fadeIn();

        $.ajax({
            type: "POST",
            url: "service",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                $("body").empty().append("<p>" + _("Thank you, the document is now signed.") + "</p>");
            },
            error: function(jqxhr, textstatus, response) {
                $("body").append("<p>" + response + "</p>");
            }
        });
    });

    $("#reviewlink").click(function() {
        $("#reviewlink").fadeOut();
        $("#review").slideDown();
    });

});

