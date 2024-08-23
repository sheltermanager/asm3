/* global $, jQuery, _, common*/

$(function(){

    "use strict";

    const event ={


        render: function(){
            return [
                // console.log(controller),
                edit_header.event_edit_header(controller.event, "event", []),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this event") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this event") },
                ]),
                '<div id="asm-details-accordion">',
                this.render_details(),
                '</div>',
                '</div>'
            ].join("\n");
        },

        render_details: function(){
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<div class="row">',
                // left column
                '<div class="col-sm">',
                '<table>',
                '<tr>',
                '<td ><label for="eventname">' + _("Event Name") + '</label></td>',
                '<td><input id="eventname" data-post="eventname" type="text" data-json="EVENTNAME" class="asm-textbox"  /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="startdate">' + _("Start Date") + '</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><input id="startdate" data-post="startdate" data-json="STARTDATETIME" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="enddate">' + _("End Date") + '</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><input id="enddate" data-post="enddate" data-json="ENDDATETIME" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="location">' + _("Location") + '</label>',
                '</td>',
                '<td><input type="hidden" id="location" class="asm-personchooser" data-type="organization" data-post="event" data-json="EVENTOWNERID" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="address">' + _("Address") +'</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><textarea class="asm-textareafixed" id="address" data-post="address" data-json="EVENTADDRESS" rows="3"></textarea></td>',
                '</tr>',
                '<tr>',
                '<td><label for="town">' + _("City") + '</label></td>',
                '<td><input class="asm-textbox" maxlength="100" id="town" data-post="town" data-json="EVENTTOWN" type="text" /></td>',
                '</tr>',
                '<tr id="statecounty">',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td><input class="asm-textbox" maxlength="100" id="county" data-post="county" data-json="EVENTCOUNTY" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="postcode">' + _("Zipcode") + '</label></td>',
                '<td><input class="asm-textbox newform" id="postcode" data-post="postcode" data-json="EVENTPOSTCODE" type="text" /></td>',
                '</tr>',
                '<tr id="countryrow">',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input class="asm-textbox" id="country" data-post="country" data-json="EVENTCOUNTRY" type="text" /></td>',
                '</tr>',
                additional.additional_fields_linktype(controller.additional, 21),
                '</table>',
                '</div>', // col-sm
                // right column
                '<div class="col-sm">',
                '<p><label for="description">' + _("Description") + '</label></p>',
                '<div id="description" data-post="description" data-height="200px" data-margin-top="0px" data-json="EVENTDESCRIPTION" class="asm-richtextarea"></div>',
                '</div>', // col-sm
                '</div>', // row
                '</div>', // end accordion section
            ].join("\n");
        },

        bind: function(){

            // accordion
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            });

            validate.save = function(callback) {
                if (!event.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                let formdata = "mode=save" +
                    "&id=" + $("#eventid").val() +
                    "&ownerid=" + $("#location").personchooser().val() +
                    "&recordversion=" + controller.event.RECORDVERSION +
                    "&" + $("input, select, textarea, .asm-richtextarea").not(".chooser").toPOST();
                common.ajax_post("event", formdata)
                    .then(callback)
                    .fail(function() {
                        validate.dirty(true);
                    });
            };

            // Load the tab strip
            $(".asm-tabbar").asmtabs();

            $("#button-save").button().click(function(){
               header.show_loading(_("Saving..."));
               validate.save(function() {
                   common.route_reload();
               });
            });

            $("#button-delete").button().click(async function(){
                await tableform.delete_dialog(null, _("This will permanently remove this event, are you sure?"));
                let formdata = "mode=delete&eventid=" + $("#eventid").val();
                await common.ajax_post("event", formdata);
                common.route("main");
            });

            // If the bonded animals are cleared (or any animalchooser as part
            // of an additional field for that matter), dirty the form.
            $(".asm-animalchooser").animalchooser().bind("animalchoosercleared", function(event) {
                validate.dirty(true);
            });

            // Same goes for any of our person choosers
            $(".asm-personchooser").personchooser().bind("personchoosercleared", function(event) {
                validate.dirty(true);
            });

        },

        enable_widgets: function() {

            if (!common.has_permission("ce")) { $("#button-save").hide(); }
            if (!common.has_permission("de")) { $("#button-delete").hide(); }
            $("#countryrow").toggle( !config.bool("HideCountry") );

        },

        validation: function(){
            header.hide_error();
            validate.reset();
            if(common.trim($("#startdate").val()) == ""){
                header.show_error(_("Event must have a start date."));
                validate.highlight("startdate");
                validate.dirty(false);
                return false;
            }
            if (common.trim($("#enddate").val()) == ""){
                header.show_error(_("Event must have an end date."));
                validate.highlight("enddate");
                validate.dirty(false);
                return false;
            }
            if (common.trim($("#address").val()) == ""){
                header.show_error(_("Event must have an address."));
                validate.highlight("address");
                validate.dirty(false);
                return false;
            }
            // mandatory additional fields
            if (!additional.validate_mandatory()) { return false; }
            return true;
        },

        sync: function(){

            // Load the data into the controls for the screen
            $("input, select, textarea, .asm-richtextarea").fromJSON(controller.event);

            // Update on-screen fields from the data and display the screen
            event.enable_widgets();

            // Dirty handling
            validate.bind_dirty([ "event_" ]);
        },

        destroy: function() {
            common.widget_destroy("#description", "richtextarea");
        },

        name: "event",
        animation: "formtab",
        autofocus: "#eventtype",
        title: function() {
            var e = controller.event;
            var dates_range = "";
            if(format.date(e.STARTDATETIME) == format.date(e.ENDDATETIME))
                    dates_range = format.date(e.STARTDATETIME);
                else
                    dates_range = format.date(e.STARTDATETIME) + " - " + format.date(e.ENDDATETIME);
            return dates_range + " " + e.EVENTNAME + " " + [e.EVENTADDRESS, e.EVENTTOWN, e.EVENTCOUNTY, e.EVENTCOUNTRY].filter(Boolean).join(", ");
        },
        routes: {
            "event": function() { common.module_loadandstart("event", "event?id=" + this.qs.id); }
        }
    };

    common.module_register(event);

});
