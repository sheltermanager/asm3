/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, console, jQuery */
/*global asm, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

(function($) {

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
            rowlocations: [],
            rowspecies: [],
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
                '<table style="border-bottom: 1px solid #aaa; width: 100%">',
                '<tr>',
                '<td>' + _("Locations") + ':</td>',
                '<td class="animalchoosermulti-locations"></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Species") + ':</td>',
                '<td class="animalchoosermulti-species"></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Litters") + ':</td>',
                '<td class="animalchoosermulti-litters"></td>',
                '</tr>',
                '</table>',
                '<div class="animalchoosermulti-results">',
                '</div>',
                '</div>', 
                '</div>'
            ].join("\n");

            var node = $(h);
            var self = this;

            this.options.node = node;
            var dialog = node.find(".animalchoosermulti-find");
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
            this.options.locations.find(":checked").prop("checked", false);
            this.options.species.find(":checked").prop("checked", false);
            this.options.results.find(":checked").prop("checked", false);
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
         * Updates the info strip at the top to show how many animals selected
         */
        update_status: function() {
            var c = this.options.results.find(":checked").length;
            this.options.dialog.find(".totalselected").html(html.info(_("{0} selected").replace("{0}", c)));
            this.options.results.find(".asm-animalchoosermulti-selected").removeClass("asm-animalchoosermulti-selected");
            this.options.results.find(":checked").each(function() {
                var tn = $(this);
                tn.closest(".asm-animalchoosermulti-result").addClass("asm-animalchoosermulti-selected");
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
                    self.rowlocations = rv.locations;
                    self.rowspecies = rv.species;
                    self.rowlitters = rv.litters;

                    // Add a thumbnail for each shelter animal to the results
                    $.each(self.rows, function(i, a) {
                        var loc = '<input type="hidden" class="locationid" data="{locid}" />'.replace("{locid}", a.SHELTERLOCATION);
                        // If the animal has an active movement, don't include their last location, add a hook for the movement type instead
                        if (a.ACTIVEMOVEMENTTYPE > 0) { loc = '<input type="hidden" class="activemovementtype" data="{mtype}" />'.replace("{mtype}", a.ACTIVEMOVEMENTTYPE); }
                        results.append( '<div class="asm-animalchoosermulti-result">' + 
                            html.animal_link_thumb(a, { showselector: true, showunit: true, showlocation: true }) + 
                            loc + 
                            '<input type="hidden" class="speciesid" data="{speciesid}" />'.replace("{speciesid}", a.SPECIESID) +
                            '<input type="hidden" class="litterid" data="{litterid}" />'.replace("{litterid}", self.litterid_escape(a.ACCEPTANCENUMBER)) +
                        '</div>' );
                    });
                    results.off("click", "input[type='checkbox']");
                    results.on("click", "input[type='checkbox']", function(e) {
                        self.update_status();
                    });

                    // Add virtual locations for Foster and Retailer
                    if (self.id_used("ACTIVEMOVEMENTTYPE", 2)) {
                        locations.append('<span style="white-space: nowrap"><input type="checkbox" class="mtypecheck" data="2" id="mtype8" />' +
                            '<label for="mtype2">' + _("Foster") + '</label></span>');
                    }
                    if (self.id_used("ACTIVEMOVEMENTTYPE", 8)) {
                        locations.append('<span style="white-space: nowrap"><input type="checkbox" class="mtypecheck" data="8" id="mtype8" />' +
                            '<label for="mtype8">' + _("Retailer") + '</label></span>');
                    }

                    // Add a checkbox for each location and make clicking it auto select those animals
                    $.each(self.rowlocations, function(i, l) {
                        if (self.id_used("SHELTERLOCATION", l.ID)) {
                            locations.append('<span style="white-space: nowrap"><input type="checkbox" class="loccheck" data="' + l.ID + '" id="loc' + l.ID + '" />' +
                                '<label for="loc' + l.ID + '">' + l.LOCATIONNAME + '</label></span> ');
                        }
                    });
                    locations.off("click", "input[type='checkbox']");
                    locations.on("click", "input[type='checkbox']", function(e) {
                        var tn = $(this);
                        if (tn.hasClass("loccheck")) {
                            results.find(".locationid[data='" + tn.attr("data") + "']").each(function() {
                                $(this).closest("div").find(".animalselect").prop("checked", tn.prop("checked"));
                            });
                        }
                        else if (tn.hasClass("mtypecheck")) {
                            results.find(".activemovementtype[data='" + tn.attr("data") + "']").each(function() {
                                $(this).closest("div").find(".animalselect").prop("checked", tn.prop("checked"));
                            });
                        }
                        self.update_status();
                    });

                    // Add a checkbox for each species and make clicking it auto select those animals
                    $.each(self.rowspecies, function(i, s) {
                        if (self.id_used("SPECIESID", s.ID)) {
                            species.append('<span style="white-space: nowrap"><input type="checkbox" class="spcheck" data="' + s.ID + '" id="sp' + s.ID + '" />' +
                                '<label for="sp' + s.ID + '">' + s.SPECIESNAME + '</label></span> ');
                        }
                    });
                    species.off("click", "input[type='checkbox']");
                    species.on("click", "input[type='checkbox']", function(e) {
                        var tn = $(this);
                        var aset = results.find(".speciesid[data='" + tn.attr("data") + "']").each(function() {
                            $(this).closest("div").find(".animalselect").prop("checked", tn.prop("checked"));
                        });
                        self.update_status();
                    });

                    // Add a checkbox for each litter and make clicking it auto select those animals
                    $.each(self.rowlitters, function(i, l) {
                        if (self.id_used("ACCEPTANCENUMBER", l.ACCEPTANCENUMBER)) {
                            litters.append('<span style="white-space: nowrap"><input type="checkbox" class="litcheck" data="' + 
                                self.litterid_escape(l.ACCEPTANCENUMBER) + '" id="lit' + l.ID + '" />' +
                                '<label for="lit' + l.ID + '">' + 
                                common.nulltostr(l.MOTHERCODE) + ' ' + common.nulltostr(l.MOTHERNAME) + 
                                ' ' + l.ACCEPTANCENUMBER + ' - ' + l.SPECIESNAME + '</label></span> ');
                        }
                    });
                    litters.off("click", "input[type='checkbox']");
                    litters.on("click", "input[type='checkbox']", function(e) {
                        var tn = $(this);
                        var aset = results.find(".litterid[data='" + tn.attr("data") + "']").each(function() {
                            $(this).closest("div").find(".animalselect").prop("checked", tn.prop("checked"));
                        });
                        self.update_status();
                    });

                    // Remove the spinner
                    dialog.find(".spinner").hide();

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

} (jQuery));
