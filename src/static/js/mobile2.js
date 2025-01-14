/*global $, controller */

$(document).ready(function() {

    "use strict";

    const mobile = {

        post_handler: "mobile2",

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

        /* Outputs the displaylocation for an animal. If the user does not have permission to view
            person records and the animal has left on an active movement to a person, only show the
            active movement and remove the person name */
        display_location: function(a) {
            let displaylocation = a.DISPLAYLOCATION;
            if (a.ACTIVEMOVEMENTTYPE > 0 && !common.has_permission("vo") && displaylocation.indexOf("::") != -1) { 
                displaylocation = a.DISPLAYLOCATIONNAME;
            }
            return displaylocation;
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
                '<h2 class="mt-3">' + _("Add Animal") + '</h2>',
                '<input type="hidden" name="mode" value="addanimal">',
                '<div class="mb-3">',
                    '<label for="animalname" class="form-label">' + _("Name") + '</label>',
                    '<input type="text" class="form-control" id="animalname" data="animalname">',
                '</div>',
                '<div class="mb-3">',
                    '<label for="sheltercode" class="form-label">' + _("Code") + '</label>',
                    '<input type="text" class="form-control" id="sheltercode" data="sheltercode">',
                '</div>',
                '<div class="mb-3">',
                    '<label for="estimatedage" class="form-label">' + _("Age") + '</label>',
                    '<input type="text" class="form-control" id="estimatedage" data="estimatedage" value="1.0">',
                '</div>',
                '<div class="mb-3">',
                    '<label for="sex" class="form-label">' + _("Sex") + '</label>',
                    '<select class="form-select" name="sex" id="sex">',
                    html.list_to_options(controller.sexes, "ID", "SEX"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="animaltype" class="form-label">' + _("Type") + '</label>',
                    '<select class="form-select" data="animaltype" id="animaltype">',
                    html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="species" class="form-label">' + _("Species") + '</label>',
                    '<select class="form-select" data="species" id="species">',
                    html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="breed1" class="form-label">' + _("Breed") + '</label>',
                    '<select class="form-select" data="breed1" id="breed1">',
                    html.list_to_options_breeds(controller.breeds),
                    '</select>',
                    '<select id="breedp" data="breedp" style="display:none;">',
                    html.list_to_options_breeds(controller.breeds),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="basecolour" class="form-label">' + _("Color") + '</label>',
                    '<select class="form-select" data="basecolour" id="basecolour">',
                    html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="size" class="form-label">' + _("Size") + '</label>',
                    '<select class="form-select" data="size" id="size">',
                    html.list_to_options(controller.sizes, "ID", "SIZE"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="internallocation" class="form-label">' + _("Location") + '</label>',
                    '<select class="form-select" data="internallocation" id="internallocation">',
                    html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                    '</select>',
                '</div>',
                '<div class="mb-3">',
                    '<label for="unit" class="form-label">' + _("Unit") + '</label>',
                    '<select class="form-select" id="unit" data="unit">',
                    '</select>',
                '</div>',
                '<div class="d-flex justify-content-center pb-2">',
                '<button id="addanimal-submit" type="submit" class="btn btn-primary">',
                    '<i class="bi bi-plus-square"></i>',
                    _("Create"), 
                    '<span class="spinner-border spinner-border-sm" style="display: none"></span>',
                '</button>',
                '</div>',
                '</form>',
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

        // Returns the HTML for rendering an animal record
        render_animal: async function(a, selector) {
            const i = function(label, value, cfg) {
                if (!value) { value = ""; }
                if (cfg && config.bool(cfg)) { return; } // Hide if this config element is true, eg: DontShowLocationUnit
                return '<div class="row align-items-start"><div class="col">' + label + '</div><div class="col">' + value + '</div></div>';
            };
            const col3 = function(c1, c2, c3) {
                if (!c1 && !c2 && !c3) { return ""; }
                return '<div class="row align-items-start"><div class="col">' + c1 + '</div><div class="col">' + c2 + '</div><div class="col">' + c3 + '</div></div>';
            };
            const hd = function(value) {
                return '<div class="row align-items-start mt-3"><div class="col fw-bold">' + value + '</div></div>';
            };
            const n = function(s) {
                if (!s) { return ""; }
                return s;
            };
            const fgs = function(s) {
                let o = [];
                if (!s) { return ""; }
                $.each(s.split("|"), function(i, v) {
                    if (v.trim()) { o.push(v.trim()); }
                });
                return o.join(", ");
            };
            const aci = function(id, headerhtml, bodyhtml, show) {
                if (!show) { show=""; }
                return '<div class="accordion-item">' +
                    '<h2 class="accordion-header" id="heading-' + id + '">' +
                    '<button class="accordion-button ' + ( show ? "" : "collapsed") + '" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-' + id + 
                        '" aria-expanded="false" aria-controls="collapse-' + id + '">' + headerhtml + '</button></h2>' + 
                    '<div id="collapse-' + id + '" class="accordion-collapse collapse ' + show + '" aria-labelledby="heading-' + id + '" data-bs-parent="#accordion-animal">' + 
                    '<div class="accordion-body">' + bodyhtml + '</div>' +
                    '</div></div>';
            };
            // Grab the extra data for this animal from the backend
            let o = await common.ajax_post(mobile.post_handler, "mode=loadanimal&id=" + a.ID);
            o = jQuery.parseJSON(o);
            a = o.animal;
            let [adoptable, adoptreason] = html.is_animal_adoptable(a);
            let x = [];
            let h = [
                '<div class="list-group mt-3">',
                '<a href="#" data-link="shelteranimals" class="list-group-item list-group-item-action internal-link">',
                '&#8592; ' + _("Back"),
                '</a>',
                '<div class="list-group-item">',
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(a, "animalthumb") + '">',
                '<h5 class="mb-1">' + a.ANIMALNAME + ' - ' + a.CODE + '</h5>',
                '<small>' + common.substitute(_("{0} {1} {2} aged {3}"), { "0": a.SEXNAME, "1": a.BREEDNAME, "2": a.SPECIESNAME, "3": a.ANIMALAGE }) + '<br/>',
                a.IDENTICHIPNUMBER + '</small>',
                '<br/><small class="fst-italic">' + fgs(a.ADDITIONALFLAGS) + '</small>',
                //'<br/>',
                //'<button type="button" class="uploadphoto btn btn-primary"><i class="bi-cloud-upload-fill"></i> ' + _("Upload"),
                //'</button>',
                //'<input type="file" accept="image/*" class="uploadphotofile" style="display: none" />',
                '</div>',
                '</div>',

                '<div class="accordion" id="accordion-animal">',

                aci("details", _("Animal"), [
                    i(_("Status"), adoptable ? '<span class="text-success">' + _("Available for adoption") + '</span>' : 
                        '<span class="text-danger">' + _("Not available for adoption") + " (" + adoptreason + ")</span>"),
                    i(_("Type"), a.ANIMALTYPENAME),
                    i(_("Location"), mobile.display_location(a)),
                    i(_("Color"), a.BASECOLOURNAME),
                    i(_("Coat Type"), a.COATTYPENAME, "DontShowCoatType"),
                    i(_("Size"), a.SIZENAME, "DontShowSize"),
                    i(_("DOB"), format.date(a.DATEOFBIRTH) + " (" + a.ANIMALAGE + ")"),
                    
                    i(_("Markings"), a.MARKINGS),
                    i(_("Hidden Comments"), a.HIDDENANIMALDETAILS),
                    i(_("Description"), a.ANIMALCOMMENTS),
                    
                    i(_("Cats"), a.ISGOODWITHCATSNAME, "DontShowGoodWith"),
                    i(_("Dogs"), a.ISGOODWITHDOGSNAME, "DontShowGoodWith"),
                    i(_("Children"), a.ISGOODWITHCHILDRENNAME, "DontShowGoodWith"),
                    i(_("Housetrained"), a.ISHOUSETRAINEDNAME, "DontShowGoodWith")
                ].join("\n"), "show"),
            
                aci("entry", _("Entry"), [
                    i(_("Date Brought In"), format.date(a.DATEBROUGHTIN)),
                    i(_("Entry Type"), a.ENTRYTYPENAME, "DontShowEntryType"),
                    i(_("Entry Category"), a.ENTRYREASONNAME),
                    i(_("Entry Reason"), a.REASONFORENTRY),
                    common.has_permission("vo") ? i(_("Original Owner"), a.ORIGINALOWNERNAME) : "",
                    common.has_permission("vo") ? i(_("Brought In By"), a.BROUGHTINBYOWNERNAME) : "",
                    i(_("Bonded With"), n(a.BONDEDANIMAL1CODE) + " " + n(a.BONDEDANIMAL1NAME) + " " + n(a.BONDEDANIMAL2CODE) + " " + n(a.BONDEDANIMAL2NAME), "DontShowBonded")
                ].join("\n")),

                aci("health", _("Health and Identification"), [
                    i(_("Microchipped"), format.date(a.IDENTICHIPDATE) + " " + a.IDENTICHIPPED==1 ? a.IDENTICHIPNUMBER : "", "DontShowMicrochip"),
                    i(_("Tattoo"), format.date(a.TATTOODATE) + " " + a.TATTOO==1 ? a.TATTOONUMBER : "", "DontShowTattoo"),
                    i(_("Neutered"), a.NEUTEREDNAME + " " + format.date(a.NEUTEREDDATE), "DontShowNeutered"),
                    i(_("Declawed"), a.DECLAWEDNAME, "DontShowDeclawed"),
                    i(_("Heartworm Tested"), format.date(a.HEARTWORMTESTDATE) + " " + a.HEARTWORMTESTED==1 ? a.HEARTWORMTESTRESULTNAME : "", "DontShowHeartworm"),
                    i(_("FIV/L Tested"), format.date(a.COMBITESTDATE) + " " + a.COMBITESTED==1 ? a.COMBITESTRESULTNAME + " " + a.FLVRESULTNAME : "", "DontShowCombi"),
                    i(_("Health Problems"), a.HEALTHPROBLEMS),
                    i(_("Rabies Tag"), a.RABIESTAG),
                    i(_("Special Needs"), a.HASSPECIALNEEDSNAME),
                    i(_("Current Vet"), n(a.CURRENTVETNAME) + " " + n(a.CURRENTVETWORKTELEPHONE))
                ].join("\n"))
            ];
            if (o.additional.length > 0) {
                x = [];
                $.each(o.additional, function(d, v) {
                    x.push(i(v.NAME, v.VALUE)); 
                });
                h.push(aci("additional", _("Additional"), x.join("\n")));
            }
            if (common.has_permission("dvad") && o.diets.length > 0) {
                x = [];
                $.each(o.diets, function(d, v) {
                    x.push(col3(format.date(v.DATESTARTED), v.DIETNAME, v.COMMENTS));
                });
                h.push(aci("diet", _("Diet"), x.join("\n")));
            }
            if (common.has_permission("vav") && o.vaccinations.length > 0) {
                x = [];
                $.each(o.vaccinations, function(d, v) {
                    x.push(col3(format.date(v.DATEOFVACCINATION) || _("Due {0}").replace("{0}", format.date(v.DATEREQUIRED)), v.VACCINATIONTYPE, v.COMMENTS));
                });
                h.push(aci("vacc", _("Vaccination"), x.join("\n")));
            }
            if (common.has_permission("vat") && o.tests.length > 0) {
                x = [];
                $.each(o.tests, function(d, v) {
                    x.push(col3(format.date(v.DATEOFTEST) || _("Due {0}").replace("{0}", format.date(v.DATEREQUIRED)), v.TESTNAME, v.RESULTNAME || ""));
                });
                h.push(aci("test", _("Test"), x.join("\n")));
            }
            if (common.has_permission("mvam") && o.medicals.length > 0) {
                x = [];
                $.each(o.medicals, function(d, v) {
                    x.push(col3(format.date(v.STARTDATE), v.TREATMENTNAME, v.DOSAGE));
                });
                h.push(aci("medical", _("Medical"), x.join("\n")));
            }
            if (common.has_permission("vdn") && o.diary.length > 0) {
                x = [];
                $.each(o.diary, function(d, v) {
                    x.push(col3(format.date(v.DIARYDATETIME), v.SUBJECT, v.NOTE));
                });
                h.push(aci("diary", _("Diary"), x.join("\n")));
            }
            if (common.has_permission("vle") && o.logs.length > 0) {
                x = [];
                $.each(o.logs, function(d, v) {
                    x.push(col3(format.date(v.DATE), v.LOGTYPENAME, v.COMMENTS));
                });
                h.push(aci("log", _("Log"), x.join("\n")));
            }
            if (common.has_permission("ale")) {
                h.push(aci("addlog", _("Add Log"), mobile.render_addlog(a.ID, 0)));
            }
            h.push('</div>'); // close accordion
            $(selector).html( h.join("\n") );
            // Display our animal now it's rendered
            $(".container").hide();
            $("#content-animal").show();
            // Handle the uploading of a photo when one is chosen
            $("#content-animal .uploadphoto").click(function() { $("#content-animal .uploadphotofile").click(); });
            $("#content-animal .uploadphotofile").change(function() { alert($("#content-animal .uploadphotofile").val()); });
        },

        // Renders an incident record into the selector given
        render_incident: async function(ac, selector, backlink) {
            const i = function(label, value) {
                if (!value) { value = ""; }
                return '<div class="row align-items-start"><div class="col">' + label + '</div><div class="col">' + value + '</div></div>';
            };
            const col3 = function(c1, c2, c3) {
                if (!c1 && !c2 && !c3) { return ""; }
                return '<div class="row align-items-start"><div class="col">' + c1 + '</div><div class="col">' + c2 + '</div><div class="col">' + c3 + '</div></div>';
            };
            const hd = function(value) {
                return '<div class="row align-items-start mt-3"><div class="col fw-bold">' + value + '</div></div>';
            };
            const n = function(s) {
                if (!s) { return ""; }
                return s;
            };
            const dt = function(s) {
                return format.date(s) + " " + format.time(s);
            };
            const tel = function(s) {
                if (!s) { return ""; }
                if ((controller.locale == "en" || controller.locale == "en_CA") && s.indexOf("+") != 0) { s = "+1" + s; }
                if (controller.locale == "en_GB" && s.indexOf("+") != 0) { s = "+44" + s; }
                if (controller.locale == "en_IE" && s.indexOf("+") != 0) { s = "+353" + s; }
                return '<a href="tel:' + s + '">' + s + '</a>';
            };
            const aci = function(id, headerhtml, bodyhtml, show) {
                if (!show) { show=""; }
                return '<div class="accordion-item">' +
                    '<h2 class="accordion-header" id="heading-' + id + '">' +
                    '<button class="accordion-button ' + ( show ? "" : "collapsed") + '" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-' + id + 
                        '" aria-expanded="false" aria-controls="collapse-' + id + '">' + headerhtml + '</button></h2>' + 
                    '<div id="collapse-' + id + '" class="accordion-collapse collapse ' + show + '" aria-labelledby="heading-' + id + '" data-bs-parent="#accordion-incident">' + 
                    '<div class="accordion-body">' + bodyhtml + '</div>' +
                    '</div></div>';
            };
            // Grab the extra data for this incident from the backend
            let o = await common.ajax_post(mobile.post_handler, "mode=loadincident&id=" + ac.ID);
            o = jQuery.parseJSON(o);
            ac = o.animalcontrol;
            console.log(ac);
            // Inline buttons for completing, dispatching and responding, either the date or a button
            let comptp = dt(ac.COMPLETEDATE) + ' ' + ac.COMPLETEDNAME;
            if (!ac.COMPLETEDDATE && common.has_permission("caci")) {
                comptp = '<select class="form-select complete"><option value=""></option>' + html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME") + '</select>';
                comptp += '<button type="button" data-id="' + ac.ID + '" disabled="disabled" class="complete btn btn-primary"><i class="bi-calendar-check"></i> ' + _("Complete");
                comptp += ' <div class="spinner-border spinner-border-sm" style="display: none"></div></button>';
            }
            let dispdt = dt(ac.DISPATCHDATETIME);
            if (!ac.DISPATCHDATETIME && common.has_permission("cacd")) { 
                dispdt = '<button type="button" data-id="' + ac.ID + '" class="dispatch btn btn-primary"><i class="bi-calendar-plus"></i> ' + _("Dispatch");
                dispdt += ' <div class="spinner-border spinner-border-sm" style="display: none"></div></button>';
            }
            let respdt = dt(ac.RESPONDEDDATETIME);
            if (ac.DISPATCHDATETIME && !ac.RESPONDEDDATETIME && common.has_permission("cacr")) { 
                respdt = '<button type="button" data-id="' + ac.ID + '" class="respond btn btn-primary"><i class="bi-calendar-range"></i> ' + _("Respond");
                respdt += ' <div class="spinner-border spinner-border-sm" style="display: none"></div></button>';
            }
            ////
            let followupdt = dt(ac.FOLLOWUPDATETIME);
            $.each([ac.FOLLOWUPDATETIME, ac.FOLLOWUPDATETIME2, ac.FOLLOWUPDATETIME3], function(followupcount, followup) {
                console.log(followup);
                if (followup == null && common.has_permission("caci")) { 
                    console.log("Adding button!");
                    followupdt = '<button type="button" data-id="' + ac.ID + '" class="followup btn btn-primary"><i class="bi-calendar-range"></i> ' + _("Follow Up");
                    followupdt += ' <div class="spinner-border spinner-border-sm" style="display: none"></div></button>';
                    return false;
                }
            });
            ////
            let dispadd = ac.DISPATCHADDRESS;
            if (dispadd) {
                let encadd = encodeURIComponent(ac.DISPATCHADDRESS + ',' + ac.DISPATCHTOWN + ',' + ac.DISPATCHCOUNTY + ',' + ac.DISPATCHPOSTCODE);
                dispadd = '<button type="button" data-address="' + encadd + '" class="showmap btn btn-secondary"><i class="bi-map"></i></button> ' + ac.DISPATCHADDRESS;
            }
            let x= [];
            let h = [
                '<div class="list-group mt-3" style="margin-top: 5px">',
                '<a href="#" data-link="' + backlink + '" class="list-group-item list-group-item-action internal-link">',
                '&#8592; ' + _("Back"),
                '</a>',
                '<div class="list-group-item">',
                '<h5 class="mb-1">' + ac.INCIDENTNAME + ' - ' + ac.DISPATCHADDRESS + '</h5>',
                '<small>' + ac.CALLNOTES + '</small>',
                //'<button type="button" class="uploadphoto btn btn-primary">' + _("Upload"),
                //'<i class="bi-cloud-upload-fill"></i>',
                //'</button>',
                //'<input type="file" accept="image/*" class="uploadphotofile" style="display: none" />',
                '</div>',
                '</div>',

                '<div class="accordion" id="accordion-incident">',

                aci("details", _("Incident"), [

                    i(_("Number"), format.padleft(ac.ID, 6)),
                    i(_("Type"), ac.INCIDENTNAME),
                    i(_("Incident Date/Time"), dt(ac.INCIDENTDATETIME)),
                    i(_("Notes"), ac.CALLNOTES),
                    i(_("Completed"), comptp),
                    i(_("Call Date/Time"), dt(ac.CALLDATETIME)),
                    i(_("Taken By"), ac.CALLTAKER),

                    common.has_permission("vo") ? i(_("Caller"), ac.CALLERNAME) : "",
                    common.has_permission("vo") ? i(_("Phone"), tel(ac.CALLERHOMETELEPHONE) + " " + tel(ac.CALLERWORKTELEPHONE) + " " + tel(ac.CALLERMOBILETELEPHONE)) : "",
                    common.has_permission("vo") ? i(_("Victim"), ac.VICTIMNAME) : ""
                ].join("\n"), "show"),

                aci("dispatch", _("Dispatch"), [
                    i(_("Address"), dispadd),
                    i(_("City"), ac.DISPATCHTOWN),
                    i(_("State"), ac.DISPATCHCOUNTY),
                    i(_("Zipcode"), ac.DISPATCHPOSTCODE),
                    i(_("Dispatched ACO"), ac.DISPATCHEDACO),
                    i(_("Dispatch Date/Time"), dispdt),
                    i(_("Responded Date/Time"), respdt),
                    i(_("Followup Date/Time"), followupdt),
                    i(_("Followup Date/Time"), dt(ac.FOLLOWUPDATETIME)),
                    i(_("Followup Date/Time"), dt(ac.FOLLOWUPDATETIME2)),
                    i(_("Followup Date/Time"), dt(ac.FOLLOWUPDATETIME3))
                ].join("\n"))
            ];

            x = [
                common.has_permission("vo") ? i(_("Suspect 1"), ac.OWNERNAME1) : "",
                common.has_permission("vo") ? i(_("Suspect 2"), ac.OWNERNAME2) : "",
                common.has_permission("vo") ? i(_("Suspect 3"), ac.OWNERNAME3) : ""
            ];
            // List linked animals
            $.each(o.animals, function(ai, v) {
                x.push(i(_("Animal"), v.SHELTERCODE + " - " + v.ANIMALNAME));
            });
            x = x.concat([
                i(_("Species"), ac.SPECIESNAME),
                i(_("Sex"), ac.SEXNAME),
                i(_("Age Group"), ac.AGEGROUP),
                i(_("Description"), ac.ANIMALDESCRIPTION)
            ]);
            h.push(aci("suspect", _("Suspect/Animal"), x.join("\n")));
            if (common.has_permission("vacc") && o.citations.length > 0) {
                x = [];
                $.each(o.citations, function(d, v) {
                    x.push(col3(format.date(v.CITATIONDATE), v.CITATIONNAME, v.COMMENTS));
                });
                h.push(aci("citations", _("Citations"), x.join("\n")));
            }
            if (common.has_permission("vdn") && o.diary.length > 0) {
                x = [];
                $.each(o.diary, function(d, v) {
                    x.push(col3(format.date(v.DIARYDATETIME), v.SUBJECT, v.NOTE));
                });
                h.push(aci("diary", _("Diary"), x.join("\n")));
            }
            if (common.has_permission("vle") && o.logs.length > 0) {
                x = [];
                $.each(o.logs, function(d, v) {
                    x.push(col3(format.date(v.DATE), v.LOGTYPENAME, v.COMMENTS));
                });
                h.push(aci("log", _("Log"), x.join("\n")));
            }
            if (common.has_permission("ale")) {
                h.push(aci("addlog", _("Add Log"), mobile.render_addlog(ac.ID, 6)));
            }
            h.push("</div>"); // close accordion
            $(selector).html( h.join("\n") );
            // Display the record
            $(".container").hide();
            $(selector).show();
            $(".btn.dispatch").click(function() {
                $(".btn.dispatch .spinner-border").show();
                mobile.ajax_post("mode=incdispatch&id=" + $(this).attr("data-id"), function() {
                    $(".btn.dispatch").hide();
                    $(".btn.dispatch").parent().append( format.datetime_now() );
                });
            });
            $(".btn.respond").click(function() {
                $(".btn.respond .spinner-border").show();
                mobile.ajax_post("mode=increspond&id=" + $(this).attr("data-id"), function() {
                    $(".btn.respond").hide();
                    $(".btn.respond").parent().append( format.datetime_now() );
                });
            });
            $(".btn.followup").click(function() {
                $(".btn.followup .spinner-border").show();
                mobile.ajax_post("mode=incfollowup&id=" + $(this).attr("data-id"), function() {
                    $(".btn.followup").hide();
                    $(".btn.followup").parent().append( format.datetime_now() );
                });
            });
            $(".form-select.complete").change(function() {
                $(".btn.complete").prop("disabled", $(".form-control.complete").val() == "");
            });
            $(".btn.complete").click(function() {
                $(".btn.complete .spinner-border").show();
                mobile.ajax_post("mode=inccomplete&ctype=" + $(".form-control.complete").val() + "&id=" + $(this).attr("data-id"), function() {
                    $(".btn.complete, .form-control.complete").hide();
                    $(".btn.complete").parent().append( $(".form-control.complete option:selected").text() + "<br>" );
                    $(".btn.complete").parent().append( format.datetime_now() );
                });
            });
            $(".showmap").click(function() {
                window.open(controller.maplink.replace("{0}", $(this).attr("data-address")));
            });
        },

        // Incidents
        render_incident_list: function(selector, backlink, incidents) {
            $(selector + " .list-group").empty();
            $.each(incidents, function(i, v) {
                let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                    '<h5 class="mb-1">' + format.date(v.INCIDENTDATETIME) + ': ' + v.INCIDENTNAME + ' - ' + v.DISPATCHADDRESS + '</h5>' +
                    '<small>' + v.CALLNOTES + '</small>' + 
                    '</a>';
                $(selector + " .list-group").append(h);
            });
            // When an incident link is clicked, display the record
            $(selector).on("click", "a", function() {
                let incidentid = format.to_int($(this).attr("data-id")), ac = null;
                $.each(incidents, function(i, v) {
                    if (v.ID == incidentid) { ac = v; return false; }
                });
                // Incidents rely on IDs to make accordions work - remove contents of all incident views before loading one
                $(".incident-view").empty();
                if (ac) { 
                    mobile.render_incident(ac, selector + "-view", backlink);
                }
            });
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

        // Returns the HTML for rendering a person record
        render_person: async function(p, selector) {
            const i = function(label, value) {
                if (!value) { value = ""; }
                return '<div class="row align-items-start"><div class="col">' + label + '</div><div class="col">' + value + '</div></div>';
            };
            const ph = function(label, value) {
                if (value) { value = '<a href="tel:+1' + value + '">' + value + '</a>'; }
                return i(label, value);
            };
            const em = function(label, value) {
                if (value) { value = '<a href="mailto:' + value + '">' + value + '</a>'; }
                return i(label, value);
            };
            const col3 = function(c1, c2, c3) {
                if (!c1 && !c2 && !c3) { return ""; }
                return '<div class="row align-items-start"><div class="col">' + c1 + '</div><div class="col">' + c2 + '</div><div class="col">' + c3 + '</div></div>';
            };
            const hd = function(value) {
                return '<div class="row align-items-start mt-3"><div class="col fw-bold">' + value + '</div></div>';
            };
            const n = function(s) {
                if (!s) { return ""; }
                return s;
            };
            const fgs = function(s) {
                let o = [];
                if (!s) { return ""; }
                $.each(s.split("|"), function(i, v) {
                    if (v.trim()) { o.push(v.trim()); }
                });
                return o.join(", ");
            };
            const aci = function(id, headerhtml, bodyhtml, show) {
                if (!show) { show=""; }
                return '<div class="accordion-item">' +
                    '<h2 class="accordion-header" id="heading-' + id + '">' +
                    '<button class="accordion-button ' + ( show ? "" : "collapsed") + '" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-' + id + 
                        '" aria-expanded="false" aria-controls="collapse-' + id + '">' + headerhtml + '</button></h2>' + 
                    '<div id="collapse-' + id + '" class="accordion-collapse collapse ' + show + '" aria-labelledby="heading-' + id + '" data-bs-parent="#accordion-person">' + 
                    '<div class="accordion-body">' + bodyhtml + '</div>' +
                    '</div></div>';
            };
            // Grab the extra data for this person from the backend
            let o = await common.ajax_post(mobile.post_handler, "mode=loadperson&id=" + p.ID);
            o = jQuery.parseJSON(o);
            p = o.person;
            let x = [];
            let h = [
                '<div class="list-group mt-3">',
                '<a href="#" data-link="personresults" class="list-group-item list-group-item-action internal-link">',
                '&#8592; ' + _("Back"),
                '</a>',
                '<div class="list-group-item">',
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(p, "personthumb") + '">',
                '<h5 class="mb-1">' + p.OWNERNAME + ' - ' + p.OWNERCODE + '</h5>',
                '<small>' + p.OWNERADDRESS + ', ' + p.OWNERTOWN + ' ' + p.OWNERCOUNTY + ' ' + p.OWNERPOSTCODE + '</small>',
                '<br/><small class="fst-italic">' + fgs(p.ADDITIONALFLAGS) + '</small>',
                '</div>',
                '</div>',

                '<div class="accordion" id="accordion-person">',

                aci("details", _("Person"), [
                    i(_("Title"), p.OWNERTITLE),
                    i(_("Initials"), p.OWNERINITIALS),
                    i(_("First name(s)"), p.OWNERFORENAMES),
                    i(_("Last name"), p.OWNERSURNAME),
                    ph(_("Home Phone"), p.HOMETELEPHONE),
                    ph(_("Work Phone"), p.WORKTELEPHONE),
                    ph(_("Cell Phone"), p.MOBILETELEPHONE),
                    em(_("Email"), p.EMAILADDRESS),
                    i(_("DOB"), format.date(p.DATEOFBIRTH)),
                    i(_("ID Number"), p.IDENTIFICATIONNUMBER),
                    i(_("Jurisdiction"), p.JURISDICTIONNAME),
                    
                    i(_("Address"), p.OWNERADDRESS),
                    i(_("City"), p.OWNERTOWN),
                    i(_("State"), p.OWNERCOUNTY),
                    i(_("Zipcode"), p.OWNERPOSTCODE),
                ].join("\n"), "show"),
            
                aci("type", _("Type"), [
                    i(_("Comments"), p.COMMENTS),
                    i(_("Warning"), p.POPUPWARNING),
                    i(_("Foster Capacity"), p.FOSTERCAPACITY),
                    i(_("Membership Number"), p.MEMBERSHIPNUMBER),
                    i(_("Membership Expiry"), format.date(p.MEMBERSHIPEXPIRY))
                ].join("\n"))
            ];
            if (o.additional.length > 0) {
                x = [];
                $.each(o.additional, function(d, v) {
                    x.push(i(v.NAME, v.VALUE)); 
                });
                h.push(aci("additional", _("Additional"), x.join("\n")));
            }
            if (common.has_permission("vacc") && o.citations.length > 0) {
                x = [];
                $.each(o.citations, function(d, v) {
                    x.push(col3(format.date(v.CITATIONDATE), v.CITATIONNAME, v.COMMENTS));
                });
                h.push(aci("citations", _("Citations"), x.join("\n")));
            }
            if (common.has_permission("vdn") && o.diary.length > 0) {
                x = [];
                $.each(o.diary, function(d, v) {
                    x.push(col3(format.date(v.DIARYDATETIME), v.SUBJECT, v.NOTE));
                });
                h.push(aci("diary", _("Diary"), x.join("\n")));
            }
            if (o.links.length > 0) {
                x = [];
                $.each(o.links, function(d, v) {
                    x.push(col3(v.TYPE, v.LINKDISPLAY, v.FIELD2));
                });
                h.push(aci("links", _("Links"), x.join("\n")));
            }
            if (common.has_permission("") && o.licences.length > 0) {
                x = [];
                $.each(o.licences, function(d, v) {
                    x.push(col3(v.LICENCENUMBER, format.date(v.ISSUEDATE), format.date(v.EXPIRYDATE)));
                });
                h.push(aci("licences", _("License"), x.join("\n")));
            }
            if (common.has_permission("vle") && o.logs.length > 0) {
                x = [];
                $.each(o.logs, function(d, v) {
                    x.push(col3(format.date(v.DATE), v.LOGTYPENAME, v.COMMENTS));
                });
                h.push(aci("log", _("Log"), x.join("\n")));
            }
            if (common.has_permission("ale")) {
                h.push(aci("addlog", _("Add Log"), mobile.render_addlog(p.ID, 1)));
            }
            h.push('</div>'); // close accordion
            $(selector).html( h.join("\n") );
            // Display our person now it's rendered
            $(".container").hide();
            $("#content-person").show();
        },

        render_shelteranimalslist: function() {
            // Load shelter animals list
            $("#content-shelteranimals .list-group").empty();
            $.each(controller.animals, function(i, v) {
                let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                    '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                    '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.CODE + '</h5>' +
                    '<small>(' + v.SEXNAME + ' ' + v.BREEDNAME + ' ' + v.SPECIESNAME + ')<br/>' + v.IDENTICHIPNUMBER + ' ' + mobile.display_location(v) + '</small>' +
                    '</a>';
                $("#content-shelteranimals .list-group").append(h);
            });
        },

        update_breed_select: function() {
            // Only show the breeds for the selected species
            $('optgroup', $('#breed1')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed1'));
            $('#breed1').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()){
                    $(this).remove();
                }
            });
        },

        update_units: async function() {
            let opts = ['<option value=""></option>'];
            $("#unit").empty();
            const response = await common.ajax_post("animal_new", "mode=units&locationid=" + $("#internallocation").val());
            $.each(html.decode(response).split("&&"), function(i, v) {
                let [unit, desc] = v.split("|");
                if (!unit) { return false; }
                if (!desc) { desc = _("(available)"); }
                opts.push('<option value="' + html.title(unit) + '">' + unit +
                    ' : ' + desc + '</option>');
            });
            $("#unit").html(opts.join("\n")).change();

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

            // When a shelter animal link is clicked, display the record
            $("#content-shelteranimals").on("click", "a", function() {
                let animalid = format.to_int($(this).attr("data-id")), a = null;
                $.each(controller.animals, function(i, v) {
                    if (v.ID == animalid) { a = v; return false; }
                });
                if (a) { 
                    mobile.render_animal(a, "#content-animal");
                }
            });

            // When the location is changed on the add animal screen, update the list of units
            $("#internallocation").change(function() {
                mobile.update_units();
            });

            // When species is changed on the add animal screen, update the breeds
            $("#species").change(function() {
                mobile.update_breed_select();
            });

            // Handle add animal
            $("#addanimal-submit").click(function() {
                $("#addanimal-submit .spinner-border").show();
                let formdata = {
                    "mode": "addanimal",
                    "animalname": $("#animalname").val(),
                    "sheltercode": $("#sheltercode").val(),
                    "estimatedage": $("#estimatedage").val(),
                    "sex": $("#sex").val(),
                    "type": $("#type").val(),
                    "species": $("#species").val(),
                    "breed1": $("#breed1").val(),
                    "basecolour": $("#basecolour").val(),
                    "size": $("#size").val(),
                    "internallocation": $("#internallocation").val(),
                    "unit": $("#unit").val()
                };
                mobile.ajax_post(formdata, function(response) {
                    let a = jQuery.parseJSON(response);
                    controller.animals.push(a);
                    mobile.render_animal(a, "#content-animal");
                    mobile.render_shelteranimalslist();
                    $(".container").hide();
                    $("#content-animal").show();
                    $("#addanimal-submit .spinner-border").hide();
                });
            });

            // Handle clicking an animal to medicate and showing a popup dialog to confirm
            $("#content-medicate").on("click", "a", function() {
                let treatmentid = $(this).attr("data-id");
                $.each(controller.medicals, function(i, v) {
                    if (v.TREATMENTID == treatmentid) {
                        $("#administerdlg .btn-primary").unbind("click");
                        $("#administerdlg .btn-primary").html(_("Give"));
                        $("#administerdlg .btn-primary").click(function() {
                            mobile.ajax_post("mode=medical&id=" + treatmentid, function() {
                                $("#content-medicate [data-id='" + treatmentid + "']").remove(); // remove the item from the list on success
                            });
                        });
                        $("#administertitle").html(_("Give Treatments"));
                        $("#administerresult").hide();
                        $("#administertext").html(format.date(v.DATEREQUIRED) + ": " + v.ANIMALNAME + ' - ' + v.SHELTERCODE + ': ' + v.TREATMENTNAME);
                        $("#administerdlg").modal("show");
                    }
                });
            });

            // Handle clicking an animal to test and showing a popup dialog to confirm
            $("#content-test").on("click", "a", function() {
                let testid = $(this).attr("data-id");
                $.each(controller.tests, function(i, v) {
                    if (v.ID == testid) {
                        $("#administerdlg .btn-primary").unbind("click");
                        $("#administerdlg .btn-primary").html(_("Perform"));
                        $("#administerdlg .btn-primary").click(function() {
                            mobile.ajax_post("mode=test&id=" + testid + "&resultid=" + $("#administerresult").val(), function() {
                                $("#content-test [data-id='" + testid + "']").remove(); // remove the item from the list on success
                            });
                        });
                        $("#administertitle").html(_("Perform Test"));
                        $("#administerresult").show();
                        $("#administertext").html(format.date(v.DATEREQUIRED) + ": " + v.ANIMALNAME + ' - ' + v.SHELTERCODE + ': ' + v.TESTNAME);
                        $("#administerdlg").modal("show");
                    }
                });
            });

            // Handle clicking an animal to vaccinate and showing a popup dialog to confirm
            $("#content-vaccinate").on("click", "a", function() {
                let vaccid = $(this).attr("data-id");
                $.each(controller.vaccinations, function(i, v) {
                    if (v.ID == vaccid) {
                        $("#administerdlg .btn-primary").unbind("click");
                        $("#administerdlg .btn-primary").html(_("Give"));
                        $("#administerdlg .btn-primary").click(function() {
                            mobile.ajax_post("mode=vaccinate&id=" + vaccid, function() {
                                $("#content-vaccinate [data-id='" + vaccid + "']").remove(); // remove the item from the list on success
                            });
                        });
                        $("#administertitle").html(_("Give Vaccination"));
                        $("#administerresult").hide();
                        $("#administertext").html(format.date(v.DATEREQUIRED) + ": " + v.ANIMALNAME + ' - ' + v.SHELTERCODE + ': ' + v.VACCINATIONTYPE);
                        $("#administerdlg").modal("show");
                    }
                });
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

            // Handle clicking on check licence button
            $("#btn-check-licence").click(function() {
                let spinner = $(this).find(".spinner-border");
                spinner.show();
                // Retrieve results
                let formdata = {
                    "mode": "checklicence",
                    "licencenumber": $("#licencenumber").val()
                };
                mobile.ajax_post(formdata, function(response) {
                    spinner.hide();
                    controller.licenceresults = jQuery.parseJSON(response);
                    // Display licence list
                    $("#content-licenceresults .list-group").empty();
                    $.each(controller.licenceresults, function(i, v) {
                        let a = '"' + v.ANIMALNAME + '": ' + common.substitute(_("{0} {1} aged {2}"), { "0": v.SEX, "1": v.SPECIESNAME, "2": v.ANIMALAGE }) + '<br>';
                        if (!v.ANIMALNAME) { a = ""; }
                        let h = '<div data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                            '<h5 class="mb-1">' + v.OWNERNAME + ' - ' + v.OWNERCODE + '</h5>' +
                            '<small>' + v.OWNERADDRESS + ', ' + v.OWNERTOWN + ' ' + v.OWNERCOUNTY + ' ' + v.OWNERPOSTCODE + '<br>' +
                            v.LICENCETYPENAME + ', ' + format.date(v.ISSUEDATE) + ' - ' + format.date(v.EXPIRYDATE) + 
                            a +
                            '</small>' +
                            '</div>';
                        $("#content-licenceresults .list-group").append(h);
                    });
                    $(".container").hide();
                    $("#content-licenceresults").show();
                });
            });

            // Handle clicking on find person button
            $("#btn-find-person").click(function() {
                let spinner = $(this).find(".spinner-border");
                spinner.show();
                // Retrieve results
                let formdata = {
                    "mode": "findperson",
                    "q": $("#personq").val()
                };
                mobile.ajax_post(formdata, function(response) {
                    spinner.hide();
                    controller.personresults = jQuery.parseJSON(response);
                    // Display person list
                    $("#content-personresults .results").empty();
                    $.each(controller.personresults, function(i, v) {
                        let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "personthumb") + '">' + 
                            '<h5 class="mb-1">' + v.OWNERNAME + ' - ' + v.OWNERCODE + '</h5>' +
                            '<small>(' + v.OWNERADDRESS + ', ' + v.OWNERTOWN + ' ' + v.OWNERCOUNTY + ' ' + v.OWNERPOSTCODE + ')</small>' +
                            '</a>';
                        $("#content-personresults .results").append(h);
                    });
                    $(".container").hide();
                    $("#content-personresults").show();
                });
            });

            // When a person result is clicked, display the record
            $("#content-personresults").on("click", "a", function() {
                let personid = format.to_int($(this).attr("data-id")), p = null;
                $.each(controller.personresults, function(i, v) {
                    if (v.ID == personid) { p = v; return false; }
                });
                if (p) { 
                    mobile.render_person(p, "#content-person");
                }
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

            // Handle clicking a person to mark homechecked
            $("#content-performhomecheck").on("click", "a", function() {
                let pid = $(this).attr("data-id");
                $.each(controller.rsvhomecheck, function(i, v) {
                    if (v.ID == pid) {
                        $("#administerdlg .btn-primary").unbind("click");
                        $("#administerdlg .btn-primary").html(_("Homechecked"));
                        $("#administerdlg .btn-primary").click(function() {
                            mobile.ajax_post("mode=homecheck&id=" + pid, function() {
                                $("#content-performhomecheck [data-id='" + pid + "']").remove(); // remove the item from the list on success
                            });
                        });
                        $("#administertitle").html(_("Perform Homecheck"));
                        $("#administerresult").hide();
                        $("#administertext").html(v.OWNERNAME + ' - ' + v.OWNERCODE + '<br>' + v.COMMENTS);
                        $("#administerdlg").modal("show");
                    }
                });
            });

            // Create the stock take screen for this location
            let active_stocklocation = "";
            $("#content-stocklocations").on("click", "a", function() {
                let pid = $(this).attr("data-id");
                active_stocklocation = $(this).find(".stock-locationname").text();
                mobile.ajax_post("mode=getstocklevel&id=" + pid, function(response) {
                    let j = jQuery.parseJSON(response);
                    let usage = '<div class="mb-3">' +
                        '<label for="usagetype" class="form-label">' + _("Usage Type") + '</label>' +
                        '<select class="form-select" id="usagetype" name="usage">' +
                        html.list_to_options(j.usagetypes, "ID", "USAGETYPENAME") +
                        '</select>' +
                        '</div>';
                    $("#content-stocktake .locations").empty();
                    $("#content-stocktake .locations").prepend(usage);
                    $.each(j.levels, function(i, v) {
                        let h = '<div class="list-group-item list-group-item-action">' +
                            '<div class="mb-3">' +
                            '<label class="form-label">' + v.NAME + ' (' + v.BALANCE + '/' + v.TOTAL + ')</label>' + 
                            '<input type="text" class="form-control stockbalance" data-id="' + v.ID + '" value="' + v.BALANCE + '">' +
                            '</div>' +
                            '</div>';
                        $("#content-stocktake .locations").append(h);
                    });
                    $("#btn-submit-stocktake").toggle( j.levels.length > 0 );
                    $(".container").hide();
                    $("#content-stocktake").show();
                });
            });

            // Handle submitting the stock take
            $("#btn-submit-stocktake").click(function() {
                let x = [];
                $("#content-stocktake .stockbalance").each(function() {
                    x.push("sl" + $(this).attr("data-id") + "=" + $(this).val());
                });
                $("#btn-submit-stocktake .spinner-border").show();
                mobile.ajax_post("mode=stocktake&usagetype=" + $("#usagetype").val() + "&" + x.join("&"), function() {
                    $("#btn-submit-stocktake .spinner-border").hide();
                    mobile.show_info(_("Stock Take"), _("Stock levels for location '{0}' updated.").replace("{0}", active_stocklocation));
                    $(".container").hide();
                    $("#content-stocklocations").show();
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

            mobile.render_incident_list("#content-myincidents", "myincidents", controller.incidentsmy);
            mobile.render_incident_list("#content-opincidents", "opincidents", controller.incidentsincomplete);
            mobile.render_incident_list("#content-unincidents", "unincidents", controller.incidentsundispatched);
            mobile.render_incident_list("#content-flincidents", "flincidents", controller.incidentsfollowup);
            mobile.render_messages(controller.messages);
            mobile.render_shelteranimalslist();

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

            // Load list of animals to medicate
            $("#content-medicate .list-group").empty();
            $.each(controller.medicals, function(i, v) {
                let h = '<a href="#" data-id="' + v.TREATMENTID + '" class="list-group-item list-group-item-action">' +
                    '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                    '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                    '<small>(' + v.TREATMENTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile.display_location(v) + '</small>' +
                    '</a>';
                $("#content-medicate .list-group").append(h);
            });

            // Load list of animals to test
            $("#content-test .list-group").empty();
            $.each(controller.tests, function(i, v) {
                let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                    '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                    '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                    '<small>(' + v.TESTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile.display_location(v) + '</small>' +
                    '</a>';
                $("#content-test .list-group").append(h);
            });

            // Load list of animals to vaccinate
            $("#content-vaccinate .list-group").empty();
            $.each(controller.vaccinations, function(i, v) {
                let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                    '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                    '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                    '<small>(' + v.VACCINATIONTYPE + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile.display_location(v) + '</small>' +
                    '</a>';
                $("#content-vaccinate .list-group").append(h);
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

            // Load stock locations list
            $("#content-stocklocations .list-group").empty();
            $.each(controller.stocklocations, function(i, v) {
                let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                    '<h5 class="mb-1"><span class="stock-locationname">' + v.LOCATIONNAME + '</span> ' + 
                    '<span class="badge bg-primary rounded-pill">' + v.TOTAL + '</span>' + '</h5>' +
                    '<small>' + v.LOCATIONDESCRIPTION + '</small>' + 
                    '</a>';
                $("#content-stocklocations .list-group").append(h);
            });

            // Load list of homechecks to perform
            $("#content-performhomecheck .list-group").empty();
            $.each(controller.rsvhomecheck, function(i, v) {
                    let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                        '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "personthumb") + '">' + 
                        '<h5 class="mb-1">' + v.OWNERNAME + ' - ' + v.OWNERCODE + '</h5>' +
                        '<small>(' + v.OWNERADDRESS + ', ' + v.OWNERTOWN + ' ' + v.OWNERCOUNTY + ' ' + v.OWNERPOSTCODE + ')</small>' +
                        '</a>';
                $("#content-performhomecheck .list-group").append(h);
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

            // Initialise add animal screen
            $("#age").val(config.str("DefaultAnimalAge"));
            $("#animaltype").val(config.str("AFDefaultType"));
            $("#basecolour").val(config.str("AFDefaultColour"));
            $("#internallocation").val(config.str("AFDefaultLocation"));
            mobile.update_units();
            $("#species").val(config.str("AFDefaultSpecies"));
            mobile.update_breed_select();
            $("#breed1").val(config.str("AFDefaultBreed"));
            $("#size").val(config.str("AFDefaultSize"));
            $("#sheltercode").closest("div").toggle(config.bool("ManualCodes"));
        
            // Switch to oldui button - remove 1/11/24
            $("#oldui").click(function() {
                window.location = "mobile";
            });

            // Show the dashboard/homepage
            $("#content-home").show();

            document.title = controller.user + ": " + _("ASM");
        }
    };

    $("body").html(mobile.render());
    mobile.bind();
    mobile.sync();

});


