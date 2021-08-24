/*global $, jQuery, alert, moment */

// This file is called by the service handler for the "sign by email" functionality

$(document).ready(function() {

    "use strict";

    let h = [
        '<div class="container">',
        '<h2>' + _("Signing") + ': ' + controller.notes + '</h2>',
        '<button class="btn btn-success" type="button" data-bs-toggle="collapse" data-bs-target="#review" aria-expanded="false" aria-controls="review">',
        _("View Document"),
        '</button>',
        '<div id="review" class="collapse">',
            '<hr />',
            controller.content,
            '<hr />',
        '</div>',
        '<div id="signature" style="max-width: 500px; width: 100%; height: 200px; border: 1px solid #aaa;"></div>',
        '<p>',
            '<button id="sig-sign" type="button" class="btn btn-primary">' + _("Sign") + '</button>',
            '<button id="sig-clear" type="button" class="btn btn-secondary">' + _("Clear") + '</button>',
            '<img id="spinner" src="static/images/wait/rolling_black.svg" style="border: 0; display: none" />',
        '</p>',
        '<p>',
        '<label for="sendsigned">',
            '<input type="checkbox" id="sendsigned" checked="checked" />',
            _("Email me a signed copy of the document at {0}").replace("{0}", controller.email),
        '</label>',
        '</p>',
        '<p>',
            _("Once signed, this document cannot be edited or tampered with."),
        '</p>',
        '</div>'
    ].join("\n");

    $("body").html(h);

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
            alert(_("Signature is required"));
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

