/*global $, jQuery, _, additional, asm, common, html */

$(function() {

    "use strict";

    const event_new = {

        render: function() {
            return [
                '<div id="dialog-similar" style="display: none" title="' + html.title(_("Similar Event")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This event is very similar to another event on file, carry on creating this record?"),
                '<br /><br />',
                '<span class="similar-event"></span>',
                '</p>',
                '</div>',
                html.content_header(_("Add a new event")),
                tableform.fields_render([
                    { post_field: "eventname", label: _("Event Name"), type: "text", maxlength: 50 },
                    { post_field: "description", label: _("Description"), type: "richtextarea", height: "100px", width: "195px" },
                    { post_field: "startdate", label: _("Start Date"), type: "date" },
                    { post_field: "enddate", label: _("End Date"), type: "date" },
                    { post_field: "location", label: _("Location"), type: "person", persontype: "organization" },
                    { post_field: "address", label: _("Address"), type: "textarea", rows: 3, classes: "asm-textareafixed" },
                    { post_field: "town", label: _("City"), type: "text", maxlength: 100 },
                    { post_field: "county", label: _("State"), type: "text", maxlength: 100 },
                    { post_field: "postcode", label: _("Zipcode"), type: "text", maxlength: 100 },
                    { post_field: "country", label: _("Country"), type: "text", maxlength: 100 },
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "addedit", icon: "event-add", text: _("Create and edit") },
                   { id: "add", icon: "event-add", text: _("Create") },
                   { id: "reset", icon: "delete", text: _("Reset") }
                ], { centered: true }),
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#button-reset").button().click(function() {
                event_new.reset();
            });
            $("#button-add").button().click(function() {
                event_new.create_and_edit = false;
                $("#asm-content button").button("disable");
                check_for_similar();
            });
            $("#button-addedit").button().click(function() {
                event_new.create_and_edit = true;
                $("#asm-content button").button("disable");
                check_for_similar();
            });
            //insert values to corresponding fields when a location is selected
            $("#location").personchooser().bind("personchooserchange", function(event, rec) {
                $("#address").val(html.decode(rec.OWNERADDRESS));
                $("#town").val(html.decode(rec.OWNERTOWN));
                $("#county").val(html.decode(rec.OWNERCOUNTY));
                $("#postcode").val(html.decode(rec.OWNERPOSTCODE));
                $("#country").val(html.decode(rec.OWNERCOUNTRY));
            });

            //insert value to the same date of the chosen Start date if End date field is empty
            $("#startdate").bind("change", function() {
                if($("#enddate").val() == "" && $("#startdate").val() != "")
                    $("#enddate").val($("#startdate").val());
            });

            const check_for_similar = async function() {
                if(!event_new.validation()){
                    $("#asm-content button").button("enable");
                    return;
                }
                // let formdata = "mode=similar&" + $("#emailaddress, #mobiletelephone, #surname, #forenames, #address").toPOST();
                add_event();
            };

            const add_event = async function() {
                if(!event_new.validation())
                {
                    $("#asm-content button").button("enable");
                    return;
                }
                header.show_loading(_("Creating..."));
                try{
                    let formdata = "ownerid=" + $("#location").personchooser().val() + "&" + $("input, textarea, select, #description, #location").toPOST();
                    let eventid = await common.ajax_post("event_new", formdata);
                    if(eventid && event_new.create_and_edit)
                        common.route("event?id=" + eventid);
                    else
                        header.show_info(_("Event successfully created"));
                }
                finally{
                    $("#asm-content button").button("enable");
                }
            };

            // CONFIG
            $("#countryrow").toggle( !config.bool("HideCountry") );
            $("#statecounty").toggle( !config.bool("HideTownCounty") );

        },

        sync: function() {
            validate.indicator(["startdate", "enddate", "address" ]);
        },

        validation: function() {
            header.hide_error();
            validate.reset();
            if(common.trim($("#startdate").val()) == ""){
                header.show_error(_("Event must have a start date."));
                validate.highlight("startdate");
                return false;
            }
            if (common.trim($("#enddate").val()) == ""){
                header.show_error(_("Event must have an end date."));
                validate.highlight("enddate");
                return false;
            }
            if (common.trim($("#address").val()) == ""){
                header.show_error(_("Event must have an address."));
                validate.highlight("address");
                return false;
            }
            // mandatory additional fields
            if (!additional.validate_mandatory()) { return false; }
            return true;
        },

        reset: function() {
            $(".asm-textbox").val("").change();
            $("#address").val("").change();
            $(".asm-personchooser").personchooser("clear");
            //init additional fields
            additional.reset_default(controller.additional);
        },

        destroy: function() {
            common.widget_destroy("#description", "richtextarea");
            common.widget_destroy("#location", "personchooser");
        },

        name: "event_new",
        animation: "newdata",
        autofocus: "#eventname",
        title: function() { return _("Add a new event"); },
        routes: {
            "event_new": function() { common.module_loadandstart("event_new", "event_new"); }
        }
    };
    common.module_register(event_new);
});
