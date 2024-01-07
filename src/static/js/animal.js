/*global $, _, asm, common, config, controller, dlgfx, additional, edit_header, format, header, html, log, microchip, social, tableform, validate */

$(function() {

    "use strict";

    const animal = {

        render_death: function() {
            return [
                '<h3><a href="#">' + _("Death") + ' <span id="tabdeath" style="display: none" class="asm-icon asm-icon-death"></span></a></h3><div>',
                '<table class="additionaltarget" data="to6">',
                '<tr>',
                '<td>',
                '<label for="deceaseddate">' + _("Deceased Date") + '</label>',
                '</td>',
                '<td>',
                '<input class="asm-textbox asm-datebox" id="deceaseddate" data-json="DECEASEDDATE" data-post="deceaseddate" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="deathcategory">' + _("Category") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="deathcategory" data-json="PTSREASONID" data-post="deathcategory">',
                html.list_to_options(controller.deathreasons, "ID", "REASONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td colspan="2">',
                '<label for="puttosleep">' + _("Euthanized") + '</label>',
                '<input class="asm-checkbox" type="checkbox" id="puttosleep" data-json="PUTTOSLEEP" data-post="puttosleep" />',
                '<label for="deadonarrival">' + _("Dead on arrival") + '</label>',
                '<input class="asm-checkbox" type="checkbox" id="deadonarrival" data-json="ISDOA" data-post="deadonarrival" />',
                '<label for="asilomarownerrequested" class="asilomar ownereuth">' + "Owner requested euthanasia" + '</label>',
                '<input class="asm-checkbox asilomar ownereuth" type="checkbox" id="asilomarownerrequested" data-json="ASILOMAROWNERREQUESTEDEUTHANASIA" data-post="asilomarownerrequested" />',
                '</td>',
                '</tr>',
                '</table>',
                '<div>',
                _("Notes") + '<br />',
                '<textarea class="asm-textarea" title="' + html.title(_("Notes")) + '" id="ptsreason" data-json="PTSREASON" data-post="ptsreason" rows="8"></textarea>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        render_details: function() {
            return [
                '<h3><a href="#">' + _("Details") + '</a></h3>',
                '<div>',
                '<table width="100%">',
                '<tr>',
                // left table
                '<td width="40%" class="asm-nested-table-td">',
                '<table>',
                '<tr>',
                '<td><label for="sheltercode">' + _("Code") + '</label></td>',
                '<td nowrap="nowrap">',
                '<input type="text" id="sheltercode" data-json="SHELTERCODE" data-post="sheltercode" class="asm-halftextbox" />',
                '<input type="text" id="shortcode" data-json="SHORTCODE" data-post="shortcode" class="asm-halftextbox" />',
                '<input type="hidden" id="yearcode" data-json="YEARCODEID" data-post="yearcode" />',
                '<input type="hidden" id="uniquecode" data-json="UNIQUECODEID" data-post="uniquecode" />',
                '</td>',
                '<td>',
                '<button id="button-gencode">' + _("Generate a new animal code") + '</button>',
                '</td>',
                '</tr>',
                '<tr id="litteridrow">',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label></td>',
                '<td><input type="text" id="litterid" data-json="ACCEPTANCENUMBER" data-post="litterid" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="animalname">' + _("Name") + '</label></td>',
                '<td><input type="text" id="animalname" data-json="ANIMALNAME" data-post="animalname" maxlength="255" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<button id="button-randomname">' + _("Generate a random name for this animal") + '</button>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="sex">' + _("Sex") + '</label></td>',
                '<td><select id="sex" data-json="SEX" data-post="sex" class="asm-selectbox">',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="animaltype">' + _("Type") + '</label></td>',
                '<td><select id="animaltype" data-json="ANIMALTYPEID" data-post="animaltype" class="asm-selectbox">',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="basecolour">' + _("Color") + '</label></td>',
                '<td><select id="basecolour" data-json="BASECOLOURID" data-post="basecolour" class="asm-selectbox">',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select></td>',
                '</tr>',
                '<tr id="coattyperow">',
                '<td><label for="coattype">' + _("Coat Type") + '</label></td>',
                '<td><select id="coattype" data-json="COATTYPE" data-post="coattype" class="asm-selectbox">',
                html.list_to_options(controller.coattypes, "ID", "COATTYPE"),
                '</select></td>',
                '</tr>',
                '<tr id="sizerow">',
                '<td><label for="size">' + _("Size") + '</label></td>',
                '<td><select id="size" data-json="SIZE" data-post="size" class="asm-selectbox">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select></td>',
                '</tr>',
                '<tr id="kilosrow">',
                '<td><label for="weight">' + _("Weight") + '</label></td>',
                '<td><span style="white-space: nowrap;">',
                '<input id="weight" data-json="WEIGHT" data-post="weight" class="asm-textbox asm-halftextbox asm-numberbox" />',
                '<label id="kglabel">' + _("kg") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="poundsrow">',
                '<td><label for="weightlb">' + _("Weight") + '</label></td>',
                '<td><span style="white-space: nowrap;">',
                '<input id="weightlb" class="asm-textbox asm-intbox" style="width: 70px" />',
                '<label id="lblabel">' + _("lb") + '</label>',
                '<input id="weightoz" class="asm-textbox asm-intbox" style="width: 70px" />',
                '<label id="ozlabel">' + _("oz") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '</table>',
                // right table
                '<td class="asm-nested-table-td">',
                '<table>',
                '<tr>',
                '<td>',
                // second column
                '<table class="additionaltarget asm-nested-table-td" data="to2">',
                '<tr>',
                '<td><label for="species">' + _("Species") + '</label></td>',
                '<td><select id="species" data-json="SPECIESID" data-post="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="breed1">' + _("Breed") + '</label></td>',
                '<td><select id="breed1" data-json="BREEDID" data-post="breed1" class="asm-selectbox">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" class="asm-selectbox" style="display:none;">',
                html.list_to_options_breeds(controller.breeds),
                '</select></td>',
                '</tr>',
                '<tr id="secondbreedrow">',
                '<td>',
                '<span style="white-space: nowrap">',
                '<label for="crossbreed">' + _("Crossbreed") + '</label>',
                '<input type="checkbox" class="asm-checkbox" id="crossbreed" data-json="CROSSBREED" data-post="crossbreed" /></td>',
                '</span>',
                '<td><select id="breed2" data-json="BREED2ID" data-post="breed2" class="asm-selectbox">',
                html.list_to_options_breeds(controller.breeds),
                '</select></td>',
                '</tr>',
                '<tr id="locationrow">',
                '<td><label for="location">' + _("Location") + '</label>',
                '<span class="asm-callout" id="callout-location">' + _("Where this animal is located within the shelter") + '</span>',
                '</td>',
                '<td>',
                '<input id="archived" data-json="ARCHIVED" type="hidden" />',
                '<input id="displaylocationname" data-json="DISPLAYLOCATIONNAME" type="hidden" />',
                '<select id="location" data-json="SHELTERLOCATION" data-post="location" class="asm-selectbox">',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="locationunitrow">',
                '<td><label for="unit">' + _("Unit") + '</label>',
                '<span class="asm-callout" id="callout-unit">' + _("Unit within the location, eg: pen or cage number") + '</span>',
                '</td>',
                '<td>',
                '<input id="unit" data-json="SHELTERLOCATIONUNIT" data-post="unit" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr id="lastlocation">',
                '<td><label>' + _("Last Location") + '</label></td>',
                '<td>',
                '<a class="asm-embed-name" href="animal_find_results?logicallocation=onshelter&shelterlocation=' + controller.animal.SHELTERLOCATION + '">' + controller.animal.SHELTERLOCATIONNAME + ' ' + common.nulltostr(controller.animal.SHELTERLOCATIONUNIT) + '</a>',
                '</td>',
                '</tr>',
                '<tr id="ownerrow">',
                '<td>',
                '<label for="owner">' + _("Owner"),
                '<span class="asm-callout">' + _("Update the current owner of this animal without returning and creating movements that affect your figures.") + '</span>',
                '</label>',
                '</td>',
                '<td>',
                '<input id="originalowner" data-json="OWNERID" data-mode="brief" data-post="owner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr id="animalflags">',
                '<td><label for="flags">' + _("Flags") + '</label></td>',
                '<td>',
                '<select id="flags" data="flags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dateofbirth">' + _("Date of Birth") + '</label></td>',
                '<td><input id="dateofbirth" data-json="DATEOFBIRTH" data-post="dateofbirth" class="asm-datebox asm-halftextbox" title="' + _("The date the animal was born") + '" />',
                '<input class="asm-checkbox" type="checkbox" id="estimateddob" data-json="ESTIMATEDDOB" data-post="estimateddob" title="' + _("This date of birth is an estimate") + '" />',
                _("Estimate"),
                '</td>',
                '</tr>',
                '<tr id="feerow">',
                '<td><label for="fee">' + _("Adoption Fee") + '</label></td>',
                '<td><input id="fee" data-json="FEE" data-post="fee" class="asm-currencybox asm-textbox" /></td>',
                '</tr>',
                // end second column
                '</table>',
                '</td>',
                '</tr>',
                // end right table
                '</table>',
                '</td>',

                // end outer table
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_entry: function() {
            return [
                '<h3><a href="#">' + _("Entry") + '</a></h3>',
                '<div>',
                // outer table
                '<table width="100%">',
                '<tr>',
                '<td width="50%" class="asm-nested-table-td">',
                // left table
                '<table width="100%">',
                '<tr id="coordinatorrow">',
                '<td valign="top" class="bottomborder">',
                '<label for="coordinator">' + _("Adoption Coordinator") + '</label>',
                '</td>',
                '<td valign="top" class="bottomborder">',
                '<input id="coordinator" data-json="ADOPTIONCOORDINATORID" data-filter="coordinator" data-post="adoptioncoordinator" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr id="originalownerrow">',
                '<td valign="top" class="bottomborder">',
                '<label for="originalowner">' + _("Original Owner") + '</label>',
                '</td>',
                '<td valign="top" class="bottomborder">',
                '<input id="originalowner" data-json="ORIGINALOWNERID" data-post="originalowner" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr id="broughtinbyownerrow">',
                '<td valign="top">',
                '<label for="broughtinby">' + _("Brought In By") + '</label>',
                '</td>',
                '<td valign="top">',
                '<input id="broughtinby" data-json="BROUGHTINBYOWNERID" data-post="broughtinby" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '</table>',
                // right table
                '</td>',
                '<td width="50%" class="asm-nested-table-td">',
                '<table width="100%" class="additionaltarget" data="to4">',
                '<tr id="datebroughtinrow">',
                '<td>',
                '<label for="datebroughtin">' + _("Date Brought In") + '</label>',
                '</td>',
                '<td>',
                '<input id="datebroughtin" data-json="DATEBROUGHTIN" data-post="datebroughtin" class="asm-textbox asm-datebox" />',
                '<input id="mostrecententrydate" class="asm-textbox" style="display: none" />',
                '</td>',
                '</tr>',
                '<tr id="timebroughtinrow">',
                '<td>',
                '<label for="timebroughtin">' + _("Time Brought In") + '</label>',
                '</td>',
                '<td>',
                '<input id="timebroughtin" data-json="DATEBROUGHTIN" data-post="timebroughtin" class="asm-textbox asm-timebox" />',
                '</td>',
                '</tr>',
                '<tr id="entrytyperow">',
                '<td><label for="entrytype">' + _("Entry Type") + '</label></td>',
                '<td><select id="entrytype" data-json="ENTRYTYPEID" data-post="entrytype" class="asm-selectbox">',
                html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME"),
                '</select></td>',
                '</tr>',
                '<tr id="entryreasonrow">',
                '<td><label for="entryreason">' + _("Entry Category") + '</label></td>',
                '<td><select id="entryreason" data-json="ENTRYREASONID" data-post="entryreason" class="asm-selectbox">',
                html.list_to_options(controller.entryreasons, "ID", "REASONNAME"),
                '</select></td>',
                '</tr>',
                '<tr class="asilomar">',
                '<td><label for="asilomarintakecategory">' + "Asilomar Category" + '</label></td>',
                '<td><select id="asilomarintakecategory" data-json="ASILOMARINTAKECATEGORY" data-post="asilomarintakecategory" class="asm-selectbox">',
                '<option value="0">Healthy</option>',
                '<option value="1">Treatable - Rehabilitatable</option>',
                '<option value="2">Treatable - Manageable</option>',
                '<option value="3">Unhealthy and Untreatable</option>',
                '</select></td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td><select id="jurisdiction" data-json="JURISDICTIONID" data-post="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="transferinrow">',
                '<td></td>',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="transferin" data-json="ISTRANSFER" />',
                '<label for="transferin">' + _("Transfer In") + '</label>',
                '</td>',
                '</tr>',
                '<tr class="asilomar">',
                '<td></td>',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="asilomartransferexternal" data-json="ASILOMARISTRANSFEREXTERNAL" data-post="asilomartransferexternal" />',
                '<label for="asilomartransferexternal">Outside community/coalition ',
                '<span id="asilomartx-callout" class="asm-callout">This animal was transferred in from outside the community/coalition</span>',
                '</label>',
                '</td>',
                '</tr>',
                '<tr id="pickeduprow">',
                '<td></td>',
                '<td>',
                '<span style="white-space: nowrap">',
                '<input class="asm-checkbox" type="checkbox" id="pickedup" data-json="ISPICKUP" data-post="pickedup" />',
                '<label for="pickedup">' + _("Picked Up") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="pickuplocationrow">',
                '<td>',
                '<label for="pickuplocation">' + _("Pickup Location") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="pickuplocation" data-json="PICKUPLOCATIONID" data-post="pickuplocation">',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="pickupaddressrow">',
                '<td>',
                '<label for="pickupaddress">' + _("Pickup Address") + '</label>',
                '</td>',
                '<td>',
                '<input class="asm-textbox" style="width: 98%" id="pickupaddress" data-json="PICKUPADDRESS" data-post="pickupaddress" />',
                '</td>',
                '</tr>',
                '<tr id="holdrow">',
                '<td></td>',
                '<td>',
                '<span style="white-space: nowrap">',
                '<input class="asm-checkbox" type="checkbox" id="hold" data-json="ISHOLD" data-post="hold" title=',
                '"' + html.title(_("This animal should be held in case it is reclaimed")) + '" />',
                '<label for="hold">' + _("Hold until") + '</label>',
                '<span class="asm-callout" id="callout-hold">' + _("Hold the animal until this date or blank to hold indefinitely") + '</span>',
                '<input class="asm-halftextbox asm-datebox" id="holduntil" data-json="HOLDUNTILDATE" data-post="holduntil" />',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="bondedwith1row">',
                '<td>',
                '<label for="bonded1">' + _("Bonded With") + '</label>',
                '</td>',
                '<td>',
                '<input id="bonded1" data-json="BONDEDANIMALID" data-post="bonded1" type="hidden" class="asm-animalchooser" />',
                '</td>',
                '</tr>',
                '<tr id="bondedwith2row">',
                '<td></td>',
                '<td>',
                '<input id="bonded2" data-json="BONDEDANIMAL2ID" data-post="bonded2" type="hidden" class="asm-animalchooser" />',
                '</td>',
                '</tr>',
                '<tr id="reasonnotfromownerrow">',
                '<td>',
                '<label for="reasonnotfromowner">' + _("Reason not from Owner") + '</label>',
                '</td>',
                '<td>',
                '<textarea class="asm-textarea" id="reasonnotfromowner" title="' + html.title(_("Reason not from Owner")) + '" ',
                'data-json="REASONNO" data-post="reasonnotfromowner" rows="2"></textarea>',
                '</td>',
                '</tr>',
                '<tr id="reasonforentryrow">',
                '<td>',
                '<label for="reasonforentry">' + _("Reason for Entry") + '</label>',
                '</td>',
                '<td>',
                '<textarea class="asm-textarea" title="' + _("Reason for Entry") + '" id="reasonforentry" data-json="REASONFORENTRY" data-post="reasonforentry" rows="2"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_entry_history: function() {
            if (controller.entryhistory.length == 0 || config.bool("DisableEntryHistory")) { return; }
            const asilomar_categories = {
                0: "Healthy",
                1: "Treatable - Rehabilitatable",
                2: "Treatable - Manageable",
                3: "Unhealthy and Untreatable"
            };
            let h = [
                '<h3><a href="#">' + _("Entry History") + '</a></h3>',
                '<div>',
                '<table class="asm-table">',
                '<thead>',
                '<tr>',
                '<th>' + _("Date") + '</th>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Code") + '</th>',
                '<th>' + _("Category") + '</th>',
                '<th>' + _("Coordinator") + '</th>',
                '<th>' + _("By") + '</th>',
                '<th>' + _("Owner") + '</th>',
                '<th>' + _("Hold") + '</th>',
                '<th>' + _("Pickup") + '</th>',
                '<th class="asilomar">' + _("Asilomar") + '</th>',
                '<th>' + _("Reason") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ];
            $.each(controller.entryhistory, function(i, v) {
                h.push('<tr>');
                h.push('<td><span class="nowrap">');
                h.push('<button type="button" class="deleteentryhistory" data-id="' + v.ID + '">' + _("Delete") + '</button>');
                h.push(format.date(v.ENTRYDATE) + '</span></td>');
                h.push('<td>' + v.ENTRYTYPENAME + (v.ASILOMARISTRANSFEREXTERNAL == 1 ? _('External') : '') + '</td>');
                h.push('<td>' + v.SHELTERCODE + '</td>');
                h.push('<td>' + v.ENTRYREASONNAME + '</td>');
                h.push('<td>' + html.person_link(v.ADOPTIONCOORDINATORID, v.COORDINATOROWNERNAME) + '</td>');
                h.push('<td>' + html.person_link(v.BROUGHTINBYOWNERID, v.BROUGHTINBYOWNERNAME) + '</td>');
                h.push('<td>' + html.person_link(v.ORIGINALOWNERID, v.ORIGINALOWNERNAME) + '</td>');
                h.push('<td>' + format.date(v.HOLDUNTILDATE) + '</td>');
                h.push('<td>' + (v.ISPICKUP == 1 ? v.PICKUPLOCATIONNAME + ' ' + v.PICKUPADDRESS : '') + '</td>');
                h.push('<td class="asilomar">' + asilomar_categories[v.ASILOMARINTAKECATEGORY] + '</td>');
                h.push('<td>' + v.REASONFORENTRY + ' ' + v.REASONNO + '</td>');
                h.push('</tr>');
            });
            h.push('</tbody></table></div>');
            return h.join("\n");
        },

        render_health_and_identification: function() {
            return [
                '<h3><a href="#">' + _("Health and Identification") + ' <span id="tabhealth" style="display: none" class="asm-icon asm-icon-health"></span></a></h3><div>',
                // outer table
                '<table width="100%">',
                '<tr>',
                '<td class="asm-nested-table-td">',
                // tested flags
                '<table>',
                '<tr id="microchiprow">',
                '<td nowrap="nowrap">',
                '<input class="asm-checkbox" type="checkbox" id="microchipped" data-json="IDENTICHIPPED" data-post="microchipped" />',
                '<label for="microchipped">' + _("Microchipped") + '</label>',
                '</td>',
                '<td>',
                '<input id="microchipdate" data-json="IDENTICHIPDATE" data-post="microchipdate" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td>',
                '<input type="text" id="microchipnumber" data-json="IDENTICHIPNUMBER" data-post="microchipnumber" class="asm-textbox" maxlength="15" placeholder="' + html.title(_("Number")) + '" /> <span id="microchipbrand"></span> <button id="button-microchipcheck">' + microchip.check_site_name() + '</button>',
                '</td>',
                '</tr>',
                '<tr id="microchiprow2">',
                '<td nowrap="nowrap"></td>',
                '<td>',
                '<input id="microchipdate2" data-json="IDENTICHIP2DATE" data-post="microchipdate2" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td>',
                '<input type="text" id="microchipnumber2" data-json="IDENTICHIP2NUMBER" data-post="microchipnumber2" class="asm-textbox" maxlength="15" placeholder="' + html.title(_("Number")) + '" /> <span id="microchipbrand2"></span> <button id="button-microchipcheck2">' + microchip.check_site_name() + '</button>',
                '</td>',
                '</tr>',
                '<tr id="tattoorow">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="tattoo" data-json="TATTOO" data-post="tattoo" />',
                '<label for="tattoo">' + _("Tattoo") + '</label>',
                '</td>',
                '<td>',
                '<input id="tattoodate" data-json="TATTOODATE" data-post="tattoodate" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td>',
                '<input type="text" id="tattoonumber" data-json="TATTOONUMBER" data-post="tattoonumber" class="asm-textbox" placeholder="' + html.title(_("Number")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="smarttagrow">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="smarttag" data-json="SMARTTAG" data-post="smarttag" />',
                '<label for="smarttag">' + _("SmartTag PETID") + '</label>',
                '</td>',
                '<td>',
                '<input id="smarttagnumber" data-json="SMARTTAGNUMBER" data-post="smarttagnumber" class="asm-halftextbox asm-alphanumberbox" placeholder="' + html.title(_("Number")) + '" />',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="smarttagtype" data-json="SMARTTAGTYPE" data-post="smarttagtype">',
                '<option value="0">' + _("Annual") + '</option>',
                '<option value="1">' + _("5 Year") + '</option>',
                '<option value="2">' + _("Lifetime") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="neuteredrow">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="neutered" data-json="NEUTERED" data-post="neutered" />',
                '<label for="neutered">' + _("Altered") + '</label>',
                '</td>',
                '<td>',
                '<input id="neutereddate" data-json="NEUTEREDDATE" data-post="neutereddate" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td valign="top">',
                '<input id="neuteringvet" data-json="NEUTEREDBYVETID" data-post="neuteringvet" data-mode="brief" data-filter="vet" type="hidden" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr id="declawedrow" class="cats">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="declawed" data-json="DECLAWED" data-post="declawed" />',
                '<label id="declawed-label" for="declawed">' + _("Declawed") + '</label>',
                '</td>',
                '</tr>',
                '<tr id="heartwormrow" class="dogs">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="heartwormtested" data-json="HEARTWORMTESTED" data-post="heartwormtested" />',
                '<label for="heartwormtested">' + _("Heartworm Tested") + '</label>',
                '</td>',
                '<td>',
                '<input id="heartwormtestdate" data-json="HEARTWORMTESTDATE" data-post="heartwormtestdate" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="heartwormtestresult" data-json="HEARTWORMTESTRESULT" data-post="heartwormtestresult">',
                html.list_to_options(controller.posneg, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="fivlrow" class="cats">',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="fivltested" data-json="COMBITESTED" data-post="fivltested" />',
                '<label for="fivltested">' + _("FIV/L Tested") + '</label>',
                '</td>',
                '<td>',
                '<input id="fivltestdate" data-json="COMBITESTDATE" data-post="fivltestdate" class="asm-halftextbox asm-datebox" placeholder="' + html.title(_("Date")) + '" />',
                '</td>',
                '<td>',
                '<select class="asm-halftextbox selectbox" id="fivresult" data-json="COMBITESTRESULT" data-post="fivresult">',
                html.list_to_options(controller.posneg, "ID", "NAME"),
                '</select>',
                '<select class="asm-halftextbox selectbox" id="flvresult" data-json="FLVRESULT" data-post="flvresult">',
                html.list_to_options(controller.posneg, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<input class="asm-checkbox" type="checkbox" id="specialneeds" data-json="HASSPECIALNEEDS" data-post="specialneeds" title="' + _("This animal has special needs") + '"  />',
                '<label for="specialneeds">' + _("Special Needs") + '</label>',
                '</td>',
                '</tr>',
                // end flag table
                '</table>',
                // separate table for additional fields
                '<table class="additionaltarget" data="to5">',
                '<tr id="rabiestagrow" class="cats dogs">',
                '<td><label for="rabiestag">' + _("Rabies Tag") + '</label></td>',
                '<td><input id="rabiestag" data-json="RABIESTAG" data-post="rabiestag" class="asm-textbox" maxlength="20" />',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td class="asm-nested-table-td">',
                // health problems/vet fields
                '<label for="healthproblems">' + _("Health Problems") + '</label><br />',
                '<textarea id="healthproblems" data-json="HEALTHPROBLEMS" data-post="healthproblems" class="asm-textarea" rows="4"></textarea>',
                '<table>',
                '</table>',
                '<table>',
                '<tr>',
                '<td valign="top" class="bottomborder">',
                '<label for="currentvet">' + _("Current Vet") + '</label>',
                '</td>',
                '<td valign="top" class="bottomborder">',
                '<input id="currentvet" data-json="CURRENTVETID" data-post="currentvet" type="hidden" data-filter="vet" class="asm-personchooser" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td valign="top">',
                '<label for="ownersvet">' + _("Owners Vet") + '</label>',
                '</td>',
                '<td valign="top">',
                '<input id="ownersvet" data-json="OWNERSVETID" data-post="ownersvet" type="hidden" data-filter="vet" class="asm-personchooser"  />',
                '</td>',
                '</tr>',
                '</table>',
                // end outer table
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_events: function() {
            
            if (controller.events.length == 0 || !common.has_permission("vea") || config.bool("DisableEvents")) {
                return;
            }

            let h = [
                '<h3><a href="#">' + _("Events") + '</a></h3>',
                '<div>',
                '<table class="asm-table">',
                '<thead>',
                '<tr>',
                '<th>' + _("Start Date") + '</th>',
                '<th>' + _("End Date") + '</th>',
                '<th>' + _("Name") + '</th>',
                '<th>' + _("Address") + '</th>',
                '<th>' + _("Arrival") + '</th>',
                '<th>' + _("Adopted") + '</th>',
                '<th>' + _("Comments") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ];

            $.each(controller.events, function(i, v) {
                h.push('<tr>');
                h.push('<td><b><a href="event?id=' + v.EVENTID + '">' + format.date(v.STARTDATETIME) + '</a></b></td>');
                h.push('<td>' + format.date(v.ENDDATETIME) + '</td>');
                h.push('<td>' + common.nulltostr(v.EVENTNAME) + '</td>');
                h.push('<td>' + v.EVENTADDRESS + ', ' + (v.EVENTTOWN != null ? v.EVENTTOWN : '') + ' ' + (v.EVENTCOUNTY != null ? v.EVENTCOUNTY : '') + ' ' + (v.EVENTPOSTCODE != null ? v.EVENTPOSTCODE : '') + ' ' + (v.EVENTCOUNTRY != null ? v.EVENTCOUNTRY : '') + '</td>');
                h.push('<td><b>' + format.date(v.ARRIVALDATE) + '</b></td>');
                h.push('<td>' + (v.ADOPTED==1 ? "&#9989;" : "&nbsp;")  + '</td>');
                h.push('<td>' + common.nulltostr(v.COMMENTS) + '</td>');
                h.push('</tr>');
            });

            h.push('</table></div>');
            return h.join("\n");
        },

        render_incidents: function() {
            
            if (controller.incidents.length == 0 || !common.has_permission("vaci")) {
                return;
            }

            let h = [
                '<h3><a href="#">' + _("Incidents") + '</a></h3>',
                '<div>',
                '<table class="asm-table">',
                '<thead>',
                '<tr>',
                '<th>' + _("Type") + '</th>',
                '<th>' + _("Number") + '</th>',
                '<th>' + _("Incident Date/Time") + '</th>',
                '<th>' + _("Address") + '</th>',
                '<th>' + _("Suspect") + '</th>',
                '<th>' + _("Completed") + '</th>',
                '<th>' + _("Notes") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ];

            $.each(controller.incidents, function(i, v) {
                h.push('<tr>');
                h.push('<td><b><a href="incident?id=' + v.ACID + '">' + v.INCIDENTNAME + '</a></b></td>');
                h.push('<td>' + format.padleft(v.ACID, 6) + '</td>');
                h.push('<td>' + format.date(v.INCIDENTDATETIME) + ' ' + format.time(v.INCIDENTDATETIME) + '</td>');
                h.push('<td>' + v.DISPATCHADDRESS + ', ' + v.DISPATCHTOWN + ' ' + v.DISPATCHCOUNTY + ' ' + v.DISPATCHPOSTCODE + '</td>');
                h.push('<td><b>' + html.person_link(v.OWNERID, v.OWNERNAME) + '</b></td>');
                h.push('<td>' + format.date(v.COMPLETEDDATE) + ' ' + common.nulltostr(v.COMPLETEDNAME) + '</td>');
                h.push('<td>' + v.CALLNOTES + '</td>');
                h.push('</tr>');
            });

            h.push('</table></div>');
            return h.join("\n");
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

        render_publish_history: function() {
            
            if (controller.publishhistory.length == 0) {
                return;
            }

            const pname = function(p) {
                let t = p;
                if (p == "first") { t = _("Adoptable and published for the first time"); }
                else if (p == "html") { t = html.icon("web") + " " + _("Published to Website"); }
                else if (p == "petfinder") { t = "Published to petfinder.com"; }
                else if (p == "adoptapet") { t = "Published to adoptapet.com"; }
                else if (p == "rescuegroups") { t = "Published to rescuegroups.org"; }
                else if (p == "meetapet") { t = "Published to meetapet.com"; }
                else if (p == "helpinglostpets") { t = "Published to helpinglostpets.com"; }
                else if (p == "savourlife") { t = "Published to savour-life.com.au"; }
                else if (p == "petrescue") { t = "Published to petrescue.com.au"; }
                else if (p == "petslocated") { t = "Published to petslocated.com"; }
                else if (p == "maddiesfund") { t = "Published to Maddie's Pet Assistant"; }
                
                else if (p == "petlink") { t = html.icon("microchip") + " Microchip registered with PetLink"; }
                else if (p == "pettracuk") { t = html.icon("microchip") + " Microchip registered with AVID/PETtrac UK"; }
                else if (p == "anibaseuk") { t = html.icon("microchip") + " Microchip registered with idENTICHIP/Anibase UK"; }
                else if (p == "smarttag") { t = html.icon("microchip") + " Microchip/Tag registered with SmartTag"; }
                else if (p == "akcreunite") { t = html.icon("microchip") + " Microchip registered with AKC Reunite"; }
                else if (p == "buddyid") { t = html.icon("microchip") + " Microchip registered with BuddyID"; }
                else if (p == "homeagain") { t = html.icon("microchip") + " Microchip registered with HomeAgain"; }
                else if (p == "foundanimals") { t = html.icon("microchip") + " Microchip registered with FoundAnimals"; }

                else if (p == "shareweb") { t = html.icon("web") + " " + _("Shared weblink"); }
                else if (p == "shareemail") { t = html.icon("email") + " " + _("Shared email"); }
                else if (p == "sharepic") { t = html.icon("media") + " " + _("Shared photo"); }
                else if (p == "facebook") { t = html.icon("facebook") + " Shared on Facebook"; }
                else if (p == "twitter") { t = html.icon("twitter") + " Shared on Twitter"; }
                else if (p == "gplus") { t = html.icon("gplus") + " Shared on Google+"; }
                else if (p == "pinterest") { t = html.icon("pinterest") + " Shared on Pinterest"; }
                else if (p == "tumblr") { t = html.icon("tumblr") + " Shared on Tumblr"; }

                return t;
            },
            h = [
                '<h3><a href="#">' + _("Publishing History") + '</a></h3>',
                '<div>'
            ];

            $.each(controller.publishhistory, function(i, v) {
                let err = "";
                if (v.EXTRA) { 
                    err = " : <span style='color: red'>" + v.EXTRA + "</span>"; 
                }
                else if (common.has_permission("uipb")) { 
                    err = ' <button type="button" class="forgetlink" data-service="' + v.PUBLISHEDTO + '">' + _("Forget") + '</button>'; 
                }
                h.push('<p>' + format.date(v.SENTDATE) + ' - ' + pname(v.PUBLISHEDTO) + err + '</p>');
            });

            h.push('</div>');
            return h.join("\n");
        },

        /**
         * Render the animal details screen
         */
        render: function() {
            let h = [
                '<div id="button-document-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                edit_header.template_list(controller.templates, "ANIMAL", controller.animal.ID),
                '</ul>',
                '</div>',
                '<div id="dialog-clone-confirm" style="display: none" title="' + html.title(_("Clone")) + '">',
                '<p><span class="ui-icon ui-icon-alert"></span> ' + _("Clone this animal?") + '</p>',
                '</div>',
                '<div id="emailform"></div>',
                '<div id="dialog-popupwarning" style="display: none" title="' + html.title(_("Warning")) + '">',
                '<p>' + html.error(controller.animal.POPUPWARNING) + '</p>',
                '</div>',
                '<div id="dialog-merge" style="display: none" title="' + html.title(_("Select animal to merge")) + '">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("Select an animal to merge into this record. The selected animal will be removed, and their movements, diary notes, log entries, etc. will be reattached to this record."),
                '</p>',
                '</div>',
                html.capture_autofocus(),
                '<table width="100%">',
                '<tr>',
                '<td><label for="mergeanimal">' + _("Animal") + '</label></td>',
                '<td>',
                '<input id="mergeanimal" data="mergeanimal" type="hidden" class="asm-animalchooser" value="" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<div id="button-share-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-shareweb" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("web") + ' ' + _("Link to this animal") + '</a></li>',
                    '<li id="button-sharepic" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("media") + ' ' + _("Link to a photo of this animal") + '</a></li>',
                    '<li id="button-shareemail" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("email") + ' ' + _("Email") + '</a></li>',
                    '<li id="button-social" class="sharebutton asm-menu-category">' + _("Social") + ' </li>',
                    '<li id="button-facebook" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("facebook") + ' ' + _("Facebook") + '</a></li>',
                    '<li id="button-twitter" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("twitter") + ' ' + _("Twitter") + '</a></li>',
                    '<li id="button-gplus" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("gplus") + ' ' + _("Google+") + '</a></li>',
                    '<li id="button-pinterest" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("pinterest") + ' ' + _("Pinterest") + '</a></li>',
                    '<li id="button-tumblr" class="sharebutton asm-menu-item"><a '
                        + '" target="_blank" href="#">' + html.icon("tumblr") + ' ' + _("Tumblr") + '</a></li>',

                '</ul>',
                '</div>',
                edit_header.animal_edit_header(controller.animal, "animal", controller.tabcounts),
                tableform.buttons_render([
                    { id: "save", text: _("Save"), icon: "save", tooltip: _("Save this animal") },
                    { id: "clone", text: _("Clone"), icon: "copy", tooltip: _("Create a new animal by copying this one") },
                    { id: "merge", text: _("Merge"), icon: "copy", tooltip: _("Merge another animal into this one") },
                    { id: "delete", text: _("Delete"), icon: "delete", tooltip: _("Delete this animal") },
                    { id: "email", text: _("Email"), icon: "email", tooltip: _("Send an email relating to this animal") },
                    { id: "document", text: _("Document"), type: "buttonmenu", icon: "document", tooltip: _("Generate a document from this animal") },
                    { id: "newentry", text: _("New Entry"), icon: "new", tooltip: _("Generate a new code and archive the current entry data"),
                        hideif: function() { 
                            return config.bool("DisableEntryHistory") || 
                                controller.returnedexitmovements.length == 0 ||
                                controller.returnedexitmovements.length == controller.entryhistory.length; } },
                    { id: "match", text: _("Match"), icon: "match", tooltip: _("Match this animal with the lost and found database") },
                    { id: "littermates", text: _("Littermates"), icon: "litter", tooltip: _("View littermates") },
                    { id: "share", text: _("Share"), type: "buttonmenu", icon: "share" }
                ]),
                '<div id="asm-details-accordion">',
                this.render_details(),
                this.render_notes(),
                '<h3 id="asm-additional-accordion"><a href="#">' + _("Additional") + '</a></h3>',
                '<div>',
                additional.additional_fields(controller.additional),
                '</div>',
                this.render_entry(),
                this.render_entry_history(),
                this.render_health_and_identification(),
                this.render_death(),
                this.render_incidents(),
                this.render_events(),
                this.render_publish_history(),
                html.audit_trail_accordion(controller),
                '</div>', // accordion
                '</div>', // asmcontent
                '</div>'  // tabs
            ].join("\n");
            return h;
        },

        /* Update the breed selects to only show the breeds for the selected species.
         * If no breeds are available the species will be displayed.
         * */
        update_breed_list: function() {
            $('optgroup', $('#breed1')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed1'));
            $('#breed1').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()){
                    $(this).remove();
                }
            });
            if($('#breed1 option').length == 0) {
                $('#breed1').append("<option value='0'>"+$('#species option:selected').text() + "</option>");
            }
            $('optgroup', $('#breed2')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed2'));
            $('#breed2').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()) {
                    $(this).remove();
                }
            });
            if ($('#breed2 option').length == 0) {
                $('#breed2').append("<option value='0'>"+$('#species option:selected').text()+"</option>");
            }
            if (controller.animal.CROSSBREED == 1 ||
                (common.array_in($("#species").val(), config.str("CrossbreedSpecies").split(",")) && !config.bool("UseSingleBreedField"))) {
                $("#secondbreedrow").show();
            }
            else {
                $("#secondbreedrow").hide();
                $("#crossbreed").prop("checked", false);
            }
        },

        // Update the units available for the selected location
        update_units: async function() {
            const response = await common.ajax_post("animal_new", "mode=units&locationid=" + $("#location").val());
            let src = [];
            $.each(html.decode(response).split("&&"), function(i, v) {
                let [unit, desc] = v.split("|");
                if (!unit) { return false; }
                if (!desc) { desc = _("(available)"); }
                src.push({ label: unit + ' : ' + desc, value: unit });
            });
            // Reload the source of available units
            $("#unit").autocomplete({ 
                source: src,
                // Dirty the form when an item is chosen from the dropdown
                select: function(event, ui) {
                    validate.dirty(true);
                }
            // Display the autocomplete on focus
            }).bind('focus', function() { 
                $(this).autocomplete("search", ":"); 
            });
        },

        /** 
         *  Enable widgets based on loaded data, security and configuration options
         */
        enable_widgets: function() {

            // DATA ===========================================

            // Hide additional accordion section if there aren't
            // any additional fields declared
            let ac = $("#asm-additional-accordion");
            let an = ac.next();
            if (an.find(".additional").length == 0) {
                ac.hide(); an.hide();
            }
            
            // Crossbreed flag being unset hides second breed field
            if ($("#crossbreed").is(":checked")) {
                $("#breed2").fadeIn();
            }
            else {
                $("#breed2").fadeOut();
                $("#breed2").select("value", $("#breed1").select("value"));
            }
            
            // Show/hide death fields based on deceased date
            if ($("#deceaseddate").val() == "") {
                $("#deathcategory").closest("tr").fadeOut();
                $("#puttosleep").closest("tr").fadeOut();
                $("#ptsreason").closest("div").fadeOut();
            }
            else {
                $("#deathcategory").closest("tr").fadeIn();
                $("#puttosleep").closest("tr").fadeIn();
                $("#ptsreason").closest("div").fadeIn();
            }

            // If we're a US shelter and this is a cat or a dog, show the asilomar categories
            if (asm.locale == "en" && !config.bool("DisableAsilomar") &&
                ($("#species").select("value") == 1 || $("#species").select("value") == 2) ) {
                $(".asilomar").show();
            }
            else {
                $(".asilomar").hide();
            }

            // Show cat and dog specific fields based on species
            $(".dogs, .cats").hide();
            if ($("#species").select("value") == 1) { $(".dogs").show(); }
            if ($("#species").select("value") == 2) { $(".cats").show(); }

            // Enable/disable health and identification fields based on checkboxes
            $("#microchipdate, #microchipnumber, #microchiprow2").toggle($("#microchipped").is(":checked"));
            $("#tattoodate, #tattoonumber").toggle($("#tattoo").is(":checked"));
            $("#smarttagnumber, #smarttagtype").toggle($("#smarttag").is(":checked"));
            $("#neutereddate").toggle($("#neutered").is(":checked"));
            $("#neuteringvet").closest("td").toggle($("#neutered").is(":checked"));
            $("#heartwormtestdate, #heartwormtestresult").toggle($("#heartwormtested").is(":checked"));
            $("#fivltestdate, #fivresult, #flvresult").toggle($("#fivltested").is(":checked"));

            // Show pickup fields if the animal is a pickup
            $("#pickupaddressrow, #pickuplocationrow").toggle($("#pickedup").is(":checked"));

            // Change the Brought In By text and filter if this record is a pickup or transfer
            if ($("#pickedup").is(":checked")) { 
                $("label[for='broughtinby']").html(_("Picked Up By")); 
                $("#broughtinby").personchooser("set_filter", "aco");
            }
            else if ($("#entrytype").val() == 3) { 
                $("label[for='broughtinby']").html(_("Transferred From")); 
                $("#broughtinby").personchooser("set_filter", "shelter");
            }
            else { 
                $("label[for='broughtinby']").html(_("Brought In By")); 
                $("#broughtinby").personchooser("set_filter", "all");
            }

            // Change the Original Owner text if this record is non-shelter
            if ($("#flags option[value='nonshelter']").is(":selected")) {
                $("label[for='originalowner']").html(_("Owner"));
            }
            else {
                $("label[for='originalowner']").html(_("Original Owner"));
            }

            // If the animal doesn't have a litterid, disable the littermates button
            if ($("#litterid").val() == "")  {
                $("#button-littermates").button("disable");
            }
            else {
                $("#button-littermates").button("enable");
            }

            // Not having any active litters disables join litter button
            if ($("#sellitter option").length == 0) {
                $("#button-litterjoin").button("disable");
            }

            // Hide the internal location dropdown row if the animal is off the shelter
            // or dead and show the last location info instead.
            if (controller.animal.ACTIVEMOVEMENTID || controller.animal.DECEASEDDATE) {
                $("#locationrow").hide();
                $("#locationunitrow").hide();
                $("#lastlocation").show();
            }
            else {
                $("#lastlocation").hide();
            }

            // If the animal is non-shelter, don't show the location, 
            // pickup, brought in by owner, bonded with, type, reasons or asilomar
            if ($("#flags option[value='nonshelter']").is(":selected")) {
                $("#lastlocation").hide();
                $("#locationrow").hide();
                $("#locationunitrow").hide();
                if ($("#animalname").val().indexOf("Template") != 0) { 
                    // Only hide the fee and intake date for non-shelter non-template animals
                    $("#feerow").hide(); 
                    $("#datebroughtinrow").hide();
                    $("#timebroughtinrow").hide();
                } 
                $("#pickeduprow").hide();
                $("#holdrow").hide();
                $("#coordinatorrow").hide();
                $("#ownerrow").hide();
                $("#broughtinbyownerrow").hide();
                $("#originalownerrow td").removeClass("bottomborder");
                $("#bondedwith1row").hide();
                $("#bondedwith2row").hide();
                $("#entryreasonrow").hide();
                $("#entrytyperow").hide();
                $("#transferinrow").hide();
                $("#reasonforentryrow").hide();
                $("#reasonnotfromownerrow").hide();
                $(".asilomar").hide();
            }

            // If we're hiding the entry type field and transfer in is selected, choose
            // the correct entry type (since transfer in is not actually saved and the
            // backend sets ISTRANSFER based on ENTRYTYPEID==3)
            if (config.bool("DontShowEntryType") && $("#transferin").is(":checked")) {
                $("#entrytype").select("value", "3");
            }
            else if (config.bool("DontShowEntryType")) {
                $("#entrytype").val(config.integer("AFDefaultEntryType"));
            }

            // If the animal is actively boarding right now, show the location fields
            if (controller.animal.HASACTIVEBOARDING) {
                $("#lastlocation").hide();
                $("#locationrow").show();
                $("#locationunitrow").show();
            }

            // Still show the owner requested euth field for non-shelter animals
            if (asm.locale == "en" && !config.bool("DisableAsilomar") &&
                ($("#species").select("value") == 1 || $("#species").select("value") == 2) &&
                $("#flags option[value='nonshelter']").is(":selected")) {
                $(".ownereuth").show();
            }

            // If the animal has an exit movement, show the owner field
            if (controller.animal.ARCHIVED == 1 && 
                (controller.animal.ACTIVEMOVEMENTTYPE == 1 ||
                controller.animal.ACTIVEMOVEMENTTYPE == 3 || 
                controller.animal.ACTIVEMOVEMENTTYPE == 5)) {
                $("#ownerrow").show();
            }
            else {
                $("#ownerrow").hide();
            }

            // If the animal has entry history, hide the datebrought in field and show
            // a read only copy of the most recent entry date instead.
            if (controller.entryhistory.length > 0) {
                $("#datebroughtin").hide();
                $("#timebroughtin").closest("tr").hide();
                $("#mostrecententrydate").val(format.date(controller.animal.MOSTRECENTENTRYDATE)).textbox("disable").show();
            }

            // CONFIG ===========================

            if (config.bool("DisableShortCodesControl")) {
                $("#shortcode").hide();
                $("#sheltercode").addClass("asm-textbox");
                $("#sheltercode").removeClass("asm-halftextbox");
            }

            if (config.bool("LockCodes") && common.current_url().indexOf("cloned=true") == -1) {
                $("#button-gencode").hide();
                $("#sheltercode").textbox("disable");
                $("#shortcode").textbox("disable");
                // Lock any fields used in the coding format, but not if
                // manual codes are on since manual codes are not dependent
                // on any other fields.
                if (!config.bool("ManualCodes")) {
                    if (config.str("CodingFormat").indexOf("T") != -1 || 
                        config.str("ShortCodingFormat").indexOf("T") != -1) {
                        $("#animaltype").select("disable");
                    }
                    if (config.str("CodingFormat").indexOf("Y") != -1 ||
                        config.str("CodingFormat").indexOf("M") != -1 ||
                        config.str("ShortCodingFormat").indexOf("Y") != -1 ||
                        config.str("ShortCodingFormat").indexOf("M") != -1) {
                        $("#datebroughtin").textbox("disable");
                        $("#timebroughtin").textbox("disable");
                    }
                    if (config.str("CodingFormat").indexOf("S") != -1 || 
                        config.str("ShortCodingFormat").indexOf("S") != -1) {
                        $("#species").select("disable");
                    }
                    if (config.str("CodingFormat").indexOf("E") != -1 || 
                        config.str("ShortCodingFormat").indexOf("E") != -1) {
                        $("#entryreason").select("disable");
                    }
                }
            }

            // Converting between whole number for weight and pounds and ounces
            const lboz_to_fraction = function() {
                let lb = format.to_int($("#weightlb").val());
                lb += format.to_int($("#weightoz").val()) / 16.0;
                $("#weight").val(String(lb));
            };

            const fraction_to_lboz = function() {
                let kg = format.to_float($("#weight").val()),
                    lb = format.to_int($("#weight").val()),
                    oz = (kg - lb) * 16.0;
                $("#weightlb").val(lb);
                $("#weightoz").val(oz);
            };

            if (config.bool("ShowWeightInLbs")) {
                $("#kilosrow").hide();
                $("#poundsrow").show();
                $("#weightlb, #weightoz").change(lboz_to_fraction);
                fraction_to_lboz();
            }
            else if (config.bool("ShowWeightInLbsFraction")) {
                $("#kglabel").html(_("lb"));
                $("#kilosrow").show();
                $("#poundsrow").hide();
            }
            else {
                $("#kglabel").html(_("kg"));
                $("#kilosrow").show();
                $("#poundsrow").hide();
            }

            if (config.bool("DontShowLitterID")) { $("#litteridrow").hide(); }
            if (config.bool("DontShowLocationUnit")) { $("#locationunitrow").hide(); }
            if (config.bool("DontShowRabies")) { $("#rabiestagrow").hide(); }
            if (config.bool("UseSingleBreedField")) { $("#secondbreedrow").hide(); }
            if (config.bool("DontShowAdoptionFee")) { $("#feerow").hide(); }
            if (config.bool("DontShowAdoptionCoordinator")) { $("#coordinatorrow").hide(); }
            if (config.bool("DontShowCoatType")) { $("#coattyperow").hide(); }
            if (config.bool("DontShowEntryType")) { 
                $("#entrytyperow").hide(); 
                $("#transferinrow").show(); 
            } 
            else { 
                $("#entrytyperow").show();
                $("#transferinrow").hide(); 
            }
            if (config.bool("DontShowJurisdiction")) { $("#jurisdictionrow").hide(); }
            if (config.bool("DontShowSize")) { $("#sizerow").hide(); }
            if (config.bool("DontShowWeight")) { $("#kilosrow, #poundsrow").hide(); }
            if (config.bool("DontShowMicrochip")) { $("#microchiprow, #microchiprow2").hide(); }
            if (config.bool("DontShowTattoo")) { $("#tattoorow").hide(); }
            if (config.str("SmartTagFTPUser") == "") { $("#smarttagrow").hide(); }
            if (config.bool("DontShowBonded")) { $("#bondedwith1row, #bondedwith2row").hide(); }
            if (config.bool("DontShowPickup")) { $("#pickeduprow, #pickupaddressrow, #pickuplocationrow").hide(); }
            if (config.bool("DontShowNeutered")) { $("#neuteredrow").hide(); }
            if (config.bool("DontShowDeclawed")) { $("#declawed").closest("tr").hide(); }
            if (config.bool("DontShowGoodWith")) { $(".goodwith").hide(); }
            if (config.bool("DontShowCombi")) { $("#fivlrow").hide(); }
            if (config.bool("DontShowHeartworm")) { $("#heartwormrow").hide(); }
            if (config.bool("DisableLostAndFound")) { $("#button-match").hide(); }
            if (config.bool("ManualCodes")) { $("#button-gencode").hide(); }
            if (!config.bool("AddAnimalsShowTimeBroughtIn")) { $("#timebroughtinrow").hide(); }

            // SECURITY =============================================================

            if (!common.has_permission("ca")) { $("#button-save").hide(); }
            if (!common.has_permission("aa")) { $("#button-clone").hide(); }
            if (!common.has_permission("ma")) { $("#button-merge").hide(); }
            if (!common.has_permission("da")) { $("#button-delete").hide(); }
            if (!common.has_permission("emo")) { $("#button-email").hide(); }
            if (!common.has_permission("gaf")) { $("#button-document").hide(); }
            if (!common.has_permission("vo")) { $("#button-currentowner").hide(); }
            if (!common.has_permission("mlaf")) { $("#button-match").hide(); }
            if (!common.has_permission("vll")) { $("#button-littermates").hide(); }
            if (!common.has_permission("uipb")) { $("#button-share").hide(); }

            // ACCORDION ICONS =======================================================

            // A value in health problems or special needs being checked flags health/id tab
            if ($("#healthproblems").val() != "" || $("#specialneeds").is(":checked")) {
                $("#tabhealth").show();
            }
            else {
                $("#tabhealth").hide();
            }

            // A deceased date being completed flags Death tab
            if ($("#deceaseddate").val() != "") {
                $("#tabdeath").show();
            }
            else {
                $("#tabdeath").hide();
            }

        },

        show_microchip_supplier: function() {
            microchip.manufacturer("#microchipnumber", "#microchipbrand");
            microchip.manufacturer("#microchipnumber2", "#microchipbrand2");
            // Show the microchip check buttons
            $("#button-microchipcheck, #button-microchipcheck2").hide();
            if (microchip.is_check_available($("#microchipnumber").val())) { $("#button-microchipcheck").show(); }
            if (microchip.is_check_available($("#microchipnumber2").val())) { $("#button-microchipcheck2").show(); }
        },

        show_popup_warning: async function() {
            if (controller.animal.POPUPWARNING) {
                await tableform.show_okcancel_dialog("#dialog-popupwarning", _("Ok"), { hidecancel: true });
            }
        },

        /** Validates the form fields prior to saving */
        validation: function() {

            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // name
            if (common.trim($("#animalname").val()) == "") {
                header.show_error(_("Name cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("animalname");
                return false;
            }

            // date brought in
            if (common.trim($("#datebroughtin").val()) == "") {
                header.show_error(_("Date brought in cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 3);
                validate.highlight("datebroughtin");
                return false;
            }

            // date of birth
            if (common.trim($("#dateofbirth").val()) == "") {
                header.show_error(_("Date of birth cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("dateofbirth");
                return false;
            }

            // shelter code
            if (common.trim($("#sheltercode").val()) == "") {
                header.show_error(_("Shelter code cannot be blank"));
                $("#asm-details-accordion").accordion("option", "active", 0);
                validate.highlight("sheltercode");
                return false;
            }

            // any additional fields that are marked mandatory
            if (!additional.validate_mandatory()) {
                return false;
            }

            return true;
        },

        /** Generates a new animal code */
        generate_code: async function() {
            validate.dirty(false);
            let formdata = "mode=gencode&datebroughtin=" + format.date(controller.animal.MOSTRECENTENTRYDATE) + 
                "&animaltypeid=" + $("#animaltype").val() +
                "&entryreasonid=" + $("#entryreason").val() +
                "&speciesid=" + $("#species").val();
            let response = await common.ajax_post("animal", formdata);
            let codes = response.split("||");
            $("#sheltercode").val(html.decode(codes[0]));
            $("#shortcode").val(html.decode(codes[1]));
            $("#uniquecode").val(codes[2]);
            $("#yearcode").val(codes[3]);
            validate.dirty(true);
        },

        /**
         * Generates the sharing links/share button
         */
        set_sharinglinks: function() {

            // Share data
            let share_url = asm.serviceurl + "?method=animal_view&animalid=" + controller.animal.ID;
            let share_image = asm.serviceurl + "?method=animal_image&animalid=" + controller.animal.ID;
            if (asm.smcom) { share_url += "&account=" + asm.useraccount; share_image += "&account=" + asm.useraccount; }
            let share_title = controller.animal.ANIMALNAME;
            let share_description = controller.animal.WEBSITEMEDIANOTES;
            
            let enc_share_url = "", enc_share_description = "", enc_share_image = "", enc_share_title = "";

            try {
                enc_share_url = encodeURIComponent(share_url);
                enc_share_description = encodeURIComponent(html.truncate(share_description, 113));
                enc_share_image = encodeURIComponent(share_image);
                enc_share_title = encodeURIComponent(share_title);
            }
            catch(e) {
                log.error("failed creating uri encoded share links", e);
            }

            if (config.bool("PublisherUseComments") || !share_description) {
                share_description = controller.animal.ANIMALCOMMENTS;
            }

            // Enable sharing according to sitedef
            $(".sharebutton").hide();
            $.each(controller.sharebutton.split(","), function(i, v) {
                $("#button-" + v).show();
            });

            // When a share button is clicked, mark it as such for the publishing history
            $("#button-share-body").on("click", "li", function() {
                let service = $(this).attr("id").replace("button-", "");
                common.ajax_post("animal", "mode=shared&id=" + controller.animal.ID + "&service=" + service);
            });

            // Web, picture and email
            $("#button-shareweb a").attr("href", share_url);
            $("#button-sharepic a").attr("href", share_image);
            $("#button-shareemail a").attr("href", "mailto:?body=" + enc_share_url);

            // Facebook
            $("#button-facebook a").attr("href", "https://facebook.com/sharer/sharer.php?" +
                "&u=" + enc_share_url);

            // Twitter
            $("#button-twitter a").attr("href", "https://twitter.com/share?" +
                "text=" + enc_share_description + 
                "&url=" + enc_share_url);

            // Google Plus
            $("#button-gplus a").attr("href", "https://plus.google.com/share?" +
                "&url=" + enc_share_url);

            // Pinterest
            $("#button-pinterest a").attr("href", "http://pinterest.com/pin/create/button/?" +
                "url=" + enc_share_url + 
                "&media=" + enc_share_image +
                "&description=" + enc_share_description);

            // Tumblr
            $("#button-tumblr a").attr("href", "http://www.tumblr.com/share/link?" +
                "url=" + enc_share_url +
                "&name=" + enc_share_title +
                "&description=" + enc_share_description);

        },

        /**
         * Bind widgets and control events
         */
        bind: function() {

            // Setup the document/social menu buttons
            $("#button-document, #button-share").asmmenu();

            $("#emailform").emailform();

            // If the option isn't set to allow non-alphanumeric
            // characters in microchip and tattoo numbers, use
            // the alphanumberbox widget.
            if (!config.bool("AllowNonANMicrochip")) {
                $("#microchipnumber").alphanumber();
                $("#microchipnumber2").alphanumber();
                $("#tattoonumber").alphanumber();
            }

            // Load the tab strip
            $(".asm-tabbar").asmtabs();

            // Changing the species updates the breed list
            $('#species').change(function() {
                animal.update_breed_list();
            });

            // Changing the location updates the unit autocomplete and clears the unit
            $("#location").change(function() {
                $("#unit").val("");
                animal.update_units();
            });

            // accordion
            $("#asm-details-accordion").accordion({
                heightStyle: "content"
            });

            // Keep breed2 in sync with breed1 for non-crossbreeds
            $("#breed1").change(function() {
                if (!$("#crossbreed").is(":checked")) {
                    $("#breed2").select("value", $("#breed1").select("value"));
                }
            });

            // If the microchip number changes, lookup the manufacturer and
            // display it
            $("#microchipnumber").change(animal.show_microchip_supplier);
            $("#microchipnumber2").change(animal.show_microchip_supplier);

            additional.relocate_fields();

            // If the animal type changes, or the date brought in, we may need to
            // generate a new code
            $("#animaltype").change(function() {
                if (config.bool("ManualCodes")) { 
                    return;
                }
                if (config.str("CodingFormat").indexOf("T") != -1 || 
                    config.str("ShortCodingFormat").indexOf("T") != -1) {
                    animal.generate_code();
                }
            });
            $("#datebroughtin").change(function() {
                if (config.bool("ManualCodes")) { 
                    return;
                }
                let dbin = $("#datebroughtin").datepicker("getDate"), today = new Date();
                if (config.str("CodingFormat").indexOf("M") != -1 ||
                    config.str("ShortCodingFormat").indexOf("M") != -1) {
                    // If the month is not this month, regenerate the code
                    if (dbin && dbin.getMonth() != today.getMonth()) {
                        animal.generate_code();
                    }
                }
                if (config.str("CodingFormat").indexOf("Y") != -1 ||
                    config.str("ShortCodingFormat").indexOf("Y") != -1) {
                    // If the year is not this year, regenerate the code
                    if (dbin && dbin.getYear() != today.getYear()) {
                        animal.generate_code();
                    }
                }
            });

            // Litter autocomplete
            $("#litterid").autocomplete({source: html.decode(controller.activelitters)});

            // If the bonded animals are cleared (or any animalchooser as part
            // of an additional field for that matter), dirty the form.
            $(".asm-animalchooser").animalchooser().bind("animalchoosercleared", function(event) {
                validate.dirty(true);
            });

            // Same goes for any of our person choosers
            $(".asm-personchooser").personchooser().bind("personchoosercleared", function(event) {
                validate.dirty(true);
            });

            // If a value is set in the previously blank deceased date, 
            // set the default death reason.
            // Another change event for this field handles visibility below
            $("#deceaseddate").change(function() {
                if ($("#deceaseddate").val() != "" && !controller.animal.DECEASEDDATE) {
                    $("#deathcategory").select("value", config.str("AFDefaultDeathReason"));
                }
            });

            // If the user just ticked hold, there's no hold until date and
            // we have an auto remove days period, default the date
            const hold_change = function() {
                if ($("#hold").is(":checked") && $("#holduntil").val() == "" && config.integer("AutoRemoveHoldDays") > 0) {
                    let holddate = format.date_js(controller.animal.DATEBROUGHTIN).getTime();
                    holddate += config.integer("AutoRemoveHoldDays") * 86400000;
                    holddate = format.date( new Date(holddate) );
                    $("#holduntil").val(holddate);
                }
            };
            $("#hold").click(hold_change).keyup(hold_change);

            // Controls that update the screen when changed
            $("#microchipped").change(animal.enable_widgets);
            $("#tattoo").change(animal.enable_widgets);
            $("#smarttag").change(animal.enable_widgets);
            $("#neutered").change(animal.enable_widgets);
            $("#fivltested").change(animal.enable_widgets);
            $("#heartwormtested").change(animal.enable_widgets);
            $("#deceaseddate").change(animal.enable_widgets);
            $("#healthproblems").change(animal.enable_widgets);
            $("#specialneeds").change(animal.enable_widgets);
            $("#entrytype").change(animal.enable_widgets);
            $("#transferin").change(animal.enable_widgets);
            $("#litterid").keyup(animal.enable_widgets);
            $("#microchipnumber").keyup(animal.enable_widgets);
            $("#microchipnumber2").keyup(animal.enable_widgets);
            $("#microchipdate").change(animal.enable_widgets);
            $("#microchipdate2").change(animal.enable_widgets);
            $("#pickedup").change(animal.enable_widgets);
            $("#crossbreed").change(animal.enable_widgets);
            $("#species").change(animal.enable_widgets);

            validate.save = async function(callback) {
                if (!animal.validation()) { header.hide_loading(); return; }
                validate.dirty(false);
                let formdata = "mode=save" +
                    "&id=" + controller.animal.ID + 
                    "&recordversion=" + controller.animal.RECORDVERSION + 
                    "&" + $("input, select, textarea").not(".chooser").toPOST();
                try {
                    let response = await common.ajax_post("animal", formdata);
                    callback(response);
                }
                catch(err) {
                    log.error(err, err);
                    validate.dirty(true); 
                }
            };

            // Toolbar buttons
            $("#button-save").button().click(function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload();
                });
            });

            $("#button-clone").button().click(async function() {
                await tableform.show_okcancel_dialog("#dialog-clone-confirm", _("Clone"));
                let formdata = "mode=clone&animalid=" + $("#animalid").val();
                header.show_loading(_("Cloning..."));
                let response = await common.ajax_post("animal", formdata);
                header.hide_loading();
                common.route("animal?id=" + response + "&cloned=true"); 
            });

            $("#button-merge").button().click(function() {
                let mb = {}; 
                mb[_("Merge")] = async function() { 
                    $("#dialog-merge").dialog("close");
                    let formdata = "mode=merge&animalid=" + $("#animalid").val() + "&mergeanimalid=" + $("#mergeanimal").val();
                    await common.ajax_post("animal", formdata);
                    validate.dirty(false);
                    common.route_reload(); 
                };
                mb[_("Cancel")] = function() { $(this).dialog("close"); };
                $("#dialog-merge").dialog({
                     width: 600,
                     resizable: false,
                     modal: true,
                     dialogClass: "dialogshadow",
                     show: dlgfx.delete_show,
                     hide: dlgfx.delete_hide,
                     buttons: mb
                });
            });

            $("#button-delete").button().click(async function() {
                await tableform.delete_dialog(null, _("This will permanently remove this animal, are you sure?"));
                let formdata = "mode=delete&animalid=" + $("#animalid").val();
                await common.ajax_post("animal", formdata);
                common.route("main");
            });

            $("#button-email").button().click(function() {
                let defaultemail = "", defaultname = "", toaddresses = [];
                // Use the future owner if the animal has a future adoption
                if (controller.animal && controller.animal.FUTUREOWNEREMAILADDRESS) {
                    defaultemail = controller.animal.FUTUREOWNEREMAILADDRESS;
                    defaultname = controller.animal.FUTUREOWNERNAME;
                } 
                // Use the latest reservation/person if the animal is on shelter/foster and a reserve is available
                else if (controller.animal && controller.animal.ARCHIVED == 0 && controller.animal.RESERVEDOWNEREMAILADDRESS) {
                    defaultemail = controller.animal.RESERVEDOWNEREMAILADDRESS;
                    defaultname = controller.animal.RESERVEDOWNERNAME;
                }
                // Otherwise person from the active movement
                else if (controller.animal && controller.animal.CURRENTOWNEREMAILADDRESS) {
                    defaultemail = controller.animal.CURRENTOWNEREMAILADDRESS;
                    defaultname = controller.animal.CURRENTOWNERNAME;
                }
                // Other useful addresses for the dialog
                if (controller.animal && controller.animal.FUTUREOWNEREMAILADDRESS) { 
                    toaddresses.push(controller.animal.FUTUREOWNEREMAILADDRESS);
                }
                if (controller.animal && controller.animal.RESERVEDOWNEREMAILADDRESS) { 
                    toaddresses.push(controller.animal.RESERVEDOWNEREMAILADDRESS);
                }
                if (controller.animal && controller.animal.CURRENTOWNEREMAILADDRESS) { 
                    toaddresses.push(controller.animal.CURRENTOWNEREMAILADDRESS);
                }
                if (controller.animal && controller.animal.CURRENTOWNEREMAILADDRESS2) { 
                    toaddresses.push(controller.animal.CURRENTOWNEREMAILADDRESS2);
                }
                if (controller.animal && controller.animal.CURRENTVETEMAILADDRESS) { 
                    toaddresses.push(controller.animal.CURRENTVETEMAILADDRESS);
                }
                if (controller.animal && controller.animal.ADOPTIONCOORDINATOREMAILADDRESS) {
                    toaddresses.push(controller.animal.ADOPTIONCOORDINATOREMAILADDRESS);
                }
                if (controller.animal && controller.animal.ORIGINALOWNEREMAILADDRESS) {
                    toaddresses.push(controller.animal.ORIGINALOWNEREMAILADDRESS);
                }
                if (controller.animal && controller.animal.BROUGHTINBYEMAILADDRESS) {
                    toaddresses.push(controller.animal.BROUGHTINBYEMAILADDRESS);
                }
                $("#emailform").emailform("show", {
                    title: _("Send email"),
                    post: "animal",
                    formdata: "mode=email&animalid=" + controller.animal.ID,
                    name: defaultname,
                    email: defaultemail,
                    toaddresses: toaddresses,
                    animalid: controller.animal.ID, 
                    subject: controller.animal.ANIMALNAME + " - " + controller.animal.CODE,
                    logtypes: controller.logtypes,
                    templates: controller.templatesemail
                });
            });

            $("#button-match").button().click(function() {
                common.route("lostfound_match?animalid=" + $("#animalid").val());
            });

            $("#button-newentry").button().click(async function() {
                let formdata = "mode=newentry&animalid=" + controller.animal.ID;
                let response = await common.ajax_post("animal", formdata);
                common.route("animal?id=" + controller.animal.ID + "&view=entryhistory", true);
            });

            $("#button-littermates").button().click(function() {
                common.route("animal_find_results?mode=ADVANCED&q=&filter=includedeceased&litterid=" + encodeURIComponent($("#litterid").val()));
            });

            // Inline buttons
            $("#button-gencode")
                .button({ icons: { primary: "ui-icon-refresh" }, text: false })
                .click(animal.generate_code);

            $("#button-microchipcheck")
                .button({ icons: { primary: "ui-icon-search" }, text: false })
                .click(function() { microchip.check($("#microchipnumber").val()); });

            $("#button-microchipcheck2")
                .button({ icons: { primary: "ui-icon-search" }, text: false })
                .click(function() { microchip.check($("#microchipnumber2").val()); });

            $("#button-randomname")
                .button({ icons: { primary: "ui-icon-tag" }, text: false })
                .click(async function() {
                    validate.dirty(false);
                    let formdata = "mode=randomname&sex=" + $("#sex").val();
                    let response = await common.ajax_post("animal", formdata);
                    $("#animalname").val(response);
                    validate.dirty(true);
                });

            $("#button-commentstomedia")
                .hide()
                .button({ icons: { primary: "ui-icon-arrow-1-ne" }, text: false })
                .click(async function() {
                    $("#button-commentstomedia").button("disable");
                    let formdata = "mode=webnotes&id=" + $("#animalid").val() + "&" + $("#comments").toPOST();
                    await common.ajax_post("animal", formdata);
                    $("#button-commentstomedia").button("enable");
                   header.show_info(_("Comments copied to web preferred media."));
                });

            $(".forgetlink").button({ icons: { primary: "ui-icon-trash" }, text: false })
                .click(async function() {
                    let t = $(this), service = $(this).attr("data-service");
                    await common.ajax_post("animal", "mode=forgetpublish&id=" + controller.animal.ID + "&service=" + service);
                    t.closest("p").fadeOut();
                });
            $(".deleteentryhistory").button({ icons: { primary: "ui-icon-trash" }, text: false })
                .click(async function() {
                    let t = $(this), aeid = $(this).attr("data-id");
                    await common.ajax_post("animal", "mode=deleteentryhistory&id=" + aeid);
                    t.closest("tr").fadeOut();
                });

        },

        sync: function() {

            // Load the data into the controls for the screen
            $("#asm-content input, #asm-content select, #asm-content textarea").fromJSON(controller.animal);

            // Update the breeds to match the species we just loaded and reload the breed values
            animal.update_breed_list();
            $("#breed1, #breed2").fromJSON(controller.animal);

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Load animal flags (note some will not be added if animal is not on shelter)
            html.animal_flag_options(controller.animal, controller.flags, $("#flags"));

            // Update the unit autocomplete to match the selected location
            animal.update_units();

            // Update on-screen fields from the data and display the screen
            animal.enable_widgets();
            animal.show_microchip_supplier();

            // Share button/links
            animal.set_sharinglinks();

            // Dirty handling
            validate.bind_dirty([ "animal_" ]);
            validate.indicator(["animalname", "dateofbirth", "datebroughtin" ]);

            // We can open on a particular slider
            if (controller.view && controller.view == "notes") {
                $("#asm-details-accordion").accordion("option", "active", 2);
            }
            if (controller.view && controller.view == "entry") {
                $("#asm-details-accordion").accordion("option", "active", 3);
            }
            if (controller.view && controller.view == "entryhistory") {
                $("#asm-details-accordion").accordion("option", "active", 4);
            }

            // If a popup warning has been set, display it
            animal.show_popup_warning();

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#dialog-merge");
            common.widget_destroy("#dialog-clone-confirm");
            common.widget_destroy("#dialog-popupwarning");
            common.widget_destroy("#mergeanimal", "animalchooser");
            common.widget_destroy("#bonded1", "animalchooser");
            common.widget_destroy("#bonded2", "animalchooser");
            common.widget_destroy("#owner", "personchooser");
            common.widget_destroy("#originalowner", "personchooser");
            common.widget_destroy("#broughtinby", "personchooser");
            common.widget_destroy("#neuteringvet", "personchooser");
            common.widget_destroy("#coordinator", "personchooser");
            common.widget_destroy("#pickedupby", "personchooser");
            common.widget_destroy("#currentvet", "personchooser");
            common.widget_destroy("#ownersvet", "personchooser");
            common.widget_destroy("#emailform");
        },

        name: "animal",
        animation: "formtab",
        autofocus: "#animalname", 
        title:  function() { return common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
            0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
            3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); },

        routes: {
            "animal": function() {
                common.module_loadandstart("animal", "animal?id=" + this.qs.id);
            }
        }

    };
    
    common.module_register(animal);

});
