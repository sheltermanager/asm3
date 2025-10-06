/*global $, console, jQuery */
/*global asm, asm_widget, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

"use strict";

/**
 * Multiple animal chooser widget. To create one, use a hidden input
 * with a class of asm-animalchoosermulti for bind_widgets to autoload
 *
 * <input id="animal" class="asm-animalchoosermulti" data="boundfield" type="hidden" value="commaseparatedids" />
 * 
 * $(".asm-animalchoosermulti").animalchoosermulti(); // (bind_widgets does this automatically)
 *
 * events: select (after selectbyids is complete)
 *         change (after user has clicked select button)
 */
$.fn.animalchoosermulti = asm_widget({

    _create: function(t) {
        
        let self = this;

        let h = [
            '<div class="animalchoosermulti asm-chooser-container">',
            '<table style="margin-left: 0px; margin-right: 0px; width: 100%; ">',
            '<tr>',
            '<td class="animalchoosermulti-display">',
            '</td>',
            '<td valign="top" style="text-align: end; white-space: nowrap">',
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
             _("Locations") + ': <select multiple="multiple" title="' + _("Filter") + '" class="animalchoosermulti-locations asm-selectmulti"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Species") + ': <select multiple="multiple" title="' + _("Filter") + '" class="animalchoosermulti-species asm-selectmulti"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Litters") + ': <select multiple="multiple" title="' + _("Filter") + '" class="animalchoosermulti-litters asm-selectmulti"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Age Groups") + ': <select multiple="multiple" title="' + _("Filter") + '" class="animalchoosermulti-agegroups asm-selectmulti"></select>', 
            '</div>',
            '<div class="asm-animalchoosermulti-filter">',
             _("Flags") + ': <select multiple="multiple" title="' + _("Filter") + '" class="animalchoosermulti-flags asm-selectmulti"></select>', 
            '</div>',
            '</div>',
            '<div class="animalchoosermulti-results">',
            '</div>',
            '</div>', 
            '</div>'
        ].join("\n");

        let node = $(h);

        let o = {};
        t.data("o", o);
        o.node = node;
        o.dialog = node.find(".animalchoosermulti-find");
        o.display = node.find(".animalchoosermulti-display");
        o.locations = node.find(".animalchoosermulti-locations");
        o.species = node.find(".animalchoosermulti-species");
        o.litters = node.find(".animalchoosermulti-litters");
        o.flags = node.find(".animalchoosermulti-flags");
        o.agegroups = node.find(".animalchoosermulti-agegroups");
        o.results = node.find(".animalchoosermulti-results");
        o.loaded = false;

        t.parent().append(node);

        // Create the dialog
        let acbuttons = {};
        acbuttons[_("Select")] = function() { self.select.call(self, t); };
        acbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        o.dialog.dialog({
            autoOpen: false,
            height: common.vheight(600),
            width: common.vwidth(875),
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: acbuttons,
            open: function() {
                // Load animal thumbs when opening the dialog if they
                // haven't been loaded yet
                if (!o.loaded) {
                    self.load.call(self, t);
                    o.loaded = true;
                }
            }
        });

        o.dialog.find("img").hide();

        // Bind the find button
        node.find(".animalchoosermulti-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                o.dialog.dialog("open");
            });

        // Bind the clear button
        node.find(".animalchoosermulti-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear.call(self, t);
            });
    },

    /**
     * Empties the widget
     */
    clear: function(t) {
        t.val("");
        let o = t.data("o");
        o.display.html("");
        o.results.find(":checked").prop("checked", false);
        this.update_status(t);
    },

    is_empty: function(t) {
        let o = t.data("o");
        return o.results.find(":checked").length == 0;
    },

    destroy: function(t) {
        try {
            let o = t.data("o");
            o.dialog.empty();
            o.dialog.dialog("destroy"); 
        }
        catch (ex) {}
    },

    /**
     * Returns the animal row with ID aid
     */
    get_row: function(t, aid) {
        let rv, o = t.data("o");
        $.each(o.rows, function(i, v) {
            if (v.ID == aid) {
                rv = v;
            }
        });
        return rv;
    },

    /**
     * Returns true if a row has idval in column fname
     */
    id_used: function(t, fname, idval) {
        let rv = false, o = t.data("o");
        $.each(o.rows, function(i, a) {
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
    select: function(t) {
        let self = this, o = t.data("o"), selval = [];
        o.display.html("");
        o.results.find(":checked").each(function() {
            let aid = $(this).attr("data"), rec = self.get_row(t, aid);
            selval.push(aid);
            let disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
            o.display.append(disp);
            o.display.append("<br />");
        });
        t.val(selval.join(","));
        t.trigger("change", [ t.val() ]);
        o.dialog.dialog("close");
    },

    /**
     * Update the visible list of animals according to what's selected in the filters
     */
    update_filters: function(t) {
        let o = t.data("o");
        $.each(o.rows, function(i, a) {
            let show = true;
            let selspecies = String(o.species.val()).trim().split(",");
            if ( String(o.species.val()).trim() && selspecies.indexOf(String(a.SPECIESID)) == -1 ) { show = false; }
            let selloc = String(o.locations.val()).trim().split(",");
            if ( String(o.locations.val()).trim() ) {
                if (a.ACTIVEMOVEMENTTYPE == 1 && selloc.indexOf("m1") == -1) { show = false; }
                if (a.ACTIVEMOVEMENTTYPE == 2 && selloc.indexOf("m2") == -1) { show = false; }
                if (a.ACTIVEMOVEMENTTYPE == 8 && selloc.indexOf("m8") == -1) { show = false; }
                if (!a.ACTIVEMOVEMENTTYPE && selloc.indexOf(String(a.SHELTERLOCATION)) == -1) { show = false; }
            }
            let sellitter = String(o.litters.val()).trim().split(",");
            if ( String(o.litters.val()).trim() && sellitter.length > 0 && sellitter.indexOf(a.ACCEPTANCENUMBER) == -1) { show = false; }
            let selflag = String(o.flags.val()).trim().split(",");
            if (String(o.flags.val()).trim() && selflag.length > 0 && !common.array_overlap(selflag, a.ADDITIONALFLAGS.split("|"))) { show = false; }
            let selagegroup = String(o.agegroups.val()).trim().split(",");
            if (String(o.agegroups.val()).trim() && selagegroup.length > 0 && selagegroup.indexOf(a.AGEGROUP) == -1) { show = false; }

            // Show/hide the result appropriately
            o.dialog.find(".animalselect[data='" + a.ID + "']").closest(".asm-animalchoosermulti-result").toggle(show);
        });
    },

    /**
     * Updates the info strip at the top to show how many animals selected
     */
    update_status: function(t) {
        let o = t.data("o");
        let c = o.results.find(":checked").length;
        o.dialog.find(".totalselected").html(html.info(_("{0} selected").replace("{0}", c)));
        o.results.find(".asm-animalchoosermulti-selected").removeClass("asm-animalchoosermulti-selected").removeClass("ui-state-highlight");
        o.results.find(":checked").each(function() {
            let tn = $(this);
            tn.closest(".asm-animalchoosermulti-result").addClass("asm-animalchoosermulti-selected").addClass("ui-state-highlight");
        });
    },

    /**
     * Selects animals based on a comma separated list of ids as a string
     */
    selectbyids: function(t, animalids) {
        let self = this, o = t.data("o");
        self.clear.call(self, t);
        if (!animalids) { return; }
        $.each(animalids.split(","), function(i, v) {
            o.results.find("data=['" + v + "']").prop("checked", true);
        });
        self.update_status(t);
        t.trigger("change", [animalids] );
    },

    load: function(t) {
        let self = this, o = t.data("o");
        o.dialog.find("img").show();
        let formdata = "mode=multiselect";
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {

                let rv = jQuery.parseJSON(data);
                o.rows = rv.rows;

                // Update the list of locations
                let ll = [];
                ll.push(html.list_to_options(rv.locations, "ID", "LOCATIONNAME"));
                ll.push('<option value="m1">' + _("Trial Adoption") + '</option>');
                ll.push('<option value="m2">' + _("Foster") + '</option>');
                ll.push('<option value="m8">' + _("Retailer") + '</option>');
                o.locations.html( ll.join("\n") );
                o.locations.change();
                o.locations.on("change", function(e) {
                    self.update_filters(t);
                });

                // Species list
                o.species.html( html.list_to_options(rv.species, "ID", "SPECIESNAME") );
                o.species.change();
                o.species.on("change", function(e) {
                    self.update_filters(t);
                });

                // Litters list
                let lh = [];
                $.each(rv.litters, function(i, l) {
                    lh.push('<option value="' + html.title(l.ACCEPTANCENUMBER) + '">' + common.nulltostr(l.MOTHERCODE) + ' ' + 
                        common.nulltostr(l.MOTHERNAME) + ' ' + l.ACCEPTANCENUMBER + ' - ' + l.SPECIESNAME + '</option>');
                });
                o.litters.html( lh.join("\n") );
                o.litters.change();
                o.litters.on("change", function(e) {
                    self.update_filters(t);
                });

                // Flags list
                html.animal_flag_options(null, rv.flags, o.flags);
                //flags.html( html.list_to_options(rv.flags, "FLAG", "FLAG") );
                o.flags.change();
                o.flags.on("change", function(e) {
                    self.update_filters(t);
                });

                // Age groups list
                o.agegroups.html( html.list_to_options(rv.agegroups));
                o.agegroups.change();
                o.agegroups.on("change", function(e) {
                    self.update_filters(t);
                });

                // Load the list of animals
                $.each(o.rows, function(i, a) {
                    o.results.append( '<div class="asm-animalchoosermulti-result asm-shelterview-animal">' + 
                        html.animal_link_thumb(a, { showselector: true, showunit: true, showlocation: true }) +
                    '</div> '); // NOTE: Extra space after div to leave a small gap between items
                });

                // Delegate event handler for the checkboxes
                o.results.off("click", "input[type='checkbox']");
                o.results.on("click", "input[type='checkbox']", function(e) { 
                    self.update_status(t);
                });

                // Remove the spinner
                o.dialog.find(".spinner").hide();

                // Select all toggle
                o.dialog.find(".animalchoosermulti-selectall").click(function(e) {
                    if (!self.select_all_toggle) {
                        self.select_all_toggle = true;
                        o.dialog.find(".animalselect:visible").prop("checked", true);
                        self.update_status(t);
                    }
                    else {
                        self.select_all_toggle = false;
                        o.dialog.find(".animalselect").prop("checked", false);
                        self.update_status(t);
                    }
                    return false;
                });

                // Was there a value already set by the markup? If so, use it
                if (t.val() != "") {
                    self.selectbyids(t, t.val());
                    t.trigger("select", [ t.val() ]);
                }

            },
            error: function(jqxhr, textstatus, response) {
                o.dialog.dialog("close");
                o.dialog.find(".spinner").hide();
                log.error(response);
            }
        });
    }
});