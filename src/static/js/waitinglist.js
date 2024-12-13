/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, microchip, tableform, validate */

$(function() {

    "use strict";

    const waitinglist = {

        current_person: null,

        render: function() {
            return [
                '<div id="emailform"></div>',
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "WAITINGLIST", controller.animal.ID),
                '</ul>',
                '</div>',
                '<div id="dialog-clone-confirm" style="display: none" title="' + html.title(_("Clone")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span> ' + _("Clone this waiting list record?") + '</p>',
                '</div>',
                edit_header.waitinglist_edit_header(controller.animal, "details", controller.tabcounts),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this waiting list entry") },
                    { id: "clone", text: _("Clone"), icon: "copy", tooltip: _("Clone this waiting list entry") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this waiting list entry") },
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this record") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Email this person") },
                    { id: "toanimal", text: _("Create Animal"), icon: "animal-add", tooltip: _("Create a new animal from this waiting list entry") }
                ]),
                '<div id="asm-details-accordion">',
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { type: "raw", label: _("Number"), markup: '<span class="asm-waitinglist-number">' + format.padleft(controller.animal.WLID, 6) + '</span>' },
                    { post_field: "dateputon", json_field: "DATEPUTONLIST", type: "date", label: _("Date put on") },
                    { post_field: "animalname", json_field: "ANIMALNAME", type: "text", label: _("Name") },
                    { post_field: "microchip", json_field: "MICROCHIPNUMBER", type: "text", label: _("Microchip"), maxlength: 15, 
                        xmarkup: ' <span id="microchipbrand"></span> <button id="button-microchipcheck">' + microchip.check_site_name() + '</button>' },
                    { post_field: "species", json_field: "SPECIESID", type: "select", label: _("Species"), 
                        options: { displayfield: "SPECIESNAME", rows: controller.species }},
                    { post_field: "breed", json_field: "BREEDID", type: "select", label: _("Breed"), 
                        options: html.list_to_options_breeds(controller.breeds),
                        xmarkup: '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">' + 
                            html.list_to_options_breeds(controller.breeds) + '</select>' },
                    { post_field: "sex", json_field: "SEX", type: "select", label: _("Sex"), 
                        options: { displayfield: "SEX", rows: controller.sexes }},
                    { post_field: "neutered", json_field: "NEUTERED", type: "check", label: _("Altered") },
                    { post_field: "size", json_field: "SIZE", type: "select", label: _("Size"), 
                        options: { displayfield: "SIZE", rows: controller.sizes }},
                    { post_field: "dateofbirth", json_field: "DATEOFBIRTH", type: "date", label: _("Date of Birth") },
                    { post_field: "description", json_field: "ANIMALDESCRIPTION", type: "textarea", label: _("Description"), rows: 3, 
                        callout: _("A description or other information about the animal") },
                    { post_field: "reasonforwantingtopart", json_field: "REASONFORWANTINGTOPART", type: "textarea", label: _("Entry reason"), rows: 3,
                        callout: _("The reason the owner wants to part with the animal") },
                    { type: "nextcol" },
                    { post_field: "canafforddonation", json_field: "CANAFFORDDONATION", type: "check", label: _("Can afford donation") },
                    { post_field: "urgency", json_field: "URGENCY", type: "select", label: _("Urgency"), 
                        options: { displayfield: "URGENCY", rows: controller.urgencies }},
                    { post_field: "comments", json_field: "COMMENTS", type: "textarea", label: _("Comments"), rows: 5, },
                    { post_field: "owner", json_field: "OWNERID", type: "person", label: _("Contact") },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 14) }
                ], { full_width: true }),
                '</div>', 
                '<h3><a href="#">' + _("Removal") + '</a></h3>',
                '<div>',
                tableform.fields_render([
                    { post_field: "dateoflastownercontact", json_field: "DATEOFLASTOWNERCONTACT", type: "date", label: _("Date of last owner contact") },
                    { post_field: "autoremovepolicy", json_field: "AUTOREMOVEPOLICY", type: "number", label: _("Automatically remove"),
                        callout: _("ASM will remove this animal from the waiting list after a set number of weeks since the last owner contact date.") + 
                            ' <br />' + _("Set this to 0 to never automatically remove."),
                        xmarkup: ' ' + _("weeks after last contact.") },
                    { post_field: "dateremoved", json_field: "DATEREMOVEDFROMLIST", type: "date", label: _("Date removed") },
                    { post_field: "waitinglistremoval", json_field: "WAITINGLISTREMOVALID", type: "select", label: _("Removal category"), 
                        options: { displayfield: "REMOVALNAME", rows: controller.waitinglistremovals }},
                    { post_field: "reasonforremoval", json_field: "REASONFORREMOVAL", type: "textarea", label: _("Removal reason"), rows: 5 },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 15) }
                ]),
                '</div>',
                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                additional.additional_fields(controller.additional),
                '</div>',
                html.audit_trail_accordion(controller),
                '</div> <!-- accordion -->',
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

            if (!common.has_permission("cwl")) { $("#button-save").hide(); }
            if (!common.has_permission("aa")) { $("#button-toanimal").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }
            if (!common.has_permission("dwl")) { $("#button-delete").hide(); }
        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // owner
            if (common.trim($("#owner").val()) == "0") {
                header.show_error(_("Waiting list entries must have a contact"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("owner");
                return false;
            }

            // date put on list
            if (common.trim($("#dateputon").val()) == "") {
                header.show_error(_("Date put on cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 3);
                validate.highlight("dateputon");
                return false;
            }

            // description
            if (common.trim($("#description").val()) == "") {
                header.show_error(_("Description cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("description");
                return false;
            }

            // any additional fields that are marked mandatory
            if (!additional.validate_mandatory()) {
                return false;
            }

            return true;
        },

        bind: function() {
            
            $(".asm-tabbar").asmtabs();
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            }); 

            // Setup the document button
            $("#button-document").asmmenu();

            validate.save = function(callback) {
                if (!waitinglist.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                let formdata = "mode=save" +
                    "&id=" + $("#waitinglistid").val() + 
                    "&recordversion=" + controller.animal.RECORDVERSION + 
                    "&" + $("input, select, textarea").toPOST();
                common.ajax_post("waitinglist", formdata)
                    .then(callback)
                    .fail(function() { 
                        validate.dirty(true); 
                    });
            };

            // When contact changes, keep track of the record
            $("#owner").personchooser().bind("personchooserchange", function(event, rec) {
                waitinglist.current_person = rec;
            });
            $("#owner").personchooser().bind("personchooserloaded", function(event, rec) {
                waitinglist.current_person = rec;
            });

            $('#species').change(function() {
                waitinglist.updatebreedselect();
            });

            // Handlers for when on-screen fields are edited
            $("#microchip").change(waitinglist.enable_widgets);

            // Email dialog for sending emails
            $("#emailform").emailform();

            // Toolbar buttons
            $("#button-save").button().click(function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload();
                });
            });

            $("#button-clone").button().click(async function() {
                await tableform.show_okcancel_dialog("#dialog-clone-confirm", _("Clone"));
                let formdata = "mode=clone&waitinglistid=" + $("#waitinglistid").val();
                header.show_loading(_("Cloning..."));
                let response = await common.ajax_post("waitinglist", formdata);
                header.hide_loading();
                common.route("waitinglist?id=" + response + "&cloned=true");
            });

            $("#button-email").button().click(function() {
                $("#emailform").emailform("show", {
                    post: "waitinglist",
                    formdata: "mode=email&wlid=" + $("#waitinglistid").val(),
                    name: waitinglist.current_person.OWNERFORENAMES + " " + waitinglist.current_person.OWNERSURNAME,
                    email: waitinglist.current_person.EMAILADDRESS,
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
                let formdata = "mode=toanimal&id=" + $("#waitinglistid").val();
                let result = await common.ajax_post("waitinglist", formdata);
                common.route("animal?id=" + result); 
            });

            $("#button-delete").button().click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove this waiting list entry, are you sure?"));
                let formdata = "mode=delete&id=" + $("#waitinglistid").val();
                await common.ajax_post("waitinglist", formdata);
                common.route("main");
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
            waitinglist.enable_widgets();

            // Filter the breed select to match the loaded species
            waitinglist.updatebreedselect();
            $("#breed").fromJSON(controller.animal);

            // Dirty handling
            validate.bind_dirty([ "waitinglist_" ]);
            validate.indicator([ "owner", "dateputon", "description" ]);

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#owner");
            common.widget_destroy("#emailform");
            common.widget_destroy("#dialog-clone-confirm");
            this.current_person = null;
        },

        name: "waitinglist",
        animation: "formtab",
        autofocus: "#species",
        title:  function() { 
            return common.substitute(_("Waiting list entry for {0} ({1})"), {
                0: controller.animal.OWNERNAME, 1: controller.animal.SPECIESNAME });
        },
        routes: {
            "waitinglist": function() { common.module_loadandstart("waitinglist", "waitinglist?id=" + this.qs.id); }
        }
    };

    common.module_register(waitinglist);

});

