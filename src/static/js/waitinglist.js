/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

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
                edit_header.waitinglist_edit_header(controller.animal, "details", controller.tabcounts),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this waiting list entry") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this waiting list entry") },
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this record") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Email this person") },
                    { id: "toanimal", text: _("Create Animal"), icon: "animal-add", tooltip: _("Create a new animal from this waiting list entry") }
                ]),
                '<div id="asm-details-accordion">',
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                // left column
                '<td class="asm-nested-table-td">',
                '<table width="100%">',
                '<tr>',
                '<td>' + _("Number") + '</td>',
                '<td><span class="asm-waitinglist-number">',
                format.padleft(controller.animal.WLID, 6),
                '</span></td>',
                '</tr>',
                '<tr>',
                '<td><label for="species">' + _("Species") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="species" data-json="SPECIESID" data-post="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="size">' + _("Size") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="size" data-json="SIZE" data-post="size" class="asm-selectbox">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="dateputon">' + _("Date put on") + '</label></td>',
                '<td><input type="text" id="dateputon" data-json="DATEPUTONLIST" data-post="dateputon" class="asm-textbox asm-datebox" title="' + html.title(_("The date this animal was put on the waiting list")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="description">' + _("Description") + '</label></td>',
                '<td><textarea id="description" data-json="ANIMALDESCRIPTION" data-post="description" rows="8" maxlength="255" class="asm-textarea" title="',
                html.title(_("A description or other information about the animal")) + '"></textarea></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="reasonforwantingtopart">' + _("Entry reason") + '</label></td>',
                '<td><textarea id="reasonforwaitingtopart" data-json="REASONFORWANTINGTOPART" data-post="reasonforwantingtopart" rows="5" class="asm-textarea" ',
                'title="' + _("The reason the owner wants to part with the animal") + '"></textarea></td>',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                // right column 
                '<td class="asm-nested-table-td">',
                '<table width="100%" class="additionaltarget" data="to14">',
                '<tr>',
                '<td><label for="canafforddonation">' + _("Can afford donation?") + '</label></td>',
                '<td><input type="checkbox" id="canafforddonation" data-json="CANAFFORDDONATION" data-post="canafforddonation" class="asm-checkbox" title="' + html.title(_("Will this owner give a donation?")) + '" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="urgency">' + _("Urgency") + '</label></td>',
                '<td><select id="urgency" data-json="URGENCY" data-post="urgency" class="asm-selectbox" title="' + html.title(_("How urgent is it that we take this animal?")) + '">',
                html.list_to_options(controller.urgencies, "ID", "URGENCY"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Comments") + '</label></td>',
                '<td><textarea id="comments" data-json="COMMENTS" data-post="comments" rows="5" class="asm-textarea"></textarea></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="owner">' + _("Contact") + '</label></td>',
                '<td>',
                '<input id="owner" data-json="OWNERID" data-post="owner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<h3><a href="#">' + _("Removal") + '</a></h3>',
                '<div>',
                '<table width="100%" class="additionaltarget" data="to15">',
                '<tr>',
                '<td><label for="dateoflastownercontact">' + _("Date of last owner contact") + '</label></td>',
                '<td><input type="text" id="dateoflastownercontact" data-json="DATEOFLASTOWNERCONTACT" data-post="dateoflastownercontact" class="asm-textbox asm-datebox" ',
                'title="' + html.title(_("The date the owner last contacted the shelter")) + '" /> </td>',
                '</tr>',
                '<tr>',
                '<td><label for="autoremovepolicy">' + _("Automatically remove") + '</label>',
                '<span id="callout-hiddencomments" class="asm-callout">' +
                _("ASM will remove this animal from the waiting list after a set number of weeks since the last owner contact date.") + ' <br />' +
                _("Set this to 0 to never automatically remove.") + '</span>',
                '</td>',
                '<td><input type="text" id="autoremovepolicy" data-json="AUTOREMOVEPOLICY" data-post="autoremovepolicy" class="asm-textbox asm-numberbox" />',
                ' ' + _("weeks after last contact.") + '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dateremoved">' + _("Date removed") + '</label></td>',
                '<td><input type="text" id="dateremoved" data-json="DATEREMOVEDFROMLIST" data-post="dateremoved" class="asm-textbox asm-datebox" ',
                'title="' + html.title(_("The date this animal was removed from the waiting list")) + '" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="reasonforremoval">' + _("Removal reason") + '</label></td>',
                '<td><textarea id="reasonforremoval" data-json="REASONFORREMOVAL" data-post="reasonforremoval" rows="5" class="asm-textarea" ',
                'title="' + html.title(_("The reason this animal was removed from the waiting list")) + '"></textarea></td>',
                '</tr>',
                '</table>',
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

            // Email dialog for sending emails
            $("#emailform").emailform();

            // Toolbar buttons
            $("#button-save").button().click(function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload();
                });
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

            additional.relocate_fields();

        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.animal);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Update on-screen fields from the data and display the screen
            waitinglist.enable_widgets();

            // Dirty handling
            validate.bind_dirty([ "waitinglist_" ]);
            validate.indicator([ "owner", "dateputon", "description" ]);

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#owner");
            common.widget_destroy("#emailform");
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

