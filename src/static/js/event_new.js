

$(function() {

    "use strict";

    const event_new = {

        render: function(){
            return [
                '<div id="dialog-similar" style="display: none" title="' + html.title(_("Similar Person")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This person is very similar to another person on file, carry on creating this record?"),
                '<br /><br />',
                '<span class="similar-person"></span>',
                '</p>',
                '</div>',
                html.content_header(_("Add a new event")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td><label for="eventname">' + _("Event Name") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="50" id="eventname" data="eventname" type="text" /></td>',
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
                '<span class="asm-has-validation">*</span>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="address">' + _("Address") +'</label></td>',
                '<td><textarea class="asm-textareafixed newform" id="address" data="address" rows="3"></textarea></td>',
                '</tr>',
                '<tr>',
                '<td><label for="town">' + _("City") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="town" data="town" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="county">' + _("State") + '</label></td>',
                '<td><input class="asm-textbox newform" maxlength="100" id="town" data="town" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for=postcode>' + _("Zipcode") + '</label></td>',
                '<td><input class="asm-textbox newform" id="postcode" data="postcode" type="text" /></td>',
                '</tr>',

                

                html.content_footer()
                ].join("\n");
            },

            name: "event_new",
            animation: "newdata",
            autofocus: "#ownertype",
            title: function() { return _("Add a new event"); },
            routes: {
                "event_new": function() { common.module_loadandstart("event_new", "event_new"); }
            }
        };
        common.module_register(event_new);
    });
