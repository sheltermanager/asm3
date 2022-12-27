/* global $, jQuery, _, common*/

$(function(){

    "use strict";

    const event ={


        render: function(){
            return [

                console.log(controller),
                edit_header.event_edit_header(controller.event, "event", []),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this event") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this event") },
                ]),
                '<div id="asm-details-accordion">',
                this.render_details(),
//                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
//                '<div>',
//                additional.additional_fields(controller.additional),
//                '</div>',
                this.render_notes(),
                '<h3><a href="#"> dsad</a></h3>',
                '<div>dsads</div>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        render_details: function(){
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                // left column
                '<td width="35%" class="asm-nested-table-td">',
                '<table width="100%" class="additionaltarget" data="to16">',
                '<tr>',
                '<td>' + _("Number") + '</td>',
                '<td><span class="asm-waitinglist-number">',
//                format.padleft(controller.incident.ACID, 6),
                '</span></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n")
        },

        render_notes: function() {
            return [
                '<h3><a href="#">' + _("Notes") + '</a></h3>',
                '<div>',
                // outer table
                '<table width="100%">',
                '<tr>',
                '<td class="asm-nested-table-td">',
                // comments table
                '<table>',
                '<tr id="markingsrow">',
                '<td>',
                '<label for="markings">' + _("Markings") + '</label>',
                '</td>',
                '<td width="80%">',
                '<textarea class="asm-textarea" id="markings" data-json="MARKINGS" data-post="markings" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '<tr id="hiddencommentsrow">',
                '<td>',
                '<label for="hiddencomments">' + _("Hidden Comments") + '</label>',
                '<span id="callout-hiddencomments" class="asm-callout">' + _("Hidden comments are for staff information only and will never be used on any adoption websites") + '</span>',
                '</td>',
                '<td>',
                '<textarea class="asm-textarea" title="' + html.title(_("Hidden Comments")) + '" id="hiddencomments" data-json="HIDDENANIMALDETAILS" data-post="hiddencomments" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td>',
                '<label for="comments">' + _("Description") + '</label>',
                '<span id="callout-comments" class="asm-callout">' + _("The description is used for the animal's bio on adoption websites") + '</span>',
                '<br/><button id="button-commentstomedia">' + _('Copy description to the notes field of the web preferred media for this animal') + '</button>',
                '</td>',
                '<td>',
                '<textarea class="asm-textarea" title="' + html.title(_("Description")) + '" id="comments" data-json="ANIMALCOMMENTS" data-post="comments" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '<tr id="popupwarningrow">',
                '<td>',
                '<label for="popupwarning">' + _("Warning") + '</label>',
                '<span id="callout-popupwarning" class="asm-callout">' + _("Show a warning when viewing this animal") + '</span>',
                '</td>',
                '<td>',
                '<textarea class="asm-textarea" title="' + html.title(_("Warning")) + '" id="popupwarning" data-json="POPUPWARNING" data-post="popupwarning" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td class="asm-nested-table-td">',
                // good with table
                '<table class="additionaltarget" data="to3">',
                '<tr class="goodwith">',
                '<td>',
                '<label for="goodwithcats">' + _("Good with cats") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithcats" data-json="ISGOODWITHCATS" data-post="goodwithcats">',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="goodwith">',
                '<td>',
                '<label for="goodwithdogs">' + _("Good with dogs") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithdogs" data-json="ISGOODWITHDOGS" data-post="goodwithdogs">',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="goodwith">',
                '<td>',
                '<label for="goodwithkids">' + _("Good with children") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithkids" data-json="ISGOODWITHCHILDREN" data-post="goodwithkids">',
                html.list_to_options(controller.ynunk, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr class="goodwith">',
                '<td>',
                '<label for="housetrained">' + _("Housetrained") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="housetrained" data-json="ISHOUSETRAINED" data-post="housetrained">',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                // end good with
                '</table>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        validation: function(){
            return false;
        },

        bind: function(){

            // accordion
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            });

            validate.save = function(callback) {
                window.alert("hi");
                if (!event.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
            };

            // Load the tab strip
            $(".asm-tabbar").asmtabs();

            $("#button-save").button().click(function(){
               header.show_loading(_("Saving..."));
               validate.save(function() {
                   common.route_reload();
               });
            });

            $("#button-delete").button().click(function(){
            });
        },

        enable_widgets: function(){

        // SECURITY =============================================================
            if (!common.has_permission("ce")) { $("#button-save").hide(); }
            if (!common.has_permission("de")) { $("#button-delete").hide(); }

        },

        sync: function(){

        // Update on-screen fields from the data and display the screen
            event.enable_widgets()
        },

        name: "event",
        animation: "formtab",
        autofocus: "#eventtype",
        title: function() { return "controller.person.OWNERCODE" + ' - ' + "controller.person.OWNERNAME"; },
        routes: {
            "event": function() { common.module_loadandstart("event", "event?id=" + this.qs.id); }
        }
    }

    common.module_register(event);

});