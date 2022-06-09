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
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("Add Animal") + '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="shelteranimals" href="#">' + _("Shelter Animals"),
                                '<span class="badge bg-primary rounded-pill">' + controller.animals.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Vaccinate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.vaccinations.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Test Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.tests.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link internal-link" data-link="medicate" href="#">' + _("Medicate Animal"),
                                '<span class="badge bg-primary rounded-pill">' + controller.medicals.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("Add Log to Animal") + '</a>',
                        '</li>',
                    '</ul>',
                '</li>',
                '<li class="nav-item dropdown">',
                    '<a class="nav-link dropdown-toggle" href="#" id="dropdown-incidents" role="button" data-bs-toggle="dropdown" aria-expanded="false">',
                    _("Animal Control") + '</a>',
                    '<ul class="dropdown-menu" aria-labelledby="dropdown-incidents">',
                        '<li class="dropdown-item">',
                            '<a class="nav-link" href="#">' + _("Add Call") + '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("My Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsmy.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("My Undispatched Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsundispatched.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Open Incidents"),
                                '<span class="badge bg-primary rounded-pill">' + controller.incidentsincomplete.length + '</span>',
                            '</a>',
                        '</li>',
                        '<li class="dropdown-item hideifzero">',
                            '<a class="nav-link" href="#">' + _("Incidents Requiring Followup"),
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
        '<div id="content-medicateanimal" class="container" style="display: none">',
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

    // Returns the HTML for rendering an animal record
    const render_animal = function(a) {
        
        const i = function(label, value) {
            if (!value) { value = ""; }
            return '<div class="row align-items-start"><div class="col">' + label + '</div><div class="col">' + value + '</div></div>';
        };
        const n = function(s) {
            if (!s) { return ""; }
            return s;
        };
        let [adoptable, adoptreason] = html.is_animal_adoptable(a);
        let h = [
            '<div class="list-group" style="margin-top: 5px">',
            '<a href="#" data-link="shelteranimals" class="list-group-item list-group-item-action internal-link">',
            '&#8592; ' + _("Back"),
            '</a>',
            '<div class="list-group-item">',
            '<img style="float: right" src="' + html.thumbnail_src(a, "animalthumb") + '">',
            '<h5 class="mb-1">' + a.ANIMALNAME + ' - ' + a.CODE + '</h5>',
            '<small>' + common.substitute(_("{0} {1} {2} aged {3}"), { "0": a.SEXNAME, "1": a.BREEDNAME, "2": a.SPECIESNAME, "3": a.ANIMALAGE }) + '<br/>',
            a.IDENTICHIPNUMBER + '</small><br/>',
            '<button type="button" id="uploadphoto" class="btn btn-primary">' + _("Upload"),
            '<i class="bi-cloud-upload-fill"></i>',
            '</button>',
            '<input type="file" accept="image/*" id="uploadphotofile" style="display: none" />',
            '</div>',
            '</div>',

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
            i(_("Housetrained"), a.ISHOUSETRAINEDNAME),
            
            common.has_permission("vo") ? i(_("Original Owner"), a.ORIGINALOWNERNAME) : "",
            common.has_permission("vo") ? i(_("Brought In By"), a.BROUGHTINBYOWNERNAME) : "",

            i(_("Date Brought In"), format.date(a.DATEBROUGHTIN)),
            i(_("Bonded With"), n(a.BONDEDANIMAL1CODE) + " " + n(a.BONDEDANIMAL1NAME) + " " + n(a.BONDEDANIMAL2CODE) + " " + n(a.BONDEDANIMAL2NAME)),
            i(_("Transfer"), a.ISTRANSFERNAME),
            i(_("Entry Category"), a.ENTRYREASONNAME),
            i(_("Entry Reason"), a.REASONFORENTRY),

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
        ];
        return h.join("\n");
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
            '<small>(' + v.SEXNAME + ' ' + v.BREEDNAME + ' ' + v.SPECIESNAME + ') ' + v.IDENTICHIPNUMBER + '</small>' +
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
            $("#content-animal").html( render_animal(a) ); 
            $(".container").hide();
            $("#content-animal").show();
            // Handle the uploading of a photo when one is chosen
            $("#uploadphoto").click(function() { $("#uploadphotofile").click(); });
            $("#uploadphotofile").change(function() { alert($("#uploadphotofile").val()); });
        }
    });
   
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
    $("#content-medicate").on("click", "a", function() {
        // TODO: render more info on the medication with a button to mark it given
    });

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
    let cgroup = "";
    $.each(controller.reports, function(i, v) {
        if (cgroup != v.CATEGORY) {
            cgroup = v.CATEGORY;
            $("#content-reports .list-group").append('<div class="list-group-item bg-secondary text-white fw-bold">' + v.CATEGORY + '</div>');
        }
        let h = '<a class="list-group-item list-group-item-action" href="mobile_report?id=' + v.ID + '">' + v.TITLE + '</a>';
        $("#content-reports .list-group").append(h);
    });

    document.title = controller.user + ": " + _("ASM");

});


