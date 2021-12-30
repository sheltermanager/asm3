/*global $, console, jQuery */
/*global asm, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

"use strict";

/**
 * Multiple animal chooser widget. To create one, use a hidden input
 * with a class of asm-animalchoosermulti
 *
 * <input id="animal" class="asm-animalchoosermulti" data="boundfield" type="hidden" value="commaseparatedids" />
 *
 * callbacks: select (after selectbyids is complete)
 *            change (after user has clicked select button)
 */
$.widget("asm.animalchoosermulti", {

    options: {
        ids: "",
        rows: [],
        node: null,
        dialog: null,
        display: null,
        results: null,
        locations: null,
        species: null,
        litters: null,
        loaded: false
    },

    _create: function() {

        var h = [
            '<div class="animalchoosermulti">',
            '<table style="margin-left: 0px; margin-right: 0px; width: 100%">',
            '<tr>',
            '<td class="animalchoosermulti-display">',
            '</td>',
            '<td valign="top" align="right">',
            '<button type="button" class="animalchoosermulti-link-find">' + _("Select animals") + '</button>',
            '<button type="button" class="animalchoosermulti-link-clear">' + _("Clear") + '</button>',
            '</td>',
            '</tr>',
            '</table>',
            '<div class="animalchoosermulti-find" title="' + html.title(_("Select animals")) + '">',
            '<div class="totalselected">',
            html.info(_("{0} selected").replace("{0}", "0")),
            '</div>',
            '<img style="height: 16px" class="spinner" src="static/images/wait/rolling_3a87cd.svg" />',
            '<div style="border-bottom: 1px solid #aaa; width: 100%">',
            '<div class="asm-animalchoosermulti-filter">',
            '<a href="#" class="animalchoosermulti-selectall" title="Select all"><span class="ui-icon ui-icon-check"></span></a>',
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Locations") + ': <select multiple="multiple" class="animalchoosermulti-locations asm-bsmselect"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Species") + ': <select multiple="multiple" class="animalchoosermulti-species asm-bsmselect"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Litters") + ': <select multiple="multiple" class="animalchoosermulti-litters asm-bsmselect"></select>', 
            '</div>',
            '</div>',
            '<div class="animalchoosermulti-results">',
            '</div>',
            '</div>', 
            '</div>'
        ].join("\n");

        let node = $(h);
        let self = this;

        this.options.node = node;
        let dialog = node.find(".animalchoosermulti-find");
        this.options.dialog = dialog;

        this.options.display = node.find(".animalchoosermulti-display");
        this.options.locations = node.find(".animalchoosermulti-locations");
        this.options.species = node.find(".animalchoosermulti-species");
        this.options.litters = node.find(".animalchoosermulti-litters");
        this.options.results = node.find(".animalchoosermulti-results");
        this.element.parent().append(node);

        // Create the dialog
        var acbuttons = {};
        acbuttons[_("Select")] = function() { self.select(); };
        acbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        dialog.dialog({
            autoOpen: false,
            height: 600,
            width: 800,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: acbuttons,
            open: function() {
                // Load animal thumbs when opening the dialog if they
                // haven't been loaded yet
                if (!self.options.loaded) {
                    self.load();
                    self.options.loaded = true;
                }
            }
        });

        dialog.find("img").hide();

        // Bind the find button
        node.find(".animalchoosermulti-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                dialog.dialog("open");
            });

        // Bind the clear button
        node.find(".animalchoosermulti-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear();
            });
    },

    /**
     * Empties the widget
     */
    clear: function() {
        this.element.val("");
        this.options.ids = "";
        this.options.display.html("");
        this.options.results.find(":checked").prop("checked", false);
        this.update_status();
    },

    is_empty: function() {
        return this.options.ids == "";
    },

    destroy: function() {
        try {
            this.options.dialog.dialog("destroy"); 
        }
        catch (ex) {}
    },

    /**
     * Returns the animal row with ID aid
     */
    get_row: function(aid) {
        var rv;
        $.each(this.rows, function(i, v) {
            if (v.ID == aid) {
                rv = v;
            }
        });
        return rv;
    },

    /**
     * Returns true if a row has idval in column fname
     */
    id_used: function(fname, idval) {
        var rv = false;
        $.each(this.rows, function(i, a) {
            if (a[fname] == idval) {
                rv = true;
            }
        });
        return rv;
    },

    /**
     * Converts the selected items into a list of ids, sets it as the
     * element value and puts links in the display area
     */
    select: function() {
        var self = this, dialog = this.options.dialog, results = this.options.results, display = this.options.display, selval = [];
        display.html("");
        results.find(":checked").each(function() {
            var aid = $(this).attr("data"), rec = self.get_row(aid);
            selval.push(aid);
            var disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
            display.append(disp);
            display.append("<br />");
        });
        self.element.val(selval.join(","));
        self._trigger("change", null, self.element.val());
        dialog.dialog("close");
    },

    /**
     * Update the visible list of animals according to what's selected in the filters
     */
    update_filters: function() {
        let results = this.options.results, locations = this.options.locations, 
            species = this.options.species, litters = this.options.litters, 
            dialog = this.options.dialog;
        $.each(this.rows, function(i, a) {
            let show = true;
            let selspecies = String(species.val()).trim().split(",");
            if ( String(species.val()).trim() && selspecies.indexOf(String(a.SPECIESID)) == -1 ) { show = false; }
            let selloc = String(locations.val()).trim().split(",");
            if ( String(locations.val()).trim() ) {
                if (a.ACTIVEMOVEMENTTYPE == 1 && selloc.indexOf("m1") == -1) { show = false; }
                if (a.ACTIVEMOVEMENTTYPE == 2 && selloc.indexOf("m2") == -1) { show = false; }
                if (a.ACTIVEMOVEMENTTYPE == 8 && selloc.indexOf("m8") == -1) { show = false; }
                if (!a.ACTIVEMOVEMENTTYPE && selloc.indexOf(String(a.SHELTERLOCATION)) == -1) { show = false; }
            }
            let sellitter = String(litters.val()).trim().split(",");
            if ( String(litters.val()).trim() && sellitter.length > 0 && sellitter.indexOf(a.ACCEPTANCENUMBER) == -1) { show = false; }
            // Show/hide the result appropriately
            dialog.find(".animalselect[data='" + a.ID + "']").closest(".asm-animalchoosermulti-result").toggle(show);
        });
    },

    /**
     * Updates the info strip at the top to show how many animals selected
     */
    update_status: function() {
        var c = this.options.results.find(":checked").length;
        this.options.dialog.find(".totalselected").html(html.info(_("{0} selected").replace("{0}", c)));
        this.options.results.find(".asm-animalchoosermulti-selected").removeClass("asm-animalchoosermulti-selected").removeClass("ui-state-highlight");
        this.options.results.find(":checked").each(function() {
            var tn = $(this);
            tn.closest(".asm-animalchoosermulti-result").addClass("asm-animalchoosermulti-selected").addClass("ui-state-highlight");
        });
    },

    /**
     * Selects animals based on a comma separated list of ids as a string
     */
    selectbyids: function(animalids) {
        this.clear();
        var self = this;
        var results = this.options.results;
        if (!animalids) { return; }
        $.each(animalids.split(","), function(i, v) {
            results.find("data=['" + v + "']").prop("checked", true);
        });
        self.update_status();
        self._trigger("change", null, animalids);
    },

    /**
     * Turns a user's litter ID into an escaped version for putting
     * in a data attribute
     */
    litterid_escape: function(s) {
        s = common.replace_all(s, " ", "_"); 
        s = common.replace_all(s, "'", "_"); 
        s = common.replace_all(s, "\"", "_"); 
        return s;
    },

    load: function() {
        var self = this;
        var dialog = this.options.dialog, node = this.options.node, results = this.options.results, 
            locations = this.options.locations, species = this.options.species, litters = this.options.litters;
        dialog.find("img").show();
        var formdata = "mode=multiselect";
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {

                var h = "";
                var rv = jQuery.parseJSON(data);
                self.rows = rv.rows;

                // Update the list of locations
                let ll = [];
                ll.push(html.list_to_options(rv.locations, "ID", "LOCATIONNAME"));
                ll.push('<option value="m1">' + _("Trial Adoption") + '</option>');
                ll.push('<option value="m2">' + _("Foster") + '</option>');
                ll.push('<option value="m8">' + _("Retailer") + '</option>');
                locations.html( ll.join("\n") );
                locations.change();
                locations.on("change", function(e) {
                    self.update_filters();
                });

                // Species list
                species.html( html.list_to_options(rv.species, "ID", "SPECIESNAME") );
                species.change();
                species.on("change", function(e) {
                    self.update_filters();
                });

                // Litters list
                let lh = [];
                $.each(rv.litters, function(i, l) {
                    lh.push('<option value="' + html.title(l.ACCEPTANCENUMBER) + '">' + common.nulltostr(l.MOTHERCODE) + ' ' + 
                        common.nulltostr(l.MOTHERNAME) + ' ' + l.ACCEPTANCENUMBER + ' - ' + l.SPECIESNAME + '</option>');
                });
                litters.html( lh.join("\n") );
                litters.change();
                litters.on("change", function(e) {
                    self.update_filters();
                });

                // Load the list of animals
                $.each(self.rows, function(i, a) {
                    results.append( '<div class="asm-animalchoosermulti-result">' + 
                        html.animal_link_thumb(a, { showselector: true, showunit: true, showlocation: true }) +
                    '</div>' );
                });

                // Delegate event handler for the checkboxes
                results.off("click", "input[type='checkbox']");
                results.on("click", "input[type='checkbox']", function(e) { 
                    self.update_status();
                });

                // Remove the spinner
                dialog.find(".spinner").hide();

                // Select all toggle
                dialog.find(".animalchoosermulti-selectall").click(function(e) {
                    if (!self.select_all_toggle) {
                        self.select_all_toggle = true;
                        dialog.find(".animalselect:visible").prop("checked", true);
                        self.update_status();
                    }
                    else {
                        self.select_all_toggle = false;
                        dialog.find(".animalselect").prop("checked", false);
                        self.update_status();
                    }
                    return false;
                });

                // Was there a value already set by the markup? If so, use it
                if (self.element.val() != "") {
                    self.selectbyids(self.element.val());
                    self._trigger("select", null, self.element.val());
                }

            },
            error: function(jqxhr, textstatus, response) {
                dialog.dialog("close");
                dialog.find(".spinner").hide();
                log.error(response);
            }
        });
    }
});
