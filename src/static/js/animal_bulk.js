/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {
    
    "use strict";

    const animal_bulk = {

        render: function() {
            let choosetypes = [];
            $.each(controller.movementtypes, function(i, v) {
                if (v.ID == 8 && !config.bool("DisableRetailer")) {
                    choosetypes.push(v);
                }
                else if (v.ID == 0) {
                    v.MOVEMENTTYPE = _("Reservation");
                    choosetypes.push(v);
                }
                else if (v.ID !=8 && v.ID != 9 && v.ID != 10 && v.ID != 11 && v.ID != 12) {
                    choosetypes.push(v);
                }
            });
            return [
                html.content_header(_("Bulk change animals")),
                '<table width="100%" class="asm-table-layout" style="padding-bottom: 5px;">',
                '<tr>',
                '<td class="asm-nested-table-td">',
                
                // left table
                '<table width="60%" class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animals">' + _("Animals") + '</label>',
                '</td>',
                '<td>',
                '<input id="animals" data="animals" type="hidden" class="asm-animalchoosermulti" value=\'\' />',
                '</td>',
                '</tr>',

                '<tr id="litteridrow">',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label></td>',
                '<td><input type="text" id="litterid" data-post="litterid" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="animaltype">' + _("Type") + '</label></td>',
                '<td><select id="animaltype" data-post="animaltype" class="asm-selectbox">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select></td>',
                '</tr>',
                '<tr id="locationrow">',
                '<td><label for="location">' + _("Location") + '</label></td>',
                '<td>',
                '<select id="location" data-post="location" class="asm-selectbox" >',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="unitrow">',
                '<td><label for="unit">' + _("Unit") + '</label></td>',
                '<td>',
                '<select id="unit" data-post="unit" class="asm-selectbox">',
                '</select></td>',
                '</tr>',
                '<tr id="entryreasonrow">',
                '<td><label for="entryreason">' + _("Entry Category") + '</label></td>',
                '<td>',
                '<select id="entryreason" data-post="entryreason" class="asm-selectbox" title="' + html.title(_("The entry reason for this animal")) + '">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.entryreasons, "ID", "REASONNAME"),
                '</select></td>',
                '</tr>',

                '<tr id="holdrow">',
                '<td>',
                '<label for="holduntil">' + _("Hold until") + '</label>',
                '</td>',
                '<td>',
                '<input id="holduntil" data-post="holduntil" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                
                '<tr id="feerow">',
                '<td><label for="fee">' + _("Adoption Fee") + '</label></td>',
                '<td><input id="fee" data-post="fee" class="asm-currencybox asm-textbox" /></td>',
                '</tr>',

                '<tr id="boardingcostrow">',
                '<td><label for="boardingcost">' + _("Daily Boarding Cost") + '</label></td>',
                '<td><input id="boardingcost" data-post="boardingcost" class="asm-currencybox asm-textbox" /></td>',
                '</tr>',

                '<tr id="addflagrow">',
                '<td><label for="addflag">' + _("Add Flag") + '</label></td>',
                '<td>',
                '<select id="addflag" data-post="addflag" class="asm-selectbox">',
                '<option value=""></option>',
                html.list_to_options(controller.flags, "FLAG", "FLAG"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr id="removeflagrow">',
                '<td><label for="removeflag">' + _("Remove Flag") + '</label></td>',
                '<td>',
                '<select id="removeflag" data-post="removeflag" class="asm-selectbox">',
                '<option value=""></option>',
                html.list_to_options(controller.flags, "FLAG", "FLAG"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td><label for="notforadoption">' + _("Not For Adoption") + '</label></td>',
                '<td><select id="notforadoption" data-post="notforadoption" class="asm-selectbox">',
                '<option value="-1">' + _("(no change)") + '</option>',
                '<option value="0">' + _("Adoptable") + '</option>',
                '<option value="1">' + _("Not For Adoption") + '</option>',
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td><label for="notforregistration">' + _("Do Not Register Microchip") + '</label></td>',
                '<td><select id="notforregistration" data-post="notforregistration" class="asm-selectbox">',
                '<option value="-1">' + _("(no change)") + '</option>',
                '<option value="0">' + _("Register Microchip") + '</option>',
                '<option value="1">' + _("Do Not Register Microchip") + '</option>',
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="goodwithcats">' + _("Good with cats") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithcats" data-post="goodwithcats">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="goodwithdogs">' + _("Good with dogs") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithdogs" data-post="goodwithdogs">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="goodwithkids">' + _("Good with kids") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithkids" data-post="goodwithkids">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynunk, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="housetrained">' + _("Housetrained") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="housetrained" data-post="housetrained">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',

                // end left table
                '</td>',
                '<td class="asm-nested-table-td">',

                // right table
                '<table>',

                '<tr id="neuteredrow">',
                '<td>',
                '<label for="neutereddate">' + _("Altered") + '</label>',
                '</td>',
                '<td>',
                '<input id="neutereddate" data-post="neutereddate" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',

                '<tr id="neuteringvetrow">',
                '<td class="bottomborder">',
                '<label for="neuteringvet">' + _("By") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<input id="neuteringvet" data-post="neuteringvet" data-mode="brief" data-filter="vet" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',

                '<tr id="coordinatorrow">',
                '<td>',
                '<label for="coordinator">' + _("Adoption Coordinator") + '</label>',
                '</td>',
                '<td>',
                '<input id="coordinator" data-post="adoptioncoordinator" type="hidden" data-filter="coordinator" class="asm-personchooser" />',
                '</td>',
                '</tr>',

                '<tr id="currentvetrow">',
                '<td>',
                '<label for="currentvet">' + _("Current Vet") + '</label>',
                '</td>',
                '<td>',
                '<input id="currentvet" data-post="currentvet" type="hidden" data-filter="vet" class="asm-personchooser" />',
                '</td>',
                '</tr>',

                '<tr id="ownersvetrow">',
                '<td class="bottomborder">',
                '<label for="ownersvet">' + _("Owners Vet") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<input id="ownersvet" data-post="ownersvet" type="hidden" data-filter="vet" class="asm-personchooser"  />',
                '</td>',
                '</tr>',

                '<tr id="diaryrow">',
                '<td><label for="diaryfor">' + _("Add Diary") + '</label></td>',
                '<td>',
                '<select id="diaryfor" data-post="diaryfor" class="asm-halfselectbox">',
                '<option value="-1"></option>',
                html.list_to_options(controller.forlist, "USERNAME", "USERNAME"),
                '</select> ',
                _("on"),
                ' <input id="diarydate" data-post="diarydate" type="text" class="asm-datebox asm-halftextbox" />',
                ' <input id="diarytime" data-post="diarytime" type="text" class="asm-timebox asm-halftextbox" />',
                '</td>',
                '</tr>',

                '<tr id="diarysubjectrow">',
                '<td><label for="diarysubject">' + _("Subject") + '</label></td><td>',
                '<input id="diarysubject" data-post="diarysubject" class="asm-textbox asm-doubletextbox" />',
                '</td>',
                '</tr>',

                '<tr id="diarynotesrow">',
                '<td colspan="2" class="bottomborder">',
                '<textarea id="diarynotes" data-post="diarynotes" rows=3 class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',

                '<tr id="logrow">',
                '<td><label for="logtype">' + _("Add Log") + '</label></td>',
                '<td>',
                '<select id="logtype" data-post="logtype" class="asm-halfselectbox">',
                '<option value="-1"></option>',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select> ',
                _("on"),
                ' <input id="logdate" data-post="logdate" type="text" class="asm-datebox asm-halftextbox" />',
                '</td>',
                '</tr>',

                '<tr id="lognotesrow">',
                '<td colspan="2" class="bottomborder">',
                '<textarea id="lognotes" data-post="lognotes" rows=3 class="asm-textarea"></textarea>',
                '</td>',
                '</tr>',

                '<tr id="moverow">',
                '<td><label for="movementtype">' + _("Add Movement") + '</label></td>',
                '<td>',
                '<select id="movementtype" data-post="movementtype" class="asm-halfselectbox">',
                '<option value="-1"></option>',
                html.list_to_options(choosetypes, "ID", "MOVEMENTTYPE"),
                '</select> ',
                _("on"),
                ' <input id="movementdate" data-post="movementdate" type="text" class="asm-datebox asm-halftextbox" />',
                '</td>',
                '</tr>',

                '<tr id="movetorow">',
                '<td class="bottomborder">',
                '<label for="moveto">' + _("to") + '</label>',
                '</td>',
                '<td class="bottomborder">',
                '<input id="moveto" data-post="moveto" type="hidden" data-filter="all" class="asm-personchooser" />',
                '</td>',
                '</tr>',


                // end right table
                '</table>',

                // end outer table
                '</td>',
                '</tr>',
                '</table>',

                '<div class="centered">',
                '<button id="button-update">' + html.icon("animal") + ' ' + _("Update") + '</button> ',
                '<button id="button-delete">' + html.icon("delete") + ' ' + _("Delete") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            // Litter autocomplete
            $("#litterid").autocomplete({source: html.decode(controller.autolitters)});

            validate.indicator([ "animals" ]);

            $("#button-update").button().click(async function() {
                if (!validate.notblank([ "animals" ])) { return; }
                $("#button-update").button("disable");
                header.show_loading(_("Updating..."));
                let formdata = "mode=update&" + $("input, select, textarea").toPOST();
                try {
                    let response = await common.ajax_post("animal_bulk", formdata);
                    header.hide_loading();
                    header.show_info(_("{0} animals successfully updated.").replace("{0}", response));
                }
                finally {
                    $("#button-update").button("enable");
                }
            });

            $("#button-delete").button().click(async function() {
                if (!validate.notblank([ "animals" ])) { return; }
                try {
                    await tableform.delete_dialog(null, _("This will permanently remove the selected animals, are you sure?"));
                    $("#button-delete").button("disable");
                    header.show_loading(_("Deleting..."));
                    let formdata = "mode=delete&" + $("input, select, textarea").toPOST();
                    let response = await common.ajax_post("animal_bulk", formdata);
                    header.hide_loading();
                    header.show_info(_("{0} animals successfully deleted.").replace("{0}", response));
                    $("#animals").animalchoosermulti("clear");
                }
                finally {
                    $("#button-delete").button("enable");
                }
            });

            $("#location").change(animal_bulk.update_units);
            animal_bulk.update_units();

            if (!common.has_permission("ca")) { $("#button-update").hide(); }
            if (!common.has_permission("da")) { $("#button-delete").hide(); }

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

        },

        // Update the units available for the selected location
        update_units: async function() {
            let opts = ['<option value="-1">' + _("(no change)") + '</option>'];
            if ($("#location").val() != -1) {
                $("#unit").empty();
                const response = await common.ajax_post("animal_new", "mode=units&locationid=" + $("#location").val());
                $.each(html.decode(response).split("&&"), function(i, v) {
                    let [unit, desc] = v.split("|");
                    if (!unit) { return false; }
                    if (!desc) { desc = _("(available)"); }
                    opts.push('<option value="' + html.title(unit) + '">' + unit +
                        ' : ' + desc + '</option>');
                });
            }
            $("#unit").html(opts.join("\n")).change();
        },

        destroy: function() {
            common.widget_destroy("#animals");
            common.widget_destroy("#coordinator", "personchooser");
            common.widget_destroy("#currentvet", "personchooser");
            common.widget_destroy("#ownersvet", "personchooser");
            common.widget_destroy("#moveto", "personchooser");
        },

        name: "animal_bulk",
        animation: "newdata",
        autofocus: "#litterid", 
        title: function() { return _("Bulk change animals"); },

        routes: {
            "animal_bulk": function() {
                common.module_loadandstart("animal_bulk", "animal_bulk");
            }
        }


    };

    common.module_register(animal_bulk);

});
