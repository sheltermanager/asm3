/*global $, controller, mobile */
/* mobile_ui_person: true */

"use strict";

const mobile_ui_person = {

     /**
     * This probably wants separating in future, as this method is render, bind and sync all in one
     * for a person record. Handles retrieving the record from the backend, hence async.
     */
    render: async function(p) {
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
        $("#content-person").html( h.join("\n") );
        // Display our person now it's rendered
        $(".container").hide();
        $("#content-person").show();
    },

    bind: () => {

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
                mobile_ui_person.render(p);
            }
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

    },

    sync: () => {
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
    }

};
