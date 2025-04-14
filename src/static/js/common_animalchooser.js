/*global $, jQuery */
/*global asm, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

"use strict";

/**
 * Animal chooser widget. To create one, use a hidden input
 * with a class of asm-animalchooser
 *
 * <input id="animal" class="asm-animalchooser" data="boundfield" type="hidden" value="initialid" />
 *
 * callbacks: loaded (after loadbyid is complete)
 *            change (after user has clicked on a new selection)
 *            cleared (after user clicks the clear button)
 */
$.widget("asm.animalchooser", {

    selected: null,

    options: {
        id: 0,
        rec: {},
        additionalfields: [], 
        node: null,
        dialog: null,
        dialogadd: null,
        display: null,
        filter: "all", 
        nonshelter: false,
        addtitle: _("Add animal")
    },

    _create: function() {
        var h = [
            '<div class="animalchooser asm-chooser-container">',
            '<input class="animalchooser-oopostcode" type="hidden" value="" />',
            '<input class="animalchooser-bipostcode" type="hidden" value = "" />',
            '<table style="margin-left: 0px; margin-right: 0px; width: 100%; ">',
            '<tr>',
            '<td class="animalchooser-display">',
            '</td>',
            '<td valign="top" style="text-align: end; white-space: nowrap">',
            '<button class="animalchooser-link-find">' + _("Select an animal") + '</button>',
            '<button class="animalchooser-link-new">' + _("Add an animal") + '</button>',
            '<button class="animalchooser-link-clear">' + _("Clear") + '</button>',
            '</td>',
            '</tr>',
            '</table>',
            '<div class="animalchooser-find" style="display: none" title="' + html.title(_("Find animal")) + '">',
            '<input type="text" class="asm-textbox" />',
            '<button>' + _("Search") + '</button>',
            '<img class="animalchooser-spinner" style="height: 16px" src="static/images/wait/rolling_3a87cd.svg" />',
            '<table width="100%">',
            '<thead>',
                '<tr class="ui-widget-header">',
                    '<th></th>',
                    '<th>' + _("Name") + '</th>',
                    '<th>' + _("Code") + '</th>',
                    '<th>' + _("Microchip") + '</th>',
                    '<th>' + _("Type") + '</th>',
                    '<th>' + _("Species") + '</th>',
                    '<th>' + _("Breed") + '</th>',
                    '<th>' + _("Sex") + '</th>',
                '</tr>',
            '</thead>',
            '<tbody></tbody>',
            '</table>',
            '</div>',

            '<div class="animalchooser-add" style="display: none" title="' + this.options.addtitle + '">',
            '<table width="100%" class="addanimaltable">',
            '<tr>',
            '<td></td>', 
            '<td><input data="nonshelter" type="checkbox" class="asm-checkbox enablecheck nonshelter" /><label>' + _("Non-Shelter") + '</label></td>',
            '</tr>',
            '<tr class="holdrow">',
            '<td></td>', 
            '<td><input data="hold" type="checkbox" class="asm-checkbox enablecheck hold" /><label>' + _("Hold until") + '</label> ', 
            '<input id="holduntil" data="holduntil" type="text" class="asm-textbox asm-datebox holduntil" /></td>',
            '</tr>',
            '<tr class="ownerrow">', 
            '<td>' + _("Owner") + '</td>', 
            '<td><input type="hidden"  class="asm-field asm-personchooser" class="owner" data="nsowner" /></td>', 
            '</tr>', 
            '<tr>',
            '<td><label>' + _("Name") + '</label><span class="asm-has-validation">*</span></td>', 
            '<td><input data="animalname" type="text" class="asm-textbox" /></td>',
            '</tr>', 
            '<tr>',
            '<td><label>' + _("Sex") + '</label></td>', 
            '<td><select data="sex" class="asm-selectbox chooser sexes" /></select></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Type") + '</label></td>', 
            '<td><select data="animaltype" class="asm-selectbox chooser animaltypes" /></select></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Color") + '</label></td>', 
            '<td><select data=basecolour class="asm-selectbox chooser colours" /></select></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Size") + '</label></td>', 
            '<td><select data="size" class="asm-selectbox chooser sizes" /></select></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Species") + '</label></td>', 
            '<td><select data="species" class="asm-selectbox chooser species" /></select></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Breed") + '</label></td>', 
            '<td><select data="breed1" class="asm-selectbox chooser breeds" /></select></td>',
            '</tr>',
            '<tr>', 
            '<td><label>' + _("Date of Birth") + '</label><span class="asm-has-validation">*</span></td>', 
            '<td><input data="dateofbirth" type="text" class="asm-textbox asm-datebox" /></td>',
            '</tr>',
            '<tr class="entrytypesrow">',
            '<td><label>' + _("Entry Type") + '</label></td>', 
            '<td><select data="entrytype" class="asm-selectbox chooser entrytypes" /></select></td>',
            '</tr>',
            '<tr class="entryreasonsrow">',
            '<td><label>' + _("Entry Reason") + '</label></td>', 
            '<td><select data="entryreason" class="asm-selectbox chooser entryreasons" /></select></td>',
            '</tr>',
            '<tr class="datebroughtinrow">', 
            '<td><label>' + _("Date Brought In") + '</label></td>', 
            '<td><input id="datebroughtin" data="datebroughtin" type="text" class="asm-textbox asm-datebox datebroughtin" /></td>',
            '</tr>',
            '<tr>',
            '<td><label>' + _("Description") + '</label></td>', 
            '<td><textarea class="asm-textareafixed chooser personchooser-address" data="comments" rows="3"></textarea></td>',
            '</tr>',
            '</table>',
            '</div>',
            '</div>'
        ].join("\n");
        var node = $(h);
        var self = this;
        this.options.node = node;
        var dialog = node.find(".animalchooser-find");
        var dialogadd = node.find(".animalchooser-add");
        this.options.dialog = dialog;
        this.options.dialogadd = dialogadd;
        this.options.display = node.find(".animalchooser-display");
        this.element.parent().append(node);
        // Set the filter
        if (this.element.attr("data-filter")) { 
            this.options.filter = this.element.attr("data-filter");
        }
        // Look for nonshelter flag
        if (this.element.attr("data-nonshelter") == "true" ) { 
            this.options.nonshelter = true;
        }
        // Create the dialog
        var acbuttons = {};
        acbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        dialog.dialog({
            autoOpen: false,
            height: common.vheight(600),
            width: common.vwidth(800),
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: acbuttons
        });
        let acaddbuttons = {};
        acaddbuttons[_("Create this animal")] = function() {
            let valid = true, dialogadd = self.options.dialogadd;
            // Validate fields that can't be blank
            dialogadd.find("label").removeClass(validate.ERROR_LABEL_CLASS);
            dialogadd.find("input[data='animalname']").each(function() {
                if (common.trim($(this).val()) == "") {
                    $(this).parent().parent().find("label").addClass(validate.ERROR_LABEL_CLASS);
                    $(this).focus();
                    valid = false;
                    return false;
                }
            });
            dialogadd.find("input[data='dob']").each(function() {
                if (common.trim($(this).val()) == "") {
                    $(this).parent().parent().find("label").addClass(validate.ERROR_LABEL_CLASS);
                    $(this).focus();
                    valid = false;
                    return false;
                }
            });
            if (!valid) { return; }
            if (!additional.validate_mandatory_node(dialogadd)) { return; }
            // Disable the dialog buttons before we make any ajax requests
            dialogadd.disable_dialog_buttons();
            self.add_animal();
        };
        acaddbuttons[_("Cancel")] = function() {
            $(this).dialog("close");
        };
        dialogadd.dialog({
            autoOpen: false,
            width: 600,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.add_show,
            hide: dlgfx.add_hide,
            buttons: acaddbuttons,
            open: function() {
                // Set non-shelter
                dialogadd.find(".nonshelter").prop("checked", self.options.nonshelter);
                dialogadd.find(".nonshelter").change();
                // Change sex to unknown
                dialogadd.find(".sexes").val(2);
                // Change animal type to default
                dialogadd.find(".animaltypes").val(config.str("AFDefaultType"));
                // Change colour to default
                dialogadd.find(".colours").val(config.str("AFDefaultColour"));
                // Change size to default
                dialogadd.find(".sizes").val(config.str("AFDefaultSize"));
                // Change species to default
                dialogadd.find(".species").val(config.str("AFDefaultSpecies"));
                // Change breed to default
                dialogadd.find(".breeds").val(config.str("AFDefaultBreed"));
                // Change entry type to default
                dialogadd.find(".entrytypes").val(config.str("AFDefaultEntryType"));
                // Change entry reason to default
                dialogadd.find(".entryreasons").val(config.str("AFDefaultEntryReason"));
                // Setting date brought in today
                dialogadd.find(".datebroughtin").val(format.date(new Date()));
                // Change additional fields to default
                additional.reset_default(self.options.additionalfields);
                // If we have a filter, set the appropriate animal flags to match
                if (self.options.filter) {
                    dialogadd.find(".animalchooser-flags option[value='" + self.options.filter + "']").prop("selected", true);
                    dialogadd.find(".animalchooser-flags").change();
                }
            }, 
            close: function() {
                dialogadd.find("input, textarea").val("");
                dialogadd.find("label").removeClass(validate.ERROR_LABEL_CLASS);
                dialogadd.enable_dialog_buttons();
            }
        });

        // Create any form controls based on classes used
        // Choosers are initialised first as they inject more widgets into the DOM that will need initialising
        $(".asm-animalchooser").animalchooser();
        $(".asm-animalchoosermulti").animalchoosermulti();
        $(".asm-personchooser").personchooser();
        $(".asm-callout").callout();
        $(".asm-datebox").date();
        $(".asm-alphanumberbox").alphanumber();
        $(".asm-autotext").autotext();
        $(".asm-numberbox").number();

        dialog.find("table").table({ sticky_header: false });
        dialog.find("input").keydown(function(event) { if (event.keyCode == 13) { self.find(); return false; }});
        dialog.find("button").button().click(function() { self.find(); });
        dialog.find(".animalchooser-spinner").hide();

        dialogadd.find(".nonshelter").change(function() {
            dialogadd.find(".datebroughtin").val(format.date(new Date()));
            if (dialogadd.find(".nonshelter").is(":checked")) {
                dialogadd.find(".animaltypes").val(config.str("AFNonShelterType"));
                dialogadd.find(".entrytypesrow").hide();
                dialogadd.find(".entryreasonsrow").hide();
                dialogadd.find(".datebroughtinrow").hide();
                dialogadd.find(".holdrow").hide();
                dialogadd.find(".ownerrow").show();
            } else {
                dialogadd.find(".animaltypes").val(config.str("AFDefaultType"));
                dialogadd.find(".entrytypesrow").show();
                dialogadd.find(".entryreasonsrow").show();
                dialogadd.find(".datebroughtinrow").show();
                dialogadd.find(".holdrow").show();
                dialogadd.find(".ownerrow").hide();
            }
        });
        
        
        
        // Bind the find button
        node.find(".animalchooser-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                dialog.dialog("open");
            });
        
        node.find(".animalchooser-link-new")
            .button({ icons: { primary: "ui-icon-plus" }, text: false })
            .click(function() {
                dialogadd.dialog("open");
        });

        // Bind the clear button
        node.find(".animalchooser-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear(true);
            });

        /// Go to the backend to get the additional fields with lookup data
        $.ajax({
            type: "GET",
            url:  "animal_embed",
            cache: true, // this data can be cached for a few minutes
            data: { mode: "lookup" },
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let d = jQuery.parseJSON(data);
                self.options.additionalfields = d.additional;
                self.options.sexes = d.sexes;
                self.options.animaltypes = d.animaltypes;
                self.options.colours = d.colours;
                self.options.sizes = d.sizes;
                self.options.species = d.species;
                self.options.breeds = d.breeds;
                self.options.entrytypes = d.entrytypes;
                self.options.entryreasons = d.entryreasons;

                dialogadd.find(".sexes").html(html.list_to_options(self.options.sexes, "ID", "SEX"));
                dialogadd.find(".animaltypes").html(html.list_to_options(self.options.animaltypes, "ID", "ANIMALTYPE"));
                dialogadd.find(".colours").html(html.list_to_options(self.options.colours, "ID", "BASECOLOUR"));
                dialogadd.find(".sizes").html(html.list_to_options(self.options.sizes, "ID", "SIZE"));
                dialogadd.find(".species").html(html.list_to_options(self.options.species, "ID", "SPECIESNAME"));
                dialogadd.find(".breeds").html(html.list_to_options(self.options.breeds, "ID", "BREEDNAME"));
                dialogadd.find(".entrytypes").html(html.list_to_options(self.options.entrytypes, "ID", "ENTRYTYPENAME"));
                dialogadd.find(".entryreasons").html(html.list_to_options(self.options.entryreasons, "ID", "REASONNAME"));
                dialogadd.find(".addanimaltable").append(additional.additional_new_fields(self.options.additionalfields, false, "additional chooser"));

                // Was there a value already set by the markup? If so, use it
                if (self.element.val() != "" && self.element.val() != "0") {
                    self.loadbyid(self.element.val());
                }
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },

    /**
     * Empties the widget
     */
    clear: function(fireclearedevent) {
        this.selected = null;
        this.element.val("0");
        this.options.id = 0;
        this.options.rec = {};
        this.options.display.html("");
        if (fireclearedevent) { this._trigger("cleared", null); }
    },

    is_empty: function() {
        return this.selected == null;
    },

    destroy: function() {
        try {
            this.options.dialog.dialog("destroy");
        } catch (ex) {}
    },

    /**
     * Loads an animal into the widget by ID
     */
    loadbyid: function(animalid) {
        if (!animalid || animalid == "0" || animalid == "") { return; }
        this.clear();
        this.element.val(animalid);
        var self = this;
        var formdata = "mode=id&id=" + animalid;
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                var h = "";
                var animal = jQuery.parseJSON(data);
                var rec = animal[0];
                var disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
                self.element.val(rec.ID);
                self.options.rec = rec;
                self.options.display.html(disp);
                self._trigger("loaded", null, rec);
                self.selected = rec;
                common.inject_target();
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },

    find: function() {
        let self = this;
        let dialog = this.options.dialog, node = this.options.node;
        dialog.find(".animalchooser-spinner").show();
        dialog.find("button").button("disable");
        let formdata = {
            "mode":     "find",
            "filter":   this.options.filter, 
            "q":        dialog.find("input").val()
        };
        common.ajax_post("animal_embed", formdata, 
            function(data) {
                var h = "";
                var animal = jQuery.parseJSON(data);
                // Create the table content from the results
                $.each(animal, function(i, a) {
                    h += "<tr>";
                    //h += "<td>" + html.animal_emblems(a, {showlocation: true}) + "</td>";
                    h += "<td><a href=\"#\" data=\"" + i + "\">" + html.animal_thumb(a, { style: "cursor: pointer;" }) + "</a></td>";
                    h += "<td><a href=\"#\" data=\"" + i + "\">" + a.ANIMALNAME + "</a><br>" + html.animal_emblems(a, {showlocation: true}) + "</td>";
                    h += "<td>" + a.CODE + "</td>";
                    h += "<td>" + a.IDENTICHIPNUMBER + "</td>";
                    h += "<td>" + a.ANIMALTYPENAME + "</td>";
                    h += "<td>" + a.SPECIESNAME + "</td>";
                    h += "<td>" + a.BREEDNAME + "</td>";
                    h += "<td>" + a.SEXNAME + "</td>";
                    h += "</tr>";
                });
                dialog.find("table > tbody").html(h);
                // Remove any existing events from previous searches
                dialog.off("click", "a");
                // Use delegation to bind to the name column and select
                // the animal once clicked. Triggers the change callback
                dialog.on("click", "a", function(e) {
                    let rec = animal[$(this).attr("data")];
                    dialog.dialog("close");
                    // Retrieve the full selected record, since the resultset only
                    // contains brief records.
                    common.ajax_post("animal_embed", "mode=id&id=" + rec.ID, function(data) {
                        let rec = jQuery.parseJSON(data)[0];
                        self.element.val(rec.ID);
                        self.options.rec = rec;
                        var disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
                        self.options.display.html(disp);
                        node.find(".animalchooser-oopostcode").val(rec.ORIGINALOWNERPOSTCODE);
                        node.find(".animalchooser-bipostcode").val(rec.BROUGHTINBYOWNERPOSTCODE);
                        try { validate.dirty(true); } catch(ex) { }
                        self._trigger("change", null, rec);
                        self.selected = rec;
                        common.inject_target();
                    });
                    return false;
                });
                // Force the table to update itself and remove the spinner
                dialog.find("table").trigger("update");
                dialog.find(".animalchooser-spinner").hide();
                dialog.find("button").button("enable");
            },
            function(jqxhr, textstatus, response) {
                dialog.dialog("close");
                log.error(response);
                dialog.find(".animalchooser-spinner").hide();
                dialog.find("button").button("enable");
            });
    },

    get_selected: function() {
        return this.selected;
    }, 

    /**
     * Posts the add dialog to the backend to create the animal
     */
    add_animal: function() {
        let self = this, dialogadd = this.options.dialogadd, display = this.options.display, node = this.options.node;
        let formdata = "mode=add&" + dialogadd.find("input, textarea, select").toPOST();
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(result) {
                let animal = jQuery.parseJSON(result);
                let rec = animal[0];
                self.element.val(rec.ID);
                self.selected = rec;
                let disp = "<span class=\"justlink\"><a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.SHELTERCODE + " " + rec.ANIMALNAME + "</a></span>";
                display.html(disp);
                try { 
                    validate.dirty(true); 
                } 
                catch(ev) { }
                dialogadd.dialog("close");
                common.inject_target();
                self._trigger("change", null, rec);
            },
            error: function(jqxhr, textstatus, response) {
                dialogadd.dialog("close");
                log.error(response);
            }
        });
    },

});

