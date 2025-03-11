/*global $, jQuery, controller */
/*global asm, common, config, format, html */
/*global _, mobile, mobile_ui_animal, mobile_ui_addanimal, mobile_ui_image, mobile_ui_person, mobile_ui_stock */
/*global mobile_ui_incident: true */

"use strict";

const mobile_ui_incident = {

    /**
     * This probably wants separating in future, as this method is render, bind and sync all in one
     * for an incident record. Handles retrieving the record from the backend, hence async.
     * ac: The incident record
     * selector: The container to put the rendered HTML in
     * backlink: Where to go when back is clicked (#content-[backlink])
     */
    render: async function(ac, selector, backlink) {

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
        let dispadd = ac.DISPATCHADDRESS;
        if (dispadd) {
            let encadd = encodeURIComponent(ac.DISPATCHADDRESS + ',' + ac.DISPATCHTOWN + ',' + ac.DISPATCHCOUNTY + ',' + ac.DISPATCHPOSTCODE);
            dispadd = '<button type="button" data-address="' + encadd + '" class="showmap btn btn-secondary"><i class="bi-map"></i></button> ' + ac.DISPATCHADDRESS;
        }
        let x= [];
        let followupdatetimes = [dt(ac.FOLLOWUPDATETIME), dt(ac.FOLLOWUPDATETIME2), dt(ac.FOLLOWUPDATETIME3)];
        $.each(followupdatetimes, function(followupcount, followupdatetime) {
            if (followupdatetime == " ") {
                let followupbutton = '<button type="button" data-id="' + ac.ID + '" class="followup btn btn-primary"><i class="bi-calendar-range"></i> ' + _("Follow Up");
                followupbutton += ' <div class="spinner-border spinner-border-sm" style="display: none"></div></button>';
                followupdatetimes[followupcount] = followupbutton;
                return false;
            }
        });
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
            aci("incidentimages", _("Images"), [
                mobile_ui_image.render_slider(o.media, "incidentimage"),
            ].join("\n")),
            aci("dispatch", _("Dispatch"), [
                i(_("Address"), dispadd),
                i(_("City"), ac.DISPATCHTOWN),
                i(_("State"), ac.DISPATCHCOUNTY),
                i(_("Zipcode"), ac.DISPATCHPOSTCODE),
                i(_("Dispatched ACO"), ac.DISPATCHEDACO),
                i(_("Dispatch Date/Time"), dispdt),
                i(_("Responded Date/Time"), respdt),
                i(_("Followup Date/Time"), followupdatetimes[0]),
                i(_("Followup Date/Time"), followupdatetimes[1]),
                i(_("Followup Date/Time"), followupdatetimes[2])
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

        $("#accordion-incident").on("click", ".media-thumb", function() {
            $(this).parent().find(".media-thumb").css("border-color", "#fff");
            $(this).css("border-color", "#000");
            $("#incidentimage-image").prop("src", "/image?db=" + asm.useraccount + "&mode=media&id=" + $(this).attr("data-imageid"));
            $("#incidentimage-anchor").prop("href", "/image?db=" + asm.useraccount + "&mode=media&id=" + $(this).attr("data-imageid"));
            $("#incidentimage-notes").html($(this).attr("data-description"));
        });

        // Listeners for adding media
        $("#incidentimage-button-gallery").click(function() {
            $("#incidentimage-input-gallery").trigger("click");
        });
        $("#incidentimage-button-camera").click(function() {
            $("#incidentimage-input-camera").trigger("click");
        });
        $("#incidentimage-input-gallery").change(function() {
            $.each($("#incidentimage-input-gallery")[0].files, function(imagecount, imagefile) {
                mobile_ui_incident.upload_incident_image(imagefile, ac.ID, "gallery");
            });
        });
        $("#incidentimage-input-camera").change(function() {
            mobile_ui_incident.upload_incident_image($("#incidentimage-input-camera")[0].files[0], ac.ID, "camera");
        });
        
    },

    /**
     * Renders a list of incidents into a list group/page
     * selector: The .list-group container to add the list to
     * backlink: Where to go when back is clicked (#content-[backlink])
     * incidents: The list of incidents
     */
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
                mobile_ui_incident.render(ac, selector + "-view", backlink);
            }
        });
    },

    upload_incident_image: function(file, incidentid, uploadtype) {
        let reader = new FileReader();
        reader.addEventListener("load", function() {
            let formdata = "incidentid=" + incidentid + "&type=" + uploadtype + "&filename=" + encodeURIComponent(file.name) + "&filedata=" + encodeURIComponent(reader.result);
            let targeturl =  "mobile_photo_upload";
            $("#incidentimage-button-" + uploadtype + " .media-button-icon").hide();
            $("#incidentimage-button-" + uploadtype + " .media-button-spinner").show();
            $.ajax({
                method: "POST",
                url: targeturl,
                data: formdata,
                dataType: "text",
                error: function(obj, error, errorthrown) {
                    mobile.show_error(error, errorthrown);
                    $(".media-button-icon").show();
                    $(".media-button-spinner").hide();
                },
                success: function(mid) {
                    let newthumbnail = mobile_ui_image.render_thumbnail(mid, "incidentimage");
                    $(newthumbnail).insertAfter($("#incidentimage-input-gallery"));
                    $(".media-button-icon").show();
                    $(".media-button-spinner").hide();
                }
            });
        }, false);
        reader.readAsDataURL(file);
    }

};
