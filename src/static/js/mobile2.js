/*global $, controller */

$(document).ready(function() {

    "use strict";

    const post_handler = "mobile2";

    const show_info = function(title, body) {
        $("#infotitle").html(title);
        $("#infotext").html(body);
        $("#infodlg").modal("show");
    };

    const show_error = function(title, body) {
        $("#errortitle").html(title);
        $("#errortext").html(body);
        $("#errordlg").modal("show");
    };

    const ajax_post = function(formdata, successfunc, errorfunc) {
        $.ajax({
            type: "POST",
            url: post_handler,
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
                show_error(textstatus, response);
            }
        });
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
                    '<div id="administertext" class="modal-body">',
                    '</div>',
                    '<div class="modal-footer">',
                        '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">' + _("Cancel") + '</button>',
                        '<button type="button" class="btn btn-primary" data-bs-dismiss="modal">' + _("Give") + '</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>',
        '<nav class="navbar navbar-expand-lg navbar-light bg-light">',
            '<div class="container-fluid">',
                '<a class="navbar-brand" href="#">' + controller.user + ': ' + _("ASM") + '</a>',
                '<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar-content" aria-controls="navbar-content" aria-expanded="false" aria-label="Toggle navigation">',
                    '<span class="navbar-toggler-icon"></span>',
                '</button>',
                '<div class="collapse navbar-collapse" id="navbar-content">',
                '<ul class="navbar-nav me-auto mb-2 mb-lg-0">',
                '<li class="nav-item">',
                    '<a class="nav-link internal-link" data-link="messages" href="#">' + _("Messages"),
                        '<span class="badge bg-primary rounded-pill">' + controller.messages.length + '</span>',
                    '</a>',
                '</li>',
                '<li class="nav-item">',
                    '<a class="nav-link internal-link" data-link="reports" href="#">' + _("Generate Report"),
                    '</a>',
                '</li>',
                '<li class="nav-item">',
                    '<a class="nav-link" href="mobile_sign">' + _("Signing Pad"),
                    '</a>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-animals" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Animals") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-animals">',
                        /*'<li class="dropdown-item">',
                            '<a class="nav-link internal-link" data-link="addanimal" href="#">' + _("Add Animal") + '</a>',
                        '</li>',*/
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="mobile_photo_upload">' + _("Photo Uploader"),
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="shelteranimals" href="#">' + _("Shelter Animals"),
                                '<span class="badge bg-primary rounded-pill">' + controller.animals.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="vaccinate" href="#">' + _("Vaccinate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.vaccinations.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="test" href="#">' + _("Test Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.tests.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="medicate" href="#">' + _("Medicate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.medicals.length + '</span>',
                            '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-incidents" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Animal Control") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-incidents">',
                        /*'<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("Add Call") + '</a>',
                        '</li>',*/
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="myincidents" href="#">' + _("My Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsmy.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="unincidents" href="#">' + _("My Undispatched Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsundispatched.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="opincidents" href="#">' + _("Open Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsincomplete.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="flincidents" href="#">' + _("Incidents Requiring Followup"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsfollowup.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item">',
                            '<a class="nav-link internal-link" data-link="checklicence" href="#">' + _("Check License") + '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-diary" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Diary") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-diary">',
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("New Task") + '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Complete Tasks"),
                                '<span class="badge bg-primary rounded-pill">' + controller.diaries.length + '</span>',
                            '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-financial" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Financial") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-financial">',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Stock Take"),
                                '<span class="badge bg-primary rounded-pill">' + controller.stocklocations.length + '</span>',
                            '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-person" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Person") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-person">',
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("Find Person"),
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Perform Homecheck"),
                                '<span class="badge bg-primary rounded-pill">' + controller.rsvhomecheck.length + '</span>',
                            '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item">',
                    '<a class="nav-link" href="main">' + _("Desktop/Tablet UI"),
                    '</a>',
                '</li>',
                '<li class="nav-item">',
                    '<a class="nav-link" href="mobile_logout">' + _("Logout"),
                    '</a>',
                '</li>',
                '</ul>',
            '</div>',
        '</nav>',

        '<div id="content-messages" class="container" style="display: none">',
        '<h2>' + _("Messages") + '</h2>',
        '<div class="list-group">',
        '</div>',
        '</div>',

        '<div id="content-reports" class="container" style="display: none">',
        '<h2>' + _("Reports") + '</h2>',
        '<div class="list-group">',
        '</div>',
        '</div>',

        /*
        '<div id="content-addanimal" class="container" style="display: none">',
        '<h2>' + _("Add Animal") + '</h2>',
        '<form method="post" action="' + post_handler + '">',
        '<input type="hidden" name="mode" value="addanimal">',
        '<div class="mb-3">',
            '<label for="name" class="form-label">' + _("Name") + '</label>',
            '<input type="text" class="form-control" id="name" name="name">',
        '</div>',
        '<div class="mb-3">',
            '<label for="sheltercode" class="form-label">' + _("Code") + '</label>',
            '<input type="text" class="form-control" id="sheltercode" name="sheltercode">',
        '</div>',
        '<div class="mb-3">',
            '<label for="age" class="form-label">' + _("Age") + '</label>',
            '<input type="text" class="form-control" id="age" name="age" value="1.0">',
        '</div>',
        '<div class="mb-3">',
            '<label for="sex" class="form-label">' + _("Sex") + '</label>',
            '<select class="form-control" name="sex" id="sex">',
            html.list_to_options(controller.sexes, "ID", "SEX"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="animaltype" class="form-label">' + _("Type") + '</label>',
            '<select class="form-control" name="animaltype" id="animaltype">',
            html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="species" class="form-label">' + _("Species") + '</label>',
            '<select class="form-control" name="species" id="species">',
            html.list_to_options(controller.species, "ID", "SPECIESNAME"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="breed1" class="form-label">' + _("Breed") + '</label>',
            '<select class="form-control" name="breed1" id="breed1">',
            html.list_to_options_breeds(controller.breeds),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="basecolour" class="form-label">' + _("Color") + '</label>',
            '<select class="form-control" name="basecolour" id="basecolour">',
            html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="size" class="form-label">' + _("Size") + '</label>',
            '<select class="form-control" name="size" id="size">',
            html.list_to_options(controller.sizes, "ID", "SIZE"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="internallocation" class="form-label">' + _("Location") + '</label>',
            '<select class="form-control" name="internallocation" id="internallocation">',
            html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
            '</select>',
        '</div>',
        '<div class="mb-3">',
            '<label for="unit" class="form-label">' + _("Unit") + '</label>',
            '<input type="text" class="form-control" id="unit" name="unit">',
        '</div>',
        '<div class="d-flex justify-content-center pb-2"><button id="btn-addanimal-submit" type="submit" class="btn btn-primary">' + _("Create") + 
        '<div class="spinner-border spinner-border-sm" style="display: none"></div></button></div>',
        '</form>',
        '</div>',
        */

        '<div id="content-shelteranimals" class="container" style="display: none">',
        '<h2>' + _("Shelter Animals") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',
        '<div id="content-animal" class="container" style="display: none">',
        '</div>',

        '<div id="content-medicate" class="container" style="display: none">',
        '<h2>' + _("Medicate Animal") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',

        '<div id="content-vaccinate" class="container" style="display: none">',
        '<h2>' + _("Vaccinate Animal") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',

        '<div id="content-test" class="container" style="display: none">',
        '<h2>' + _("Test Animal") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',

        '<div id="content-myincidents" class="container" style="display: none">',
        '<h2>' + _("My Incidents") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',
        '<div id="content-myincidents-view" class="incident-view container" style="display: none">',
        '</div>',

        '<div id="content-unincidents" class="container" style="display: none">',
        '<h2>' + _("My Undispatched Incidents") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',
        '<div id="content-unincidents-view" class="incident-view container" style="display: none">',
        '</div>',

        '<div id="content-opincidents" class="container" style="display: none">',
        '<h2>' + _("Open Incidents") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',
        '<div id="content-opincidents-view" class="incident-view container" style="display: none">',
        '</div>',

        '<div id="content-flincidents" class="container" style="display: none">',
        '<h2>' + _("Incidents Requiring Followup") + '</h2>',
        '<div class="mb-3">',
        '<input class="form-control search" type="text" placeholder="' + _("Search") + '">',
        '</div>',
        '<div class="list-group">',
        '</div>',
        '</div>',
        '<div id="content-flincidents-view" class="incident-view container" style="display: none">',
        '</div>',

        '<div id="content-checklicence" class="container" style="display: none">',
        '<h2>' + _("Check License") + '</h2>',
            '<div class="mb-3">',
                '<label for="licencenumber" class="form-label">' + _("License Number") + '</label>',
                '<input type="text" class="form-control" id="licencenumber">',
            '</div>',
            '<button id="btn-check-licence" type="button" class="btn btn-primary">Check',
            '<div class="spinner-border spinner-border-sm" style="display: none"></div>',
            '</button>',
            '</div>',
        '</div>'

    ].join("\n");

    $("body").html(h);

    // Returns the HTML for an add log slider
    const render_addlog = function(linkid, linktypeid) {
        return [
            '<div class="mb-3">',
                '<label for="logtype" class="form-label">' + _("Log Type") + '</label>',
                '<select class="form-control" id="logtype" name="logtypeid">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="comments" class="form-label">' + _("Log Text") + '</label>',
                '<input type="text" class="form-control" id="comments" name="comments">',
            '</div>',
            '<div class="d-flex justify-content-center pb-2">',
            '<button data-linkid="' + linkid + '" data-linktypeid="' + linktypeid + '" type="button" class="btn btn-primary addlog">' + _("Create"),
            '<div class="spinner-border spinner-border-sm" style="display: none"></div></button>',
            '</div>'
        ].join("\n");
    };

    // Returns the HTML for rendering an animal record
    const render_animal = async function(a, selector) {
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
        const fgs = function(s) {
            let o = [];
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
        let o = await common.ajax_post(post_handler, "mode=loadanimal&id=" + a.ID);
        o = jQuery.parseJSON(o);
        let [adoptable, adoptreason] = html.is_animal_adoptable(a);
        let x = [];
        let h = [
            '<div class="list-group mt-3">',
            '<a href="#" data-link="shelteranimals" class="list-group-item list-group-item-action internal-link">',
            '&#8592; ' + _("Back"),
            '</a>',
            '<div class="list-group-item">',
            '<img style="float: right" src="' + html.thumbnail_src(a, "animalthumb") + '">',
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
                i(_("Location"), a.DISPLAYLOCATION),
                i(_("Color"), a.BASECOLOURNAME),
                i(_("Coat Type"), a.COATTYPENAME),
                i(_("Size"), a.SIZENAME),
                i(_("DOB"), format.date(a.DATEOFBIRTH) + " (" + a.ANIMALAGE + ")"),
                
                i(_("Markings"), a.MARKINGS),
                i(_("Hidden Comments"), a.HIDDENANIMALDETAILS),
                i(_("Description"), a.ANIMALCOMMENTS),
                
                i(_("Cats"), a.ISGOODWITHCATSNAME),
                i(_("Dogs"), a.ISGOODWITHDOGSNAME),
                i(_("Children"), a.ISGOODWITHCHILDRENNAME),
                i(_("Housetrained"), a.ISHOUSETRAINEDNAME)
            ].join("\n"), "show"),
           
            aci("entry", _("Entry"), [
                i(_("Date Brought In"), format.date(a.DATEBROUGHTIN)),
                i(_("Transfer"), a.ISTRANSFERNAME),
                i(_("Entry Category"), a.ENTRYREASONNAME),
                i(_("Entry Reason"), a.REASONFORENTRY),
                common.has_permission("vo") ? i(_("Original Owner"), a.ORIGINALOWNERNAME) : "",
                common.has_permission("vo") ? i(_("Brought In By"), a.BROUGHTINBYOWNERNAME) : "",
                i(_("Bonded With"), n(a.BONDEDANIMAL1CODE) + " " + n(a.BONDEDANIMAL1NAME) + " " + n(a.BONDEDANIMAL2CODE) + " " + n(a.BONDEDANIMAL2NAME))
            ].join("\n")),

            aci("health", _("Health and Identification"), [
                i(_("Microchipped"), format.date(a.IDENTICHIPDATE) + " " + a.IDENTICHIPPED==1 ? a.IDENTICHIPNUMBER : ""),
                i(_("Tattoo"), format.date(a.TATTOODATE) + " " + a.TATTOO==1 ? a.TATTOONUMBER : ""),
                i(_("Neutered"), a.NEUTEREDNAME + " " + format.date(a.NEUTEREDDATE)),
                i(_("Declawed"), a.DECLAWEDNAME),
                i(_("Heartworm Tested"), format.date(a.HEARTWORMTESTDATE) + " " + a.HEARTWORMTESTED==1 ? a.HEARTWORMTESTRESULTNAME : ""),
                i(_("FIV/L Tested"), format.date(a.COMBITESTDATE) + " " + a.COMBITESTED==1 ? a.COMBITESTRESULTNAME + " " + a.FLVRESULTNAME : ""),
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
                x.push(col3(format.date(v.DATEREQUIRED), format.date(v.DATEOFVACCINATION), v.VACCINATIONTYPE));
            });
            h.push(aci("vacc", _("Vaccination"), x.join("\n")));
        }
        if (common.has_permission("vat") && o.tests.length > 0) {
            x = [];
            $.each(o.tests, function(d, v) {
                x.push(col3(format.date(v.DATEREQUIRED), format.date(v.DATEOFTEST), v.TESTNAME + " " + (v.DATEOFTEST ? v.RESULTNAME : "")));
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
            // TODO: section to add a new log message to the animal
            $.each(o.logs, function(d, v) {
                x.push(col3(format.date(v.DATE), v.LOGTYPENAME, v.COMMENTS));
            });
            h.push(aci("log", _("Log"), x.join("\n")));
        }
        if (common.has_permission("ale")) {
            h.push(aci("addlog", _("Add Log"), render_addlog(a.ID, 0)));
        }
        h.push('</div>'); // close accordion
        $(selector).html( h.join("\n") );
        // Display our animal now it's rendered
        $(".container").hide();
        $("#content-animal").show();
        // Handle the uploading of a photo when one is chosen
        $("#content-animal .uploadphoto").click(function() { $("#content-animal .uploadphotofile").click(); });
        $("#content-animal .uploadphotofile").change(function() { alert($("#content-animal .uploadphotofile").val()); });
    };

    // Renders an incident record into the selector given
    const render_incident = async function(ac, selector, backlink) {
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
        // Inline buttons for completing, dispatching and responding, either the date or a button
        let comptp = dt(ac.COMPLETEDATE) + ' ' + ac.COMPLETEDNAME;
        if (!ac.COMPLETEDDATE && common.has_permission("caci")) {
            comptp = '<select class="form-control complete"><option value=""></option>' + html.list_to_options(controller.completedtypes, "ID", "COMPLETEDNAME") + '</select>';
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
        let dispadd = ac.DISPATCHADDRESS;
        if (dispadd) {
            let encadd = encodeURIComponent(ac.DISPATCHADDRESS + ',' + ac.DISPATCHTOWN + ',' + ac.DISPATCHCOUNTY + ',' + ac.DISPATCHPOSTCODE);
            dispadd = '<button type="button" data-address="' + encadd + '" class="showmap btn btn-secondary"><i class="bi-map"></i></button> ' + ac.DISPATCHADDRESS;
        }
        // Grab the extra data for this incident from the backend
        let o = await common.ajax_post(post_handler, "mode=loadincident&id=" + ac.ID);
        o = jQuery.parseJSON(o);
        let x= [];
        let h = [
            '<div class="list-group" style="margin-top: 5px">',
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
        $.each(o.animals, function(x, v) {
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
            aci("citations", _("Citations"), x.join("\n"));
        }
        if (common.has_permission("vdn") && o.diary.length > 0) {
            x = [];
            $.each(o.diary, function(d, v) {
                x.push(col3(format.date(v.DIARYDATETIME), v.SUBJECT, v.NOTE));
            });
            aci("diary", _("Diary"), x.join("\n"));
        }
        if (common.has_permission("vle") && o.logs.length > 0) {
            x = [];
            $.each(o.logs, function(d, v) {
                x.push(col3(format.date(v.DATE), v.LOGTYPENAME, v.COMMENTS));
            });
            aci("log", _("Log"), x.join("\n"));
        }
        if (common.has_permission("ale")) {
            h.push(aci("addlog", _("Add Log"), render_addlog(ac.ID, 6)));
        }
        h.push("</div>"); // close accordion
        $(selector).html( h.join("\n") );
        // Display the record
        $(".container").hide();
        $(selector).show();
        $(".btn.dispatch").click(function() {
            $(".btn.dispatch .spinner-border").show();
            ajax_post("mode=incdispatch&id=" + $(this).attr("data-id"), function() {
                $(".btn.dispatch").hide();
                $(".btn.dispatch").parent().append( format.datetime_now() );
            });
        });
        $(".btn.respond").click(function() {
            $(".btn.respond .spinner-border").show();
            ajax_post("mode=increspond&id=" + $(this).attr("data-id"), function() {
                $(".btn.respond").hide();
                $(".btn.respond").parent().append( format.datetime_now() );
            });
        });
        $(".form-control.complete").change(function() {
            $(".btn.complete").prop("disabled", $(".form-control.complete").val() == "");
        });
        $(".btn.complete").click(function() {
            $(".btn.complete .spinner-border").show();
            ajax_post("mode=inccomplete&ctype=" + $(".form-control.complete").val() + "&id=" + $(this).attr("data-id"), function() {
                $(".btn.complete, .form-control.complete").hide();
                $(".btn.complete").parent().append( $(".form-control.complete option:selected").text() + "<br>" );
                $(".btn.complete").parent().append( format.datetime_now() );
            });
        });
        $(".showmap").click(function() {
            window.open(controller.maplink.replace("{0}", $(this).attr("data-address")));
        });
    };

    // Hide all the elements with hideifzero if they have a badge containing zero
    $(".hideifzero").each(function() {
        $(this).toggle( $(this).find("span.badge").text() != "0" );
    });

    // Delegate handler for internal links
    $("body").on("click", ".internal-link", function() {
        let target = $(this).attr("data-link");
        if (target) {
            $(".container").hide();
            $("#content-" + target).show();
        }
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

    // Load shelter animals list
    $("#content-shelteranimals .list-group").empty();
    $.each(controller.animals, function(i, v) {
        let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
            '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.CODE + '</h5>' +
            '<small>(' + v.SEXNAME + ' ' + v.BREEDNAME + ' ' + v.SPECIESNAME + ')<br/>' + v.IDENTICHIPNUMBER + ' ' + v.DISPLAYLOCATION + '</small>' +
            '</a>';
        $("#content-shelteranimals .list-group").append(h);
    });
    // When a shelter animal link is clicked, display the record
    $("#content-shelteranimals").on("click", "a", function() {
        let animalid = format.to_int($(this).attr("data-id")), a = null;
        $.each(controller.animals, function(i, v) {
            if (v.ID == animalid) { a = v; return false; }
        });
        if (a) { 
            render_animal(a, "#content-animal");
        }
    });

    // Initialise add animal screen
    $("#age").val(config.str("DefaultAnimalAge"));
    $("#animaltype").val(config.str("AFDefaultType"));
    $("#species").val(config.str("AFDefaultSpecies"));
    $("#breed1").val(config.str("AFDefaultBreed"));
    $("#basecolour").val(config.str("AFDefaultColour"));
    $("#internallocation").val(config.str("AFDefaultLocation"));
    $("#unit").val("");
    $("#size").val(config.str("AFDefaultSize"));
    $("#sheltercode").closest("div").toggle(config.bool("ManualCodes"));
   
    // Load list of animals to medicate
    $("#content-medicate .list-group").empty();
    $.each(controller.medicals, function(i, v) {
        let h = '<a href="#" data-id="' + v.TREATMENTID + '" class="list-group-item list-group-item-action">' +
            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
            '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
            '<small>(' + v.TREATMENTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + v.DISPLAYLOCATION + '</small>' +
            '</a>';
        $("#content-medicate .list-group").append(h);
    });
    // Handle clicking an animal to medicate and showing a popup dialog to confirm
    $("#content-medicate").on("click", "a", function() {
        let treatmentid = $(this).attr("data-id");
        $.each(controller.medicals, function(i, v) {
            if (v.TREATMENTID == treatmentid) {
                $("#administerdlg .btn-primary").unbind("click");
                $("#administerdlg .btn-primary").click(function() {
                    ajax_post("mode=medical&id=" + treatmentid, function() {
                        $("#content-medicate [data-id='" + treatmentid + "']").remove(); // remove the item from the list on success
                    });
                });
                $("#administertitle").html(_("Give Treatments"));
                $("#administertext").html(format.date(v.DATEREQUIRED) + ": " + v.ANIMALNAME + ' - ' + v.SHELTERCODE + ': ' + v.TREATMENTNAME);
                $("#administerdlg").modal("show");
            }
        });
    });

    // Load list of animals to test
    $("#content-test .list-group").empty();
    $.each(controller.tests, function(i, v) {
        let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
            '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
            '<small>(' + v.TESTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + v.DISPLAYLOCATION + '</small>' +
            '</a>';
        $("#content-test .list-group").append(h);
    });
    // Handle clicking an animal to test and showing a popup dialog to confirm
    $("#content-test").on("click", "a", function() {
        let testid = $(this).attr("data-id");
        $.each(controller.tests, function(i, v) {
            if (v.ID == testid) {
                $("#administerdlg .btn-primary").unbind("click");
                $("#administerdlg .btn-primary").click(function() {
                    ajax_post("mode=test&id=" + testid, function() {
                        $("#content-test [data-id='" + testid + "']").remove(); // remove the item from the list on success
                    });
                });
                $("#administertitle").html(_("Perform Test"));
                $("#administertext").html(format.date(v.DATEREQUIRED) + ": " + v.ANIMALNAME + ' - ' + v.SHELTERCODE + ': ' + v.TESTNAME);
                $("#administerdlg").modal("show");
            }
        });
    });

    // Load list of animals to vaccinate
    $("#content-vaccinate .list-group").empty();
    $.each(controller.vaccinations, function(i, v) {
        let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
            '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
            '<small>(' + v.VACCINATIONTYPE + ', ' + format.date(v.DATEREQUIRED) + ') ' + v.DISPLAYLOCATION + '</small>' +
            '</a>';
        $("#content-vaccinate .list-group").append(h);
    });
    // Handle clicking an animal to vaccinate and showing a popup dialog to confirm
    $("#content-vaccinate").on("click", "a", function() {
        let vaccid = $(this).attr("data-id");
        $.each(controller.vaccinations, function(i, v) {
            if (v.ID == vaccid) {
                $("#administerdlg .btn-primary").unbind("click");
                $("#administerdlg .btn-primary").click(function() {
                    ajax_post("mode=vaccinate&id=" + vaccid, function() {
                        $("#content-vaccinate [data-id='" + vaccid + "']").remove(); // remove the item from the list on success
                    });
                });
                $("#administertitle").html(_("Give Vaccination"));
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

        ajax_post(formdata, function() {
            show_info(_("Log message added"), comments.val());
            comments.val("");
        });
    });

    // Incidents
    const render_incident_list = function(selector, backlink, incidents) {
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
                render_incident(ac, selector + "-view", backlink);
            }
        });
    };
    render_incident_list("#content-myincidents", "myincidents", controller.incidentsmy);
    render_incident_list("#content-opincidents", "opincidents", controller.incidentsincomplete);
    render_incident_list("#content-unincidents", "unincidents", controller.incidentsundispatched);
    render_incident_list("#content-flincidents", "flincidents", controller.incidentsfollowup);

    // Load messages 
    $("#content-messages .list-group").empty();
    $.each(controller.messages, function(i, v) {
        let h = '<div class="list-group-item">' +
            '<h5>' + format.date(v.ADDED) + ' ' + v.CREATEDBY + ' &#8594; ' + v.FORNAME + '</h5>' + 
            '<small>' + v.MESSAGE + '</small>';
        $("#content-messages .list-group").append(h);
    });

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
    $("#content-reports").html(reps.join("\n"));

    document.title = controller.user + ": " + _("ASM");

});


