/* global $, jQuery, _, common*/

$(function(){

    "use strict";

    const event = {

        render: function() {
            return [
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
                tableform.fields_render([
                    { post_field: "eventname", json_field: "EVENTNAME", type: "text", label: _("Event Name") },
                    { post_field: "startdate", json_field: "STARTDATETIME", type: "date", label: _("Start Date") },
                    { post_field: "enddate", json_field: "ENDDATETIME", type: "date", label: _("End Date") },
                    { post_field: "location", json_field: "EVENTOWNERID", label: _("Location"), type: "person", persontype: "organization" },
                    { post_field: "address", json_field: "EVENTADDRESS", label: _("Address"), type: "textarea", rows: 3, classes: "asm-textareafixed" },
                    { post_field: "town", json_field: "EVENTTOWN", label: _("City"), type: "text", maxlength: 100 },
                    { post_field: "county", json_field: "EVENTCOUNTY", label: _("State"), type: "text", maxlength: 100 },
                    { post_field: "postcode", json_field: "EVENTPOSTCODE", label: _("Zipcode"), type: "text", maxlength: 100 },
                    { post_field: "country", json_field: "EVENTCOUNTRY", label: _("Country"), type: "text", maxlength: 100 }, 
                    { type: "nextcol" },
                    { post_field: "description", json_field: "EVENTDESCRIPTION", label: _("Description"), type: "richtextarea", 
                        height: "200px", labelpos: "above" },
                    { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 21) },
                ], { full_width: true }),
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
            validate.indicator(["startdate", "enddate", "address" ]);

        },

        destroy: function() {
            common.widget_destroy("#description", "richtextarea");
            common.widget_destroy("#location", "personchooser");
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
