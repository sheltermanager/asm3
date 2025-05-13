/*global $, jQuery, controller */
/*global common, config, format, html */
/*global _, mobile_ui_addanimal, mobile_ui_animal, mobile_ui_incident, mobile_ui_person, mobile_ui_stock */

"use strict";

const mobile = {

    post_handler: "mobile",

    show_info: function(title, body) {
        $("#infotitle").html(title);
        $("#infotext").html(body);
        $("#infodlg").modal("show");
    },

    show_error: function(title, body) {
        $("#errortitle").html(title);
        $("#errortext").html(body);
        $("#errordlg").modal("show");
    },

    ajax_post: function(formdata, successfunc, errorfunc) {
        $.ajax({
            type: "POST",
            url: mobile.post_handler,
            data: formdata,
            dataType: "text",
            mimeType: "textPlain",
            success: function(result) {
                if (successfunc) {
                    successfunc(result);
                }
            },
            error: function(jqxhr, textstatus, response) {
                if (errorfunc) {
                    errorfunc(textstatus, response);
                }
                mobile.show_error(textstatus, response);
            }
        });
    },

    markup_online_forms: function() {
        let fitems = "";
        $.each(controller.internalforms, function(i, v) {
            let furl = asm.serviceurl + "?";
            if (asm.useraccountalias) { furl += "account=" + asm.useraccountalias + "&"; }
            furl += "method=online_form_html&formid=" + v.ID;
            fitems += '<a id="stocktake-nav" class="dropdown-item hideifzero internal-link" data-perm="csl" data-link="onlineforms" href="' + furl + '" target="_blank">' + v.NAME + '</a>';
        });
        return fitems
    },

    render: function() {
        return [
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
            '<div class="modal fade" id="infodlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="infotitle" aria-hidden="true">',
                '<div class="modal-dialog">',
                    '<div class="modal-content">',
                        '<div class="modal-header">',
                            '<h5 class="modal-title" id="infotitle">Info</h5>',
                            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
                        '</div>',
                        '<div id="infotext" class="modal-body">',
                        '</div>',
                        '<div class="modal-footer">',
                            '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Close") + '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            '<div class="modal fade" id="administerdlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="administertitle" aria-hidden="true">',
                '<div class="modal-dialog">',
                    '<div class="modal-content">',
                        '<div class="modal-header">',
                            '<h5 class="modal-title" id="administertitle">' + _("Give") + '</h5>',
                        '</div>',
                        '<div class="modal-body">',
                            '<span id="administertext"></span>',
                            '<select id="administerresult" class="form-select">' + html.list_to_options(controller.testresults, "ID", "RESULTNAME") + '</select>',
                        '</div>',
                        '<div class="modal-footer">',
                            '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">' + _("Cancel") + '</button>',
                            '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Give") + '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            '<div class="modal fade" id="taskdlg" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="tasktitle" aria-hidden="true">',
                '<div class="modal-dialog">',
                    '<div class="modal-content">',
                        '<div class="modal-header">',
                            '<h5 class="modal-title" id="tasktitle">' + _("Complete") + '</h5>',
                        '</div>',
                        '<div id="tasktext" class="modal-body">',
                        '</div>',
                        '<div class="modal-footer">',
                            '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">' + _("Cancel") + '</button>',
                            '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Complete") + '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',

            mobile.render_nav(),

            '<div id="content-home" class="container" style="display: none">',
                '<div class="row">',
                    // Messages
                    '<div id="hp-messages" class="col-sm">',
                        '<div class="card shadow-sm mt-3">',
                            '<div class="card-header">' + _("Messages"), 
                            '<span class="badge bg-primary rounded-pill">' + controller.messages.length + '</span>',
                                '<div class="mt-2 mb-1">',
                                    '<select class="form-select" id="messagefor" name="messagefor">',
                                    '<option value="*">' + _("(everyone)") + '</option>',
                                    html.list_to_options(controller.usersandroles, "USERNAME", "USERNAME"),
                                    '</select>',
                                '</div>',
                                '<div class="mb-1">',
                                    '<input type="text" placeholder="' + _("Message") + '" class="form-control" id="messagebody" name="messagebody">',
                                '</div>',
                                '<div class="d-grid gap-2">',
                                    '<button type="button" class="btn btn-primary" id="addmessage"><i class="bi bi-plus-square"></i> ',
                                        _("Add Message"),
                                        '<span class="spinner-border spinner-border-sm" style="display: none"></span>',
                                    '</button>',
                                '</div>',
                            '</div>',
                            '<div class="card-body">',
                                '<div class="list-group">',
                                '</div>',
                            '</div>',
                            //'<div class="card-footer">',
                            //'</div>',
                        '</div>',
                    '</div>',
                    // Timeline
                    '<div id="hp-timeline" class="col-sm">',
                        '<div class="card shadow-sm mt-3">',
                            '<div class="card-header">',
                            _("Timeline ({0})").replace("{0}", controller.timeline.length),
                            '</div>',
                            '<div class="card-body">',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
                // TODO: remove 1/11/24
                // '<p class="mt-3"><button id="oldui" class="btn btn-outline-danger" type="button">Switch to old Mobile UI</button></p>',
            '</div>',

            '<div id="content-reports" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Reports") + '</h2>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-addanimal" class="container" style="display: none">',
            mobile_ui_addanimal.render(),
            '</div>',

            '<div id="content-shelteranimals" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Shelter Animals") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',
            '<div id="content-animal" class="container" style="display: none">',
            '</div>',

            '<div id="content-medicate" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Medicate Animal") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-vaccinate" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Vaccinate Animal") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-test" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Test Animal") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-myincidents" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("My Incidents") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',
            '<div id="content-myincidents-view" class="incident-view container" style="display: none">',
            '</div>',

            '<div id="content-unincidents" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("My Undispatched Incidents") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',
            '<div id="content-unincidents-view" class="incident-view container" style="display: none">',
            '</div>',

            '<div id="content-opincidents" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Open Incidents") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',
            '<div id="content-opincidents-view" class="incident-view container" style="display: none">',
            '</div>',

            '<div id="content-flincidents" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Incidents Requiring Followup") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',
            '<div id="content-flincidents-view" class="incident-view container" style="display: none">',
            '</div>',

            '<div id="content-checklicence" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Check License") + '</h2>',
                '<div class="mb-3">',
                    '<label for="licencenumber" class="form-label">' + _("License Number") + '</label>',
                    '<input type="text" class="form-control" id="licencenumber">',
                '</div>',
                '<button id="btn-check-licence" type="button" class="btn btn-primary">' + _("Check"),
                '<div class="spinner-border spinner-border-sm" style="display: none"></div>',
                '</button>',
                '</div>',
            '</div>',

            '<div id="content-licenceresults" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Check License") + '</h2>',
            '<div class="mb-3">',
            '<a href="#" data-link="checklicence" class="list-group-item list-group-item-action internal-link">',
            '&#8592; ' + _("Back") + '</a>',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-completediary" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Complete Tasks") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-findperson" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Find Person") + '</h2>',
                '<div class="mb-3">',
                    '<label for="personq" class="form-label">' + _("Search") + '</label>',
                    '<input type="text" class="form-control" id="personq">',
                '</div>',
                '<button id="btn-find-person" type="button" class="btn btn-primary">' + _("Search"),
                '<div class="spinner-border spinner-border-sm" style="display: none"></div>',
                '</button>',
                '</div>',
            '</div>',

            '<div id="content-personresults" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Find Person") + '</h2>',
            '<div class="mb-3 list-group">',
            '<a href="#" data-link="findperson" class="list-group-item list-group-item-action internal-link">',
            '&#8592; ' + _("Back") + '</a>',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group results">',
            '</div>',
            '</div>',
            '<div id="content-person" class="container" style="display: none">',
            '</div>',

            '<div id="content-performhomecheck" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Perform Homecheck") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-stocklocations" class="container" style="display: none">',
            '<h2 class="mt-3">' + _("Stock Locations") + '</h2>',
            '<div class="mb-3">',
            '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
            '</div>',
            '<div class="list-group">',
            '</div>',
            '</div>',

            '<div id="content-stocktake" class="container" style="display: none">',
            '<div class="mt-3 mb-3 list-group">',
            '<a href="#" data-link="stocklocations" class="list-group-item list-group-item-action internal-link">&#8592; ' + _("Back") + '</a>',
            '</div>',
            '<div class="list-group locations">',
            '</div>',
            '<div class="d-grid gap-2 d-md-block mt-3">',
            '<button id="btn-submit-stocktake" type="button" class="btn btn-primary">' + _("Update"),
            '<div class="spinner-border spinner-border-sm" style="display: none"></div> ',
            '</button>',
            '</div>',
            '</div>'
        ].join("\n");
    },

    render_nav: function() {
        return [
            '<nav class="navbar navbar-expand-lg navbar-light bg-light">',
                '<div class="container-fluid">',
                    '<a class="navbar-brand" href="#">' + controller.user + ': ' + _("ASM") + '</a>',
                    '<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar-content" aria-controls="navbar-content" aria-expanded="false" aria-label="Toggle navigation">',
                        '<span class="navbar-toggler-icon"></span>',
                    '</button>',
                    '<div class="collapse navbar-collapse" id="navbar-content">',
                    '<ul class="navbar-nav me-auto mb-2 mb-lg-0">',
                    '<li class="nav-item">',
                        '<a class="nav-link internal-link" data-perm="vcr" data-link="reports" href="#">' + _("Generate Report"),
                        '</a>',
                    '</li>',
                    '<li class="nav-item">',
                        '<a class="nav-link" href="mobile_sign">' + _("Signing Pad"),
                        '</a>',
                    '</li>',
                    '<li class="nav-item dropdown">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-animals" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Animals") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-animals">',
                            '<a class="dropdown-item internal-link" data-perm="aa" data-link="addanimal" href="#">',
                                '<span class="asm-icon asm-icon-animal-add"></span>',
                                _("Add Animal"),
                            '</a>',
                            '<a class="dropdown-item" data-perm="aam" href="mobile_photo_upload">',
                                '<span class="asm-icon asm-icon-image"></span>',
                                _("Photo Uploader"),
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="va" data-link="shelteranimals" href="#">',
                                '<span class="asm-icon asm-icon-animal"></span>',
                                _("Shelter Animals"),
                                '<span class="badge bg-primary rounded-pill">' + controller.animals.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="cav" data-link="vaccinate" href="#">',
                                '<span class="asm-icon asm-icon-vaccination"></span>',
                                _("Vaccinate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.vaccinations.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="cat" data-link="test" href="#">',
                                '<span class="asm-icon asm-icon-test"></span>',
                                _("Test Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.tests.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="mcam" data-link="medicate" href="#">',
                                '<span class="asm-icon asm-icon-medical"></span>',
                                _("Medicate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.medicals.length + '</span>',
                            '</a>',
                        '</div>',
                    '</li>',
                    '<li class="nav-item dropdown animalcontrol">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-incidents" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Animal Control") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-incidents">',
                            // '<a class="dropdown-item" href="#">' + _("Add Call") + '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="vaci" data-link="myincidents" href="#">',
                                '<span class="asm-icon asm-icon-call"></span>',
                                _("My Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsmy.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="vaci" data-link="unincidents" href="#">',
                                '<span class="asm-icon asm-icon-call"></span>',
                                _("My Undispatched Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsundispatched.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="vaci" data-link="opincidents" href="#">',
                                '<span class="asm-icon asm-icon-call"></span>',
                                _("Open Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsincomplete.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="vaci" data-link="flincidents" href="#">',
                                '<span class="asm-icon asm-icon-call"></span>',
                                _("Incidents Requiring Followup"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsfollowup.length + '</span>',
                            '</a>',
                            '<a class="dropdown-item internal-link" data-perm="vapl" data-link="checklicence" href="#">',
                                '<span class="asm-icon asm-icon-licence"></span>',
                                _("Check License"),
                            '</a>',
                        '</div>',
                    '</li>',
                    '<li class="nav-item dropdown">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-diary" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Diary") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-diary">',
                            // '<a class="dropdown-item" href="#">' + _("New Task") + '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="vdn" data-link="completediary" href="#">',
                                '<span class="asm-icon asm-icon-diary"></span>',
                                _("Complete Tasks"),
                                '<span class="badge bg-primary rounded-pill">' + controller.diaries.length + '</span>',
                            '</a>',
                        '</div>',
                    '</li>',
                    '<li class="nav-item dropdown">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-financial" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Financial") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-financial">',
                            '<a id="stocktake-nav" class="dropdown-item hideifzero internal-link" data-perm="csl" data-link="stocklocations" href="#">',
                                '<span class="asm-icon asm-icon-stock"></span>',
                                _("Stock Take"),
                                '<span class="badge bg-primary rounded-pill">' + controller.stocklocations.length + '</span>',
                            '</a>',
                        '</div>',
                    '</li>',
                    '<li class="nav-item dropdown">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-onlineforms" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Online Forms") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-onlineforms">',
                            mobile.markup_online_forms(),
                        '</div>',
                    '</li>',
                    '<li class="nav-item dropdown">',
                        '<a class="nav-link dropdown-toggle" href="#" id="dropdown-person" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                        _("Person") + '</a>',
                        '<div class="dropdown-menu shadow-sm" aria-labelledby="dropdown-person">',
                            '<a class="dropdown-item internal-link" data-perm="vo" data-link="findperson" href="#">', 
                                '<span class="asm-icon asm-icon-person-find"></span>',
                                _("Find Person"),
                            '</a>',
                            '<a class="dropdown-item hideifzero internal-link" data-perm="co" data-link="performhomecheck" href="#">',
                                '<span class="asm-icon asm-icon-person"></span>',
                                _("Perform Homecheck"),
                                '<span class="badge bg-primary rounded-pill">' + controller.rsvhomecheck.length + '</span>',
                            '</a>',
                        '</div>',
                    '</li>',
                    '<li class="nav-item">',
                        '<a class="nav-link" href="main">' + _("Desktop/Tablet UI") + '</a>',
                    '</li>',
                    '<li class="nav-item">',
                        '<a class="nav-link" href="mobile_logout">' + _("Logout") + '</a>',
                    '</li>',
                    '</ul>',
                '</div>',
            '</nav>'
        ].join("\n");
    },

    // Returns the HTML for an add log slider
    render_addlog: function(linkid, linktypeid) {
        return [
            '<div class="mb-3">',
                '<label for="logtype" class="form-label">' + _("Log Type") + '</label>',
                '<select class="form-select" id="logtype" name="logtypeid">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="comments" class="form-label">' + _("Log Text") + '</label>',
                '<input type="text" class="form-control" id="comments" name="comments">',
            '</div>',
            '<div class="d-flex justify-content-center pb-2">',
            '<button data-linkid="' + linkid + '" data-linktypeid="' + linktypeid + '" type="button" class="btn btn-primary addlog">',
            '<i class="bi bi-plus-square"></i>',
                _("Create"),
            '<div class="spinner-border spinner-border-sm" style="display: none"></div></button>',
            '</div>'
        ].join("\n");
    },

    // Renders the messages given into the list
    render_messages: function(messages) {
        $("#hp-messages .list-group").empty();
        $.each(messages, function(i, v) {
            let forname = v.FORNAME;
            if (forname == "*") { forname = _("(everyone)"); }
            let h = '<div class="list-group-item">' +
                '<h5>' + format.date(v.ADDED) + ' ' + v.CREATEDBY + ' &#8594; ' + forname + '</h5>' + 
                '<small>' + v.MESSAGE + '</small>';
            $("#hp-messages .list-group").append(h);
        });
    },

    bind: function() {

        // Delegate handler for internal links
        $("body").on("click", ".internal-link", function() {
            let target = $(this).attr("data-link");
            if (target) {
                $(".container").hide();
                $("#content-" + target).show();
            }
        });

        // Go home when user name clicked
        $(".navbar-brand").click(function() {
            $(".container").hide();
            $("#content-home").show();
        });

        // Delegate handler for filtering list groups with search inputs
        $("body").on("keyup", ".search", function() {
            let v = $(this).val().toLowerCase(),
                lg = $(this).closest(".container").find(".list-group");
            lg.find("a").filter(function() {
            $(this).toggle($(this).find("h5").text().toLowerCase().indexOf(v) > -1 || $(this).find("small").text().toLowerCase().indexOf(v) > -1);
            });
        });

        // Make the mobile submenu collapse when an internal link is clicked
        $(".navbar-collapse").on("click", ".internal-link", function() {
            $(".navbar-collapse").collapse("hide");
        });

        // Handle clicking on the addlog sliders
        $("body").on("click", ".btn.addlog", function() {
            let formdata = {
                "mode": "addlog",
                "linkid": $(this).attr("data-linkid"),
                "linktypeid": $(this).attr("data-linktypeid"),
                "type": $(this).parent().prev().prev().find("select").val(),
                "comments": $(this).parent().prev().find(".form-control").val()
            },
            comments = $(this).parent().prev().find(".form-control");
            let spinner = $(this).find(".spinner-border");
            spinner.show();
            mobile.ajax_post(formdata, function() {
                mobile.show_info(_("Log message added"), comments.val());
                comments.val("");
                spinner.hide();
            });
        });

        // Handle clicking a task to complete and showing a popup dialog to confirm
        $("#content-completediary").on("click", "a", function() {
            let diaryid = $(this).attr("data-id");
            $.each(controller.diaries, function(i, v) {
                if (v.ID == diaryid) {
                    $("#administerdlg .btn-primary").unbind("click");
                    $("#administerdlg .btn-primary").html(_("Complete"));
                    $("#administerdlg .btn-primary").click(function() {
                        mobile.ajax_post("mode=diarycomplete&id=" + diaryid, function() {
                            $("#content-completediary [data-id='" + diaryid + "']").remove(); // remove the item from the list on success
                        });
                    });
                    $("#administertitle").html(_("Complete"));
                    $("#administerresult").hide();
                    $("#administertext").html(format.date(v.DIARYDATETIME) + ": " + v.SUBJECT + ': ' + v.NOTE);
                    $("#administerdlg").modal("show");
                }
            });
        });

        $("#addmessage").click(function() {
            if (!$("#messagebody").val()) {
                mobile.show_error(_("Error"), _("Message body must be supplied"));
                return;
            }
            let formdata = {
                "mode": "addmessage",
                "for": $("#messagefor").val(),
                "body": $("#messagebody").val()
            };
            $("#addmessage .spinner-border").show();
            mobile.ajax_post(formdata, function(response) {
                mobile.render_messages(jQuery.parseJSON(response));
                $("#messagebody").val("");
                $("#addmessage .spinner-border").hide();
            });
        });

        // Hide the timeline if disabled or no permission
        if (!config.bool("ShowTimelineHomePage") || !common.has_permission("vti")) {
            $("#hp-timeline").hide();
        }

        mobile_ui_addanimal.bind();
        mobile_ui_animal.bind();
        mobile_ui_person.bind();
        mobile_ui_stock.bind();

    },

    sync: function() {

        // Hide all nav elements with hideifzero if they have a badge containing zero
        $(".hideifzero").each(function() {
            $(this).toggle( $(this).find("span.badge").text() != "0" );
        });

        // Hide all nav elements with permissions if the user does not have that permission
        $("nav a").each(function() {
            let t = $(this), perm = t.attr("data-perm");
            if (perm && !common.has_permission(perm)) {
                t.hide();
            }
        });

        mobile_ui_incident.render_incident_list("#content-myincidents", "myincidents", controller.incidentsmy);
        mobile_ui_incident.render_incident_list("#content-opincidents", "opincidents", controller.incidentsincomplete);
        mobile_ui_incident.render_incident_list("#content-unincidents", "unincidents", controller.incidentsundispatched);
        mobile_ui_incident.render_incident_list("#content-flincidents", "flincidents", controller.incidentsfollowup);

        mobile.render_messages(controller.messages);

        mobile_ui_animal.render_shelteranimalslist();

        // Hide animal control menu if the functionality is disabled
        $(".animalcontrol").toggle( !config.bool("DisableAnimalControl") );

        // Hide stock take menu item if stock control is disabled 
        if (config.bool("DisableStockControl")) {
            $("#stocktake-nav").hide();
        }

        // Hide all dropdown menus that don't have any visible items
        $("nav .dropdown-menu").each(function() {
            let t = $(this), visibleitems = 0;
            $.each(t.find(".dropdown-item"), function() {
                if ($(this).css("display") != "none") { visibleitems++; }
            });
            if (visibleitems == 0) {
                t.closest(".dropdown").hide();
            }
        });

        // Load list of diary notes to complete
        $("#content-completediary .list-group").empty();
        $.each(controller.diaries, function(i, v) {
            let linkinfo = "";
            if (v.LINKINFO) { linkinfo = " (" + v.LINKINFO + ")"; }
            let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                '<h5 class="mb-1">' + v.SUBJECT + linkinfo + '</h5>' + 
                '<small>' + format.date(v.DIARYDATETIME) + ' ' + format.time(v.DIARYDATETIME) + ': ' + v.DIARYFORNAME + '<br>' +
                v.NOTE + '</small>' +
                '</a>';
            $("#content-completediary .list-group").append(h);
        });

        // Load Timeline
        let tl = [];
        $.each(controller.timeline, function(i, v) {
            // Skip this entry if it's for a deceased animal and we aren't showing them
            if (!config.bool("ShowDeceasedHomePage") && (v.CATEGORY == "DIED" || v.CATEGORY == "EUTHANISED")) { return; }
            tl.push(html.event_text(v, { includedate: true, includeicon: true }) + '<br/>');
        });
        $("#hp-timeline .card-body").html(tl.join("\n"));

        // Load reports
        $("#content-reports .list-group").empty();
        let cgroup = "", id = "";
        let reps = [ '<div class="accordion" id="accordion-reports">' ];
        $.each(controller.reports, function(i, v) {
            if (cgroup != v.CATEGORY) {
                if (cgroup != "") { reps.push("</div></div></div></div>"); } // list-group, accordion-body, collapse, accordion-item
                cgroup = v.CATEGORY;
                id = common.replace_all(cgroup, " ", "");
                reps.push('<div class="accordion-item">');
                reps.push('<h2 class="accordion-header" id="heading-' + id + '">');
                reps.push('<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-' + id + 
                        '" aria-expanded="false" aria-controls="collapse-' + id + '">' + v.CATEGORY + '</button></h2>');
                reps.push('<div id="collapse-' + id + '" class="accordion-collapse collapse" aria-labelledby="heading-' + id + '" data-bs-parent="#accordion-reports">');
                reps.push('<div class="accordion-body">');
                reps.push('<div class="list-group">');
                //$("#content-reports .list-group").append('<div class="list-group-item bg-secondary text-white fw-bold">' + v.CATEGORY + '</div>');
            }
            reps.push('<a class="list-group-item list-group-item-action" href="mobile_report?id=' + v.ID + '">' + v.TITLE + '</a>');
        });
        reps.push("</div></div></div></div>"); // close final list-group, accordion-body, collapse, accordion-item
        $("#content-reports .list-group").html(reps.join("\n"));

        mobile_ui_addanimal.sync();
        mobile_ui_animal.sync();
        mobile_ui_person.sync();
        mobile_ui_stock.sync();
    
        // Show the dashboard/homepage
        $("#content-home").show();

        document.title = controller.user + ": " + _("ASM");
    }
};

$(document).ready(function() {
    $("body").html(mobile.render());
    mobile.bind();
    mobile.sync();
});
