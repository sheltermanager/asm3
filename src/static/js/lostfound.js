/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, microchip, tableform, validate */

$(function() {

    "use strict";

    const lostfound = {

        current_person: null,
        mode: "lost",

        render: function() {
            let mode = controller.name.indexOf("lost") != -1 ? "lost" : "found";
            this.mode = mode;
            return [
                '<div id="emailform"></div>',
                microchip.render_checkresults_dialog(),
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, ( mode == "lost" ? "LOSTANIMAL" : "FOUNDANIMAL" ), controller.animal.ID),
                '</ul>',
                '</div>',
                edit_header.lostfound_edit_header(mode, controller.animal, "details", controller.tabcounts),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this record") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this record") },
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this record") },
                    { id: "match", text: _("Match"), icon: "match", tooltip: _("Match against other lost/found animals") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Email this person") },
                    { id: "toanimal", text: _("Create Animal"), icon: "animal-add", hideif: function() { return mode != "found"; },
                        tooltip: _("Create a new animal from this found animal record") },
                    { id: "towaitinglist", text: _("Create Waiting List"), icon: "waitinglist", hideif: function() { return mode != "found"; },
                        tooltip: _("Create a new waiting list entry from this found animal record") }
                ]),
                '<div id="asm-details-accordion">',
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { type: "raw", label: _("Number"), markup: '<span class="asm-lostfound-number">' + format.padleft(controller.animal.ID, 6) + '</span>' },
                    { post_field: "datelost", json_field: "DATELOST", type: "date", label: _("Date Lost"), 
                        hideif: function() { return mode != "lost"; }},
                    { post_field: "datefound", json_field: "DATEFOUND", type: "date", label: _("Date Found"), 
                        hideif: function() { return mode != "found"; }},
                    { post_field: "datereported", json_field: "DATEREPORTED", type: "date", label: _("Date Reported") },
                    { post_field: "agegroup", json_field: "AGEGROUP", type: "select", label: _("Age Group"), 
                        options: '<option value="Unknown">' + _("(unknown)") + '</option>' + html.list_to_options(controller.agegroups) },
                    { post_field: "sex", json_field: "SEX", type: "select", label: _("Sex"), 
                        options: { displayfield: "SEX", rows: controller.sexes }},
                    { post_field: "species", json_field: "ANIMALTYPEID", type: "select", label: _("Species"), 
                        options: { displayfield: "SPECIESNAME", rows: controller.species }},
                    { post_field: "breed", json_field: "BREEDID", type: "select", label: _("Breed"), 
                        options: html.list_to_options_breeds(controller.breeds),
                        xmarkup: '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">' + 
                            html.list_to_options_breeds(controller.breeds) + '</select>' },
                    { post_field: "colour", json_field: "BASECOLOURID", type: "select", label: _("Color"), 
                        options: { displayfield: "BASECOLOUR", rows: controller.colours }},
                    { post_field: "markings", json_field: "DISTFEAT", type: "textarea", label: _("Features") },
                    { post_field: "arealost", json_field: "AREALOST", type: "textarea", label: _("Area Lost"), rows: 4, 
                        hideif: function() { return mode != "lost"; }},
                    { post_field: "areafound", json_field: "AREAFOUND", type: "textarea", label: _("Area Found"), rows: 4, 
                        hideif: function() { return mode != "found"; }},
                    { type: "nextcol" },
                    { post_field: "areapostcode", json_field: "AREAPOSTCODE", type: "text", label: _("Zipcode") },
                    { post_field: "datefound", json_field: "DATEFOUND", type: "date", label: _("Date Found"), 
                        hideif: function() { return mode != "lost"; }},
                    { post_field: "returntoownerdate", json_field: "RETURNTOOWNERDATE", type: "date", label: _("Returned"), 
                        hideif: function() { return mode != "found"; }},
                    { post_field: "microchip", json_field: "MICROCHIPNUMBER", type: "text", label: _("Microchip"), maxlength: 15, 
                        xmarkup:  '<span id="microchipbrand"></span> <button id="button-microchipcheck">' + microchip.check_site_name() + '</button>' },
                    { post_field: "comments", json_field: "COMMENTS", type: "textarea", label: _("Comments"), rows: 5 },
                    { post_field: "owner", json_field: "OWNERID", type: "person", label: _("Contact") },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 10), hideif: function() { return mode != "lost"; }},
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 12), hideif: function() { return mode != "found"; }}
                ], { full_width: true }),
                '</div>', // accordion section
                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                additional.additional_fields(controller.additional),
                '</div>',
                html.audit_trail_accordion(controller),
                '</div>', // accordion
                html.content_footer()
            ].join("\n");
        },

        enable_widgets: function() {

            // Hide additional accordion section if there aren't
            // any additional fields declared
            let ac = $("#asm-additional-accordion");
            let an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }

            // Show the microchip manufacturer
            microchip.manufacturer("#microchip", "#microchipbrand");

            // Show the microchip check button
            $("#button-microchipcheck").hide();
            if (microchip.is_check_available($("#microchip").val())) { $("#button-microchipcheck").show(); }

            if (!common.has_permission("aa")) { $("#button-toanimal").hide(); }
            if (!common.has_permission("awl")) { $("#button-towaitinglist").hide(); }
            if (!common.has_permission("mlaf")) { $("#button-match").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }
            if (lostfound.mode == "lost") {
                if (!common.has_permission("cla")) { $("#button-save").hide(); }
                if (!common.has_permission("dla")) { $("#button-delete").hide(); }
            }
            if (lostfound.mode == "found") {
                if (!common.has_permission("cfa")) { $("#button-save").hide(); }
                if (!common.has_permission("dfa")) { $("#button-delete").hide(); }
            } 
        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // owner
            if (common.trim($("#owner").val()) == "") {
                header.show_error(_("Lost and found entries must have a contact"));
                validate.highlight("owner");
                return false;
            }

            // date lost
            if (lostfound.mode == "lost" && common.trim($("#datelost").val()) == "") {
                header.show_error(_("Date lost cannot be blank"));
                validate.highlight("datelost");
                return false;
            }

            // date found
            if (lostfound.mode == "found" && common.trim($("#datefound").val()) == "") {
                header.show_error(_("Date found cannot be blank"));
                validate.highlight("datefound");
                return false;
            }

            // date reported
            if (common.trim($("#datereported").val()) == "") {
                header.show_error(_("Date reported cannot be blank"));
                validate.highlight("datereported");
                return false;
            }

            // any additional fields that are marked mandatory
            if (!additional.validate_mandatory()) {
                return false;
            }

            return true;
        },

        bind: function() {

            // Load the tab strip
            $(".asm-tabbar").asmtabs();

            // Setup the document button
            $("#button-document").asmmenu();

            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            });

            validate.save = function(callback) {
                if (!lostfound.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                var formdata = "mode=save" +
                    "&id=" + $("#lfid").val() + 
                    "&recordversion=" + controller.animal.RECORDVERSION + 
                    "&" + $("input, select, textarea").not(".chooser").toPOST();
                common.ajax_post(controller.name, formdata)
                    .then(callback)
                    .fail(function() { 
                        validate.dirty(true); 
                    });
            };

            // When contact changes, keep track of the record
            $("#owner").personchooser().bind("personchooserchange", function(event, rec) {
                lostfound.current_person = rec;
            });
            $("#owner").personchooser().bind("personchooserloaded", function(event, rec) {
                lostfound.current_person = rec;
            });

            // Handlers for when on-screen fields are edited
            $("#microchip").change(lostfound.enable_widgets);

            // Email dialog for sending emails
            $("#emailform").emailform();

            // Toolbar buttons
            $("#button-save").button().click(function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload();
                });
            });

            $("#button-match").button().click(function() {
                let qs = ( lostfound.mode == "lost" ? "lostanimalid=" : "foundanimalid=" ) + $("#lfid").val();
                common.route("lostfound_match?" + qs);
            });

            $("#button-email").button().click(function() {
                $("#emailform").emailform("show", {
                    post: controller.name,
                    formdata: "mode=email&lfid=" + $("#lfid").val() + "&lfmode=" + lostfound.mode,
                    name: lostfound.current_person.OWNERFORENAMES + " " + lostfound.current_person.OWNERSURNAME,
                    email: lostfound.current_person.EMAILADDRESS,
                    logtypes: controller.logtypes,
                    personid: controller.animal.OWNERID,
                    templates: controller.templatesemail
                });
            });

            $("#button-microchipcheck")
                .button({ icons: { primary: "ui-icon-search" }, text: false })
                .click(function() { microchip.check($("#microchip").val()); });

            $("#button-toanimal").button().click(async function() {
                $("#button-toanimal").button("disable");
                let formdata = "mode=toanimal&id=" + $("#lfid").val();
                let result = await common.ajax_post(controller.name, formdata);
                common.route("animal?id=" + result); 
            });

            $("#button-towaitinglist").button().click(async function() {
                $("#button-towaitinglist").button("disable");
                let formdata = "mode=towaitinglist&id=" + $("#lfid").val();
                let result = await common.ajax_post(controller.name, formdata);
                common.route("waitinglist?id=" + result); 
            });

            $("#button-delete").button().click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove this record, are you sure?"));
                let formdata = "mode=delete&id=" + $("#lfid").val();
                await common.ajax_post(controller.name, formdata);
                $("#dialog-delete").dialog("close"); 
                common.route("main"); 
            });

            $('#species').change(function() {
                lostfound.updatebreedselect();
            });

        },

        // Only show the breeds for the selected species
        updatebreedselect: function() {
            $('optgroup', $('#breed')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed'));

            $('#breed').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()){
                    $(this).remove();
                }
            });
        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.animal);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Update on-screen fields from the data and display the screen
            lostfound.enable_widgets();

            // Filter the breed select to match the loaded species
            lostfound.updatebreedselect();
            $("#breed").fromJSON(controller.animal);

            // Dirty handling
            validate.bind_dirty([ "lostanimal_", "foundanimal_" ]);
            if (this.mode == "lost") { validate.indicator([ "datelost", "datereported", "owner" ]); }
            if (this.mode == "found") { validate.indicator([ "datefound", "datereported", "owner" ]); }
        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#owner");
            common.widget_destroy("#emailform");
        },

        name: "lostfound",
        animation: "formtab",
        autofocus: "#datereported",
        title: function() {
            if (controller.name.indexOf("lost") != -1) {
                return common.substitute(_("Lost animal - {0} {1} [{2}]"), { 
                    0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME });
            }
            return common.substitute(_("Found animal - {0} {1} [{2}]"), { 
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME });
        },
        routes: {
            "foundanimal": function() { common.module_loadandstart("lostfound", "foundanimal?id=" + this.qs.id); },
            "lostanimal": function() { common.module_loadandstart("lostfound", "lostanimal?id=" + this.qs.id); }
        }
    };

    common.module_register(lostfound);

});

