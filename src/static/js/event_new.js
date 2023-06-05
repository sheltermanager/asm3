/*global $, jQuery, _, additional, asm, common, html */

$(function() {

    "use strict";

    const event_new = {

        render: function(){
            return [
                '<div id="dialog-similar" style="display: none" title="' + html.title(_("Similar Event")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This event is very similar to another event on file, carry on creating this record?"),
                '<br /><br />',
                '<span class="similar-event"></span>',
                '</p>',
                '</div>',
                html.content_header(_("Add a new event")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td><label for="eventname">' + _("Event Name") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="50" id="eventname" data="eventname" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="description">' + _("Description") + '</label></td>',
                '<td>',
                '<div id="description" data="description" data-height="100px" data-margin-top="0px" class="asm-richtextarea"></div>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="startdate">' + _("Start Date") + '</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><input id="startdate" data="startdate" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="enddate">' + _("End Date") + '</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><input id="enddate" data="enddate" class="asm-textbox asm-datebox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="location">' + _("Location") + '</label>',
                '</td>',
                '<td><input type="hidden" id="location" class="asm-personchooser" data-type="organization" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="address">' + _("Address") +'</label>',
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '<td><textarea class="asm-textareafixed newform" id="address" data="address" rows="3"></textarea></td>',
                '</tr>',
                '<tr>',
                '<td><label for="town">' + _("City") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="town" data="town" type="text" /></td>',
                '</tr>',
                '<tr id="statecounty">',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="county" data="county" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="postcode">' + _("Zipcode") + '</label></td>',
                '<td><input class="asm-textbox newform" id="postcode" data="postcode" type="text" /></td>',
                '</tr>',
                '<tr id="countryrow">',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input class="asm-textbox newform" id="country" data="country" type="text" /></td>',
                '</tr>',
                additional.additional_new_fields(controller.additional),
                '</table>',
                '<p></p>',
                '<div class="centered">',
                '<button id="addedit">' + _("Create and edit") + '</button>',
                '<button id="add">' + _("Create") + '</button>',
                '<button id="reset">' + _("Reset") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function(){
            $("#reset").button().click(function(){
                event_new.reset();
            });
            $("#add").button().click(function(){
                event_new.create_and_edit = false;
                $("#asm-content button").button("disable");
                check_for_similar();
            });
            $("#addedit").button().click(function(){
                event_new.create_and_edit = true;
                $("#asm-content button").button("disable");
                check_for_similar();
            });
            //insert values to corresponding fields when a location is selected
            $("#location").personchooser().bind("personchooserchange", function(event, rec){
                $("#address").val(html.decode(rec.OWNERADDRESS));
                $("#town").val(html.decode(rec.OWNERTOWN));
                $("#county").val(html.decode(rec.OWNERCOUNTY));
                $("#postcode").val(html.decode(rec.OWNERPOSTCODE));
                $("#country").val(html.decode(rec.OWNERCOUNTRY));
            });

            //insert value to the same date of the chosen Start date if End date field is empty
            $("#startdate").bind("change", function(){
                if($("#enddate").val() == "" && $("#startdate").val() != "")
                    $("#enddate").val($("#startdate").val());
            });

            const check_for_similar = async function(){
                if(!event_new.validation()){
                    $("#asm-content button").button("enable");
                    return;
                }
                // let formdata = "mode=similar&" + $("#emailaddress, #mobiletelephone, #surname, #forenames, #address").toPOST();
                add_event();
            };

            const add_event = async function(){
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

        validation: function(){
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

        reset: function(){
            $(".asm-textbox").val("").change();
            $("#address").val("").change();
            $(".asm-personchooser").personchooser("clear");

            //init additional fields
            additional.reset();

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
