/*global $, jQuery, controller, alert */
/*global asm, common, config, format, html */
/*global _, mobile, mobile_ui_addanimal, mobile_ui_incident, mobile_ui_image, mobile_ui_person, mobile_ui_stock */
/*global mobile_ui_animal: true */

"use strict";

const mobile_ui_animal = {

    /**
     * This probably wants separating in future, as this method is render, bind and sync all in one
     * for an animal record. Handles retrieving the record from the backend, hence async.
     */
    render: async function(a) {
        // Returns the HTML for rendering an animal record
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
                i(_("Location"), mobile_ui_animal.display_location(a)),
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
                i(_("Microchipped"), format.date(a.IDENTICHIPDATE) + " " + (a.IDENTICHIPPED==1 ? a.IDENTICHIPNUMBER : ""), "DontShowMicrochip"),
                i(_("Tattoo"), format.date(a.TATTOODATE) + " " + (a.TATTOO==1 ? a.TATTOONUMBER : ""), "DontShowTattoo"),
                i(_("Neutered"), a.NEUTEREDNAME + " " + format.date(a.NEUTEREDDATE), "DontShowNeutered"),
                i(_("Declawed"), a.DECLAWEDNAME, "DontShowDeclawed"),
                i(_("Heartworm Tested"), format.date(a.HEARTWORMTESTDATE) + " " + (a.HEARTWORMTESTED==1 ? a.HEARTWORMTESTRESULTNAME : ""), "DontShowHeartworm"),
                i(_("FIV/L Tested"), format.date(a.COMBITESTDATE) + " " + (a.COMBITESTED==1 ? a.COMBITESTRESULTNAME + " " + a.FLVRESULTNAME : ""), "DontShowCombi"),
                i(_("Health Problems"), a.HEALTHPROBLEMS),
                i(_("Rabies Tag"), a.RABIESTAG),
                i(_("Special Needs"), a.HASSPECIALNEEDSNAME),
                i(_("Current Vet"), n(a.CURRENTVETNAME) + " " + n(a.CURRENTVETWORKTELEPHONE))
            ].join("\n")),

            aci("animalimages", _("Images"), [
                mobile_ui_image.render_slider(o.media, "animalimage"),
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
        $("#content-animal").html( h.join("\n") );

        // Display our animal now it's rendered
        $(".container").hide();
        $("#content-animal").show();

        // Show images based on clicked thumbnail
        $("#content-animal").on("click", ".media-thumb", function() {
            $(this).parent().find(".media-thumb").css("border-color", "#fff");
            $(this).css("border-color", "#000");
            $("#animalimage-image").prop("src", "/image?db=" + asm.useraccount + "&mode=media&id=" + $(this).attr("data-imageid"));
            $("#animalimage-anchor").prop("href", "/image?db=" + asm.useraccount + "&mode=media&id=" + $(this).attr("data-imageid"));
            $("#animalimage-notes").html($(this).attr("data-description"));
        });

        // Add listener for adding media
        $("#animalimage-button-gallery").click(function() {
            $("#animalimage-input-gallery").trigger("click");
        });
        $("#animalimage-button-camera").click(function() {
            $("#animalimage-input-camera").trigger("click");
        });
        $("#animalimage-input-gallery").change(function() {
            $.each($("#animalimage-input-gallery")[0].files, function(imagecount, imagefile) {
                mobile_ui_animal.upload_animal_image(imagefile, a.ID, "gallery");
            });
        });
        $("#animalimage-input-camera").change(function() {
            mobile_ui_animal.upload_animal_image($("#animalimage-input-camera")[0].files[0], a.ID, "camera");
        });
        // Handle the uploading of a photo when one is chosen
        $("#content-animal .uploadphoto").click(function() { $("#content-animal .uploadphotofile").click(); });
        $("#content-animal .uploadphotofile").change(function() { alert($("#content-animal .uploadphotofile").val()); });
    },

    render_shelteranimalslist: function() {
        // Load shelter animals list
        $("#content-shelteranimals .list-group").empty();
        $.each(controller.animals, function(i, v) {
            let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.CODE + '</h5>' +
                '<small>(' + v.SEXNAME + ' ' + v.BREEDNAME + ' ' + v.SPECIESNAME + ')<br/>' + v.IDENTICHIPNUMBER + ' ' + mobile_ui_animal.display_location(v) + '</small>' +
                '</a>';
            $("#content-shelteranimals .list-group").append(h);
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

    upload_animal_image: function(file, animalid, uploadtype) {
        let reader = new FileReader();
        reader.addEventListener("load", function() {
            let formdata = "animalid=" + animalid + "&type=" + uploadtype + "&filename=" + encodeURIComponent(file.name) + "&filedata=" + encodeURIComponent(reader.result);
            let targeturl =  "mobile_photo_upload";
            $("#animalimage-button-" + uploadtype + " .media-button-icon").hide();
            $("#animalimage-button-" + uploadtype + " .media-button-spinner").show();
            $.ajax({
                method: "POST",
                url: targeturl,
                data: formdata,
                dataType: "text",
                mimeType: "textPlain",
                error: function(obj, error, errorthrown) {
                    mobile.show_error(error, errorthrown);
                    $(".media-button-icon").show();
                    $(".media-button-spinner").hide();
                },
                success: function(mid) {
                    let newthumbnail = mobile_ui_image.render_thumbnail(mid, "animalimage");
                    $(newthumbnail).insertAfter($("#animalimage-input-gallery"));
                    $(".media-button-icon").show();
                    $(".media-button-spinner").hide();
                }
            });
        }, false);
        reader.readAsDataURL(file);
    },

    bind: function() {

        // Handle a change of internal location on daily observations
        $("#dailyobslocation").change(function() {
            $("#content-dailyobs .list-group").empty();
            controller.animals.sort(common.sort_single("SHELTERLOCATIONUNIT"));
            $.each(controller.animals, function(i, v) {
                if (v.SHELTERLOCATION == $("#dailyobslocation").val()) {
                    let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                        '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                        '<h5 class="mb-1"><input type=checkbox class="dailyobsselector">&nbsp;' + v.ANIMALNAME + ' - ' + v.CODE + ' - ' + v.SHELTERLOCATIONUNIT + '</h5>';
                        let colnames = [], colwidgets = [];
                        for (let i = 0; i < 50; i++) {
                            let name = config.str("Behave" + i + "Name"), value = config.str("Behave" + i + "Values");
                            if (name) { 
                                colnames.push(name);
                                if (value) {
                                    colwidgets.push('<select class="asm-selectbox asm-halfselectbox widget" data-name="' + html.title(name) + '" disabled>' +
                                        '<option value="">' + name + '</option>' + html.list_to_options(value.split("|")) + '</select>');
                                }
                                else {
                                    colwidgets.push('<input type="text" class="asm-textbox widget" data-name="' + html.title(name) + '" placeholder="' + name + '"  disabled />');
                                }
                            }
                        }
                        $.each(colnames, function(i, c) {
                            h += colwidgets[i];
                        });
                        '</a>';
                    $("#content-dailyobs .list-group").append(h);
                }
            });
        });

        // Handle clicking on the clear daily obs button
        $("#btn-clear-dailyobs").click(function() {
            $("#content-dailyobs .list-group .widget").val('');
            $("#content-dailyobs .list-group .widget").prop('disabled', true);
            $("#content-dailyobs .list-group .dailyobsselector").prop('checked', false);
        });

        $("#content-dailyobs").on('click', '.dailyobsselector', function() {
            console.log("Clicked!");
            if ($(this).closest('.list-group-item').find('.widget').first().prop('disabled')) {
                $(this).closest('.list-group-item').find('.widget').prop('disabled', false);
            } else {
                $(this).closest('.list-group-item').find('.widget').prop('disabled', true);
            }
        });

        $("#btn-commit-dailyobs").click(async function() {
            // Send the logs to the backend in the format:
            //    ANIMALID==FIELD1=VALUE1, FIELD2=VALUE2^^ANIMALID==FIELD1=VALUE1,
            //    52==Wet food=Mostly, Pen state=Dirty
            // means the backend can split by ^^ to get animals, then by == to get 
            // animalid and value string for the log.
            let formdata = { "mode": "save", "logtype": config.str("BehaveLogType") }, logs = [];
            $("#content-dailyobs .list-group .list-group-item").each(function() {
                if (! $(this).find(".dailyobsselector").is(":checked")) { return; } // skip unselected rows
                let animalid = $(this).attr("data-id"), avs = [];
                // Build a packed set of values for this animal
                $(this).find(".widget").each(function() {
                    if (config.bool("SuppressBlankObservations") && !$(this).val()) { return; }
                    avs.push( $(this).attr("data-name") + "=" + $(this).val() );
                });
                logs.push( animalid + "==" + avs.join(", ") );
            });
            formdata.logs = logs.join("^^");
            if (formdata.logs == "") { return; }
            //header.show_loading(_("Saving..."));
            let response = await common.ajax_post("animal_observations", formdata);
            //header.hide_loading();
            //header.show_info(_("{0} observation logs successfully written.").replace("{0}", response));
            // Unselect the previously selected values
            $("#content-dailyobs .list-group .widget").val('');
            $("#content-dailyobs .list-group .widget").prop('disabled', true);
            $("#content-dailyobs .list-group .dailyobsselector").prop('checked', false);
        });

        // Handle clicking on check microchip button
        $("#btn-check-microchip").click(function() {
            if ($("#microchipnumbersearch").val() == '') {
                mobile.show_error(_("Error"), _("A microchip number must be supplied"));
            } else {
                let spinner = $(this).find(".spinner-border");
                spinner.show();
                // Retrieve results
                let formdata = {
                    "mode": "checkmicrochip",
                    "microchipnumber": $("#microchipnumbersearch").val()
                };
                mobile.ajax_post(formdata, function(response) {
                    spinner.hide();
                    controller.microchipresults = jQuery.parseJSON(response);
                    // Display person list
                    $("#content-microchipresults .list-group").empty();
                    $.each(controller.microchipresults, function(i, v) {
                        let a = '"' + v.ANIMALNAME + '": ' + common.substitute(_("{0} {1} aged {2}"), { "0": v.SEX, "1": v.SPECIESNAME, "2": v.ANIMALAGE }) + '<br>';
                        if (!v.ANIMALNAME) { a = ""; }
                        let h = '<div data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                            '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                            '<h5 class="mb-1">' + v.SHELTERCODE + ' ' + v.ANIMALNAME + ' - ' + v.ANIMALAGE + '</h5>';
                        if (v.CURRENTOWNERID) {
                            h += '<small>' + _("Current Owner") + ': ' + 
                                v.CURRENTOWNERNAME + '<br>' + v.CURRENTOWNERADDRESS + ', ' + v.CURRENTOWNERTOWN + ' ' + v.CURRENTOWNERCOUNTY + ' ' + v.CURRENTOWNERPOSTCODE;
                            $.each([v.CURRENTOWNERHOMETELEPHONE, v.CURRENTOWNERWORKTELEPHONE, v.CURRENTOWNERMOBILETELEPHONE], function(i, v) {
                                if (v) {
                                    h += '<br><a href=tel:' + v.replace(/ /g, '') + '>' + v + '</a>';
                                }
                            });
                            if (v.CURRENTOWNEREMAILADDRESS) {
                                h += '<br><a href=mailto:' + v.CURRENTOWNEREMAILADDRESS + '>' + v.CURRENTOWNEREMAILADDRESS + '</a>';
                            }
                            h += '</small>';
                            
                        } else {
                            h += '<small>' + _("No current owner found") + '</small>';
                        }
                        h += '</div>';
                        $("#content-microchipresults .list-group").append(h);
                    });
                    if (controller.microchipresults.length == 0) {
                        let h = '<p>' + _("No results found") + '</p>';
                        $("#content-microchipresults .list-group").append(h);
                    }
                    $(".container").hide();
                    $("#content-microchipresults").show();
                });
            }
        });

        // When a shelter animal link is clicked, display the record
        $("#content-shelteranimals").on("click", "a", function() {
            let animalid = format.to_int($(this).attr("data-id")), a = null;
            $.each(controller.animals, function(i, v) {
                if (v.ID == animalid) { a = v; return false; }
            });
            if (a) { 
                mobile_ui_animal.render(a);
            }
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
    },

    sync: function() {

        // Load list of animals to medicate
        $("#content-medicate .list-group").empty();
        $.each(controller.medicals, function(i, v) {
            let h = '<a href="#" data-id="' + v.TREATMENTID + '" class="list-group-item list-group-item-action">' +
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                '<small>(' + v.TREATMENTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile_ui_animal.display_location(v) + '</small>' +
                '</a>';
            $("#content-medicate .list-group").append(h);
        });

        // Load list of animals to test
        $("#content-test .list-group").empty();
        $.each(controller.tests, function(i, v) {
            let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                '<small>(' + v.TESTNAME + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile_ui_animal.display_location(v) + '</small>' +
                '</a>';
            $("#content-test .list-group").append(h);
        });

        // Load list of animals to vaccinate
        $("#content-vaccinate .list-group").empty();
        $.each(controller.vaccinations, function(i, v) {
            let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                '<img style="float: right" height="75px" src="' + html.thumbnail_src(v, "animalthumb") + '">' + 
                '<h5 class="mb-1">' + v.ANIMALNAME + ' - ' + v.SHELTERCODE + '</h5>' +
                '<small>(' + v.VACCINATIONTYPE + ', ' + format.date(v.DATEREQUIRED) + ') ' + mobile_ui_animal.display_location(v) + '</small>' +
                '</a>';
            $("#content-vaccinate .list-group").append(h);
        });

        // Load list of animals for daily obs
        $("#dailyobslocation").change();

    }

};


