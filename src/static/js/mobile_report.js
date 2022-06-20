/*global $, controller */

$(document).ready(function() {

    "use strict";

    const show_dlg = function(title, body) {
        $("#errortitle").html(title);
        $("#errortext").html(body);
        $("#errordlg").modal("show");
    };

    let h = [
        '<div class="modal fade" id="errordlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="errortitle" aria-hidden="true">',
            '<div class="modal-dialog">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="errortitle">Error</h5>',
                        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                    '</div>',
                    '<div id="errortext" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',

        '<div id="content" class="container">',
        '<h2>' + controller.title + '</h2>',
        '<form action="mobile_report" method="get">',
        '<input name="id" type="hidden" value="' + controller.crid + '" >',
        '<input name="mode" type="hidden" value="exec" >'

    ];

    $.each(controller.criteria, function(i, v) {
        let [name, rtype, question] = v;
        if (rtype == "DATE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + question + '</label>' +
                '<input type="date" class="form-control" id="report-' + name + '" name="' + name + '">' + 
            '</div>');
        }
        else if (rtype == "STRING") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + question + '</label>' +
                '<input type="text" class="form-control" id="report-' + name + '" name="' + name + '">' +
            '</div>');
        }
        else if (rtype == "LOOKUP") {
            let values = question.substring(question.indexOf("|")+1);
            if (question.indexOf("|") != -1) { question = question(0, question.indexOf("|")); } 
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + question + '</label>' +
                '<select class="form-control" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(values) + '</select></div>');
        }
        else if (rtype == "NUMBER") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + question + '</label>' +
                '<input type="number" class="form-control" id="report-' + name + '" name="' + name + '">' + 
            '</div>');
        }
        else if (rtype == "ANIMAL" || rtype == "FSANIMAL" || rtype == "ALLANIMAL" || rtype == "ANIMALS") {
            let multiple = "";
            if (rtype == "ANIMALS") { multiple = 'multiple="multiple"'; }
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Animal") + '</label>' +
                '<select class="form-control" id="report-' + name + '" name="' + name + '" ' + multiple + '>' +
                html.list_to_options(controller.animals, "ID", "ANIMALNAME++SHELTERCODE") + '</select></div>');
        }
        else if (rtype == "ANIMALFLAG") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Flag") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                '</select></div>');
        }
        else if (rtype == "PERSONFLAG") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Flag") + '</label>' +
                '<select class="form-control personflags" id="report-' + name + '" name="' + name + '">' +
                '</select></div>');
        }
        else if (rtype == "PERSON") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Person") + '</label>' +
                '<select class="form-control" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.people, "ID", "OWNERNAME++OWNERADDRESS") + '</select></div>');
        }
        else if (rtype == "DONATIONTYPE" || rtype == "PAYMENTTYPE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Payment Type") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME") + 
                '</select></div>');
        }
        else if (rtype == "LITTER") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Litter") + '</label>' +
                '<select class="form-control" id="report-' + name + '" name="' + name + '" ' + multiple + '>' +
                html.list_to_options(controller.litters, "value", "label") + '</select></div>');
        }
        else if (rtype == "LOCATION") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Location") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.locations, "ID", "LOCATIONNAME") + 
                '</select></div>');
        }
        else if (rtype == "LOGTYPE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Log Type") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + 
                '</select></div>');
        }
        else if (rtype == "PAYMENTMETHOD" || rtype == "PAYMENTTYPE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Payment Method") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.donationtypes, "ID", "PAYMENTNAME") + 
                '</select></div>');
        }
        else if (rtype == "SITE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Site") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.sites, "ID", "SITENAME") + 
                '</select></div>');
        }
        else if (rtype == "SPECIES") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Species") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.species, "ID", "SPECIESNAME") + 
                '</select></div>');
        }
        else if (rtype == "TYPE") {
            h.push('<div class="mb-3">' + 
                '<label for="report-' + name + '" class="form-label">' + _("Type") + '</label>' +
                '<select class="form-control animalflags" id="report-' + name + '" name="' + name + '">' +
                html.list_to_options(controller.types, "ID", "ANIMALTYPE") + 
                '</select></div>');
        }
    });

    h.push('<button id="btn-submit" type="submit" class="btn btn-primary">' + _("Generate") + 
        ' <div id="spinner" class="spinner-border spinner-border-sm" style="display: none"></div></button>');
    h.push('<button id="btn-back" type="button" class="btn btn-secondary">&#8592; ' + _("Back") + '</button>');
    h.push('</form></div>');

    $("body").html(h.join("\n"));

    // Special handling for flags
    html.animal_flag_options(null, controller.animalflags, $(".animalflags"));
    html.person_flag_options(null, controller.personflags, $(".personflags"));

    // Set date inputs to today in the local timezone
    let today = new Date();
    today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    $("input[type='date']").val( today.toJSON().slice(0,10) );

    $("#btn-back").click(function() { history.back(); });
    $("#btn-submit").click(function() { $("#spinner").show(); });

    document.title = controller.title;

});


