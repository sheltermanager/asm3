/*global $, controller, */

// This file is called by the service handler for the "adoption checkout" functionality

$(document).ready(function() {

    "use strict";

    const show_dlg = function(title, body) {
        $("#validation-title").html(title);
        $("#validation-text").html(body);
        $("#validation-dlg").modal("show");
    };

    let h = [
        '<div class="modal fade" id="validation-dlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="validation-title" aria-hidden="true">',
            '<div class="modal-dialog">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="validation-title">Error</h5>',
                        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                    '</div>',
                    '<div id="validation-text" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',

        '<div id="pane-review" class="container text-center">',
        '<h2 class="mt-3">' + _("Review") + ' (1/3)</h2>',
        '<div class="mb-3">',
            '<img src="service?account=' + controller.database + '&method=animal_image&animalid=' + controller.animalid + 
                '" style="width: 100%; max-width: 300px" />',
        '</div>',
        '<div class="form-group">',
        '<h3>' + controller.animalname + '</h3>',
        '<p>' + controller.sex + ' ' + controller.speciesname + ' ' + controller.age + '</p>',
        '<p>' + _("Adoption Fee") + ': <b>' + controller.formatfee + '</b></p>',
        '</div>',
        '<div>',
            '<button id="btn-next" type="button" class="btn btn-primary">',
                _("Next"),
                '<i class="bi-arrow-right-circle"></i>',
            '</button>',
        '</div>',
        '</div>',

        '<div id="pane-sign" class="container text-center" style="display: none">',
        '<form>',
        '<h2 class="mt-3">' + _("Sign adoption paperwork") + ' (2/3)</h2>',
        '<div class="accordion" id="accordion-paperwork">',
            '<div class="accordion-item">',
                '<h2 class="accordion-header" id="header-paperwork">',
                '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-paperwork" aria-expanded="true" aria-controls="collapse-paperwork">',
                _("View"),
                '</button>',
                '</h2>',
                '<div id="collapse-paperwork" class="accordion-collapse collapse" aria-labelledby="heading-paperwork" data-bs-parent="#accordion-paperwork">',
                    '<div class="accordion-body">',
                    controller.mediacontent,
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<div id="signature" style="margin-left: auto; margin-right: auto; max-height: 300px; max-width: 800px; width: 95vw; height: 70vh; border: 1px solid #aaa;"></div>',
        '<div class="mb-3">',
            '<small class="text-muted">' + _("Once signed, this document cannot be edited or tampered with.") + '</small>',
        '</div>',
        '<div class="form-group">',
            '<label for="sendsigned" class="form-label">',
                '<input type="checkbox" id="sendsigned" checked="checked" />',
                _("Email me a signed copy of the document at {0}").replace("{0}", controller.email),
            '</label>',
        '</div>',
        '<div class="form-group">',
            '<button id="btn-clear" type="button" class="btn btn-secondary">',
                '<i class="bi-x"></i>',
                _("Clear"),
                '</button>',
            '<button id="btn-sign" type="button" class="btn btn-primary">',
                '<i class="bi-vector-pen"></i>',
                _("Sign"),
                '</button>',
        '</div>',
        '</form>',
        '</div>',

        '<div id="pane-donate" class="container text-center" style="display: none">',
        '<form>',
        '<h2 class="mt-3">' + _("Donate (3/3)") + '</h2>',
        '<p>' + controller.donationmsg + '</p>',
        '<div id="buttons-donation">',
        '</div>',
        '</form>',
        '</div>',

        '<div id="pane-loading" class="container text-center" style="display: none">',
        '<h1 class="mt-5">' + _("Loading...") + '</h1>',
        '<div id="spinner" class="spinner-border spinner-border-lg"></div>',
        '</div>'

    ].join("\n");

    $("body").html(h);


    $("#btn-next").click(function() {
        $(".container").hide();
        $("#pane-sign").show();
        $("#signature").signature({ guideline: true });
    });

    $("#btn-clear").click(function() {
        $("#signature").signature("clear");
    });

    $("#btn-sign").click(function() {
        if ($("#signature").signature("isEmpty")) {
            show_dlg("Error", _("Signature is required"));
            return;
        }
        $(".container").hide();
        $("#pane-donate").show();
    });

    $.each(controller.donationtiers.split("\n"), function(i, v) {
        let [amt, desc] = v.split("=");
        let col = "btn-secondary";
        if (i == 0) { col = "btn-primary"; }
        let c = amt.replace(new RegExp("&[^;]+;", "ig"), ''); // Remove HTML entities first as they contain numbers
        c = c.replace(new RegExp("[^0-9\\.]", "g"), ''); // Remove anything that isn't a digit or decimal point
        $("#buttons-donation").append('<p><button type="button" data-amount="' + c + '" ' +
            'class="btn ' + col + '"><b>' + amt + '</b><br/>' + desc + '</button></p>');
    });

    $("#buttons-donation button").on("click", function() {
        let formdata = {
            "account":      controller.database,
            "method":       "checkout_adoption",
            "token":        controller.token,
            "sig":          $("#signature canvas").get(0).toDataURL("image/png"),
            "sendsigned":   $("#sendsigned").is(":checked") ? "on" : "",
            "donationamt":  $(this).attr("data-amount")
        };

        $(".container").hide();
        $("#pane-loading").show();

        $.ajax({
            type: "POST",
            url: "service",
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(response) {
                // response is a URL to redirect to the payment processor
                window.location = response;
            },
            error: function(jqxhr, textstatus, response) {
                $(".container").hide();
                $("#pane-donate").show();
                show_dlg("Error", response);
            }
        });

    });

});

