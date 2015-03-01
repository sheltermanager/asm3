/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, additional, common, config, controller, dlgfx, edit_header, format, header, html, validate */

$(function() {

    var waitinglist = {

        current_person: null,

        render: function() {
            return [
                '<div id="emailform" />',
                '<div id="dialog-delete" style="display: none" title="' + _("Delete") + '">',
                '<p><span class="ui-icon ui-icon-alert" style="float: left; margin: 0 7px 20px 0;"></span>' + _("This will permanently remove this waiting list entry, are you sure?") + '</p>',
                '</div>',
                edit_header.waitinglist_edit_header(controller.animal, "details", controller.tabcounts),
                '<div class="asm-toolbar">',
                '<button id="button-save" title="' + html.title(_("Save this waiting list entry")) + '">' + html.icon("save"),
                ' ' + _("Save") + '</button>',
                '<button id="button-delete" title="' + html.title(_("Delete this waiting list entry")) + '">' + html.icon("delete"),
                ' ' + _("Delete") + '</button>',
                '<button id="button-email" title="' + html.title(_("Email this person")) + '">' + html.icon("email"),
                ' ' + _("Email") + '</button>',
                '<button id="button-toanimal" title="' + html.title(_("Create a new animal from this waiting list entry")) + '">' + html.icon("animal-add"),
                ' ' + _("Create Animal") + '</button>',
                '</div>',
                '<div id="asm-details-accordion">',
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                '<!-- left column -->',
                '<td>',
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
                '<!-- right column -->',
                '<td>',
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
                '<td><input type="text" id="autoremovepolicy" data-json="AUTOREMOVEPOLICY" data-post="autoremovepolicy" class="asm-textbox asm-numberbox" />',
                ' ' + _("weeks after last contact.") + '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("ASM will remove this animal from the waiting list after a set number of weeks since the last owner contact date.") + ' <br />',
                _("Set this to 0 to never automatically remove."),
                '</p>',
                '</div>',
                '</td>',
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
                '</div> <!-- accordion -->',
                html.content_footer()
            ].join("\n");
        },

        enable_widgets: function() {
            // Hide additional accordion section if there aren't
            // any additional fields declared
            var ac = $("#asm-additional-accordion");
            var an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }

            if (!common.has_permission("cwl")) { $("#button-save").hide(); }
            if (!common.has_permission("aa")) { $("#button-toanimal").hide(); }
            if (!common.has_permission("dwl")) { $("#button-delete").hide(); }
        },

        validation: function() {

            // Remove any previous errors
            header.hide_error();
            $("label").removeClass("ui-state-error-text");

            // owner
            if ($.trim($("#owner").val()) == "0") {
                header.show_error(_("Waiting list entries must have a contact"));
                $("label[for='owner']").addClass("ui-state-error-text");
                $("#asm-details-accordion").accordion("option", "active", 0);
                $("#owner").focus();
                return false;
            }

            // date put on list
            if ($.trim($("#dateputon").val()) == "") {
                header.show_error(_("Date put on cannot be blank"));
                $("label[for='dateputon']").addClass("ui-state-error-text");
                $("#asm-details-accordion").accordion("option", "active", 3);
                $("#dateputon").focus();
                return false;
            }

            // description
            if ($.trim($("#description").val()) == "") {
                header.show_error(_("Description cannot be blank"));
                $("label[for='description']").addClass("ui-state-error-text");
                $("#asm-details-accordion").accordion("option", "active", 0);
                $("#description").focus();
                return false;
            }

            // any additional fields that are marked mandatory
            var valid = true;
            $(".additional").each(function() {
                var t = $(this);
                if (t.attr("type") != "checkbox") {
                    var d = String(t.attr("data"));
                    if (d.indexOf("a.1") != -1) {
                        if ($.trim(t.val()) == "") {
                            header.show_error(_("{0} cannot be blank").replace("{0}", d.substring(4)));
                            $("#asm-details-accordion").accordion("option", "active", 2);
                            $("label[for='" + t.attr("id") + "']").addClass("ui-state-error-text");
                            t.focus();
                            valid = false;
                            return;
                        }
                    }
                }
            });

            return valid;
        },

        bind: function() {

            $(".asm-tabbar").asmtabs();
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            }); 

            validate.save = function(callback) {
                if (!waitinglist.validation()) { return; }
                validate.dirty(false);
                var formdata = "mode=save&id=" + $("#waitinglistid").val() + "&" + $("input, select, textarea").toPOST();
                common.ajax_post("waitinglist", formdata, callback, function() { validate.dirty(true); });
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
                    window.location="waitinglist?id=" + $("#waitinglistid").val();
                });
            });

            $("#button-email").button().click(function() {
                $("#emailform").emailform("show", {
                    post: controller.name,
                    formdata: "mode=email&wlid=" + $("#waitinglistid").val(),
                    name: waitinglist.current_person.OWNERFORENAMES + " " + waitinglist.current_person.OWNERSURNAME,
                    email: waitinglist.current_person.EMAILADDRESS,
                    logtypes: controller.logtypes
                });
            });

            $("#button-toanimal").button().click(function() {
                $("#button-toanimal").button("disable");
                var formdata = "mode=toanimal&id=" + $("#waitinglistid").val();
                common.ajax_post("waitinglist", formdata, function(result) { window.location = "animal?id=" + result; });
            });

            $("#button-delete").button().click(function() {
                var b = {}; 
                b[_("Delete")] = function() { 
                    var formdata = "mode=delete&id=" + $("#waitinglistid").val();
                    $("#dialog-delete").disable_dialog_buttons();
                    common.ajax_post("waitinglist", formdata, function() { window.location = "waitinglist_results"; });
                };
                b[_("Cancel")] = function() { $(this).dialog("close"); };
                $("#dialog-delete").dialog({
                     resizable: false,
                     modal: true,
                     dialogClass: "dialogshadow",
                     show: dlgfx.delete_show,
                     hide: dlgfx.delete_hide,
                     buttons: b
                });
            });

            // If any of our additional fields need moving to other tabs, 
            // let's take care of that. Additional fields are always in pairs of
            // <td> fields, with the label containing a toX class, where toX is
            // an entry in lksfieldlink. Some tables in the form have a .additionaltarget
            // class with a data element marked toX. We reparent our .toX elements
            // to those elements.
            $(".additionaltarget").each(function() {
                var target = $(this);
                var targetname = target.attr("data");
                $(".additionalmove ." + targetname).each(function() {
                    // $(this) is the td containing the label
                    var label = $(this);
                    var item = $(this).next();
                    // For some reason, jquery gets confused if we reparent the row, so
                    // we have to add a new row to the table and then move our cells in.
                    target.append("<tr></tr>");
                    target.find("tr:last").append(label);
                    target.find("tr:last").append(item);
                });
            });

        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.animal);

            // Update on-screen fields from the data and display the screen
            waitinglist.enable_widgets();

            // Dirty handling
            validate.bind_dirty();
            validate.dirty(false);
            validate.check_unsaved_links("waitinglist_");

        }

    };

    common.module(waitinglist, "waitinglist", "formtab");

});

function image_error(image) {
    image.style.display = "none";
}
