/*global $, console, jQuery */
/*global asm, asm_widget, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

"use strict";

/**
 * Multiple person chooser widget. To create one, use a hidden input
 * with a class of asm-personchoosermulti for bind_widgets to autoload
 *
 * <input id="person" class="asm-personchoosermulti" data="boundfield" type="hidden" value="commaseparatedids" />
 * 
 * $(".asm-personchoosermulti").personchoosermulti(); // (bind_widgets does this automatically)
 *
 * events: select (after selectbyids is complete)
 *         change (after user has clicked select button)
 *         cleared (after user clicks the clear button)
 */
$.fn.personchoosermulti = asm_widget({

    _create: function(t) {
        
        let self = this;

        let h = [
            '<div class="personchoosermulti asm-chooser-container">',
                '<table style="margin-left: 0px; margin-right: 0px; width: 100%; ">',
                    '<tr>',
                    '<td class="personchoosermulti-display">',
                    '</td>',
                    '<td valign="top" style="text-align: end; white-space: nowrap">',
                    '<button type="button" class="personchoosermulti-link-find">' + _("Select people") + '</button>',
                    '<button type="button" class="personchoosermulti-link-clear">' + _("Clear") + '</button>',
                    '</td>',
                    '</tr>',
                '</table>',
                '<div class="personchoosermulti-find" title="' + html.title(_("Select people")) + '">',
                    '<div class="totalselected" style="margin-bottom: 5px;">',
                        html.info(_("{0} selected").replace("{0}", "0")),
                    '</div>',
                    '<div style="border-bottom: 1px solid #aaa; width: 100%;padding-bottom: 5px;">',
                        '<div class="asm-personchoosermulti-filter">',
                            '<a href="#" class="personchoosermulti-selectall" title="Select all"><span class="ui-icon ui-icon-check"></span></a>',
                        '</div>',
                        '<div style="display: inline-block;vertical-align: top;">',
                            '<input class="asm-textbox personchoosermulti-searchinput" type="text" />',
                            '<button class="personchoosermulti-searchbutton">' + _("Search") + '</button>',
                            '<img style="height: 16px" class="spinner" src="static/images/wait/rolling_3a87cd.svg" />',
                        '</div>',
                        '<div class="personchoosermulti-flags-container" style="display: inline-block;float: right;max-width: 400px;">',
                            '<div style="vertical-align: top;padding-top: 3px;">' + _("Flags") + ':&nbsp;</div>',
                            '<select style="display: inline-block;" multiple="multiple" title="' + _("Filter") + '" class="personchoosermulti-flags asm-selectmulti"></select>', 
                        '</div>',
                        '<div style="clear: right;"></div>',
                    '</div>',
                    '<div>',
                    '<table class="personchoosermulti-results asm-widget asm-table tablesorter tablesorter-default"><thead><tr><th>' + _("Name") + '</th><th>' + _("Code") + '</th><th>' + _("Address") + '</th><th>' + _("Zipcode") + '</th></thead><tbody class="personchoosermulti-results-body"></tbody></table>',
                    '</div>',
                '</div>', 
            '</div>'
        ].join("\n");

        let node = $(h);

        let o = {};
        t.data("o", o);
        o.node = node;
        o.dialog = node.find(".personchoosermulti-find");
        o.display = node.find(".personchoosermulti-display");
        o.flags = node.find(".personchoosermulti-flags");
        o.search = node.find(".personchoosermulti-searchbutton");
        o.results = node.find(".personchoosermulti-results-body");
        o.selectedrows = [];
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
                if (!o.loaded) {
                    self.load.call(self, t);
                    $(".personchoosermulti-flags-container div").css("display", "inline-block");
                    o.loaded = true;
                }
            }
        });
        o.dialog.find("table").table({ sticky_header: false });
        o.dialog.find("input").keydown(function(event) { if (event.keyCode == 13) { self.find.call(self, t); return false; }});
        o.dialog.find("img").hide();
        o.dialog.find(".personchoosermulti-searchbutton").button().css("padding", ".2em 1em").css("top", "-1px");

        // Bind the find button
        node.find(".personchoosermulti-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                o.dialog.dialog("open");
            });

        // Bind the clear button
        node.find(".personchoosermulti-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear.call(self, t, true);
            });
    },

    /**
     * Empties the widget
     */
    clear: function(t, fireclearedevent = false) {
        t.val("");
        let o = t.data("o");
        o.display.html("");
        o.results.find(":checked").prop("checked", false);
        this.update_status(t);
        o.selectedrows = [];
        if (fireclearedevent) { t.trigger("cleared"); }
    },

    is_empty: function(t) {
        let o = t.data("o");
        return o.results.find(":checked").length == 0;
    },

    destroy: function(t) {
        try {
            let o = t.data("o");
            o.dialog.dialog("destroy"); 
            o.dialog.remove();
        }
        catch (ex) {}
    },

    /**
     * Returns the person row with ID pid
     */
    get_row: function(t, pid) {
        let rv, o = t.data("o");
        $.each(o.rows, function(i, v) {
            if (v.ID == pid) {
                rv = v;
            }
        });
        return rv;
    }, 

    get_rows: function(t) {
        return t.data("o").rows;
    }, 

    get_selected_rows: function(t) {
        let rows = [];
        let self = this;
        $.each(t.val().split(","), function(i, v) {
            rows.push(self.get_row(t, v));
        });
        return rows;
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
        let summaryfloor = 5;
        o.display.html("");
        let h = []
        if (o.selectedrows.length > 0) {
            if (o.selectedrows.length > summaryfloor) {
                h = [
                    '<div class="personchoosermulti-summary">',
                    '<span class="personchooser-summaryexpander ui-icon ui-icon-triangle-1-e" data="0"></span>',
                    '<b>' + _("{0} selected").replace("{0}", o.selectedrows.length) + '</b>',
                    '</div>'
                ];
            }
            h.push('<div class="personchoosermulti-details" style="display: none;">');
            $.each(o.selectedrows, function(i, p) {
                selval.push(p.ID);
                h.push('<a class="asm-embed-name" href="person?id=' + p.ID + '">' + p.OWNERNAME + '</a><br />');
            });
            h.push('</div>');
            if (o.selectedrows.length > summaryfloor) {
                h.push('</div>');
            }
        }
        let outputhtml = h.join("\n");
        o.display.html(outputhtml);
        if (o.selectedrows.length <= summaryfloor) {
            o.display.find(".personchoosermulti-details").show();
        }
        t.val(selval.join(","));
        t.trigger("change", [ t.val() ]);
        o.dialog.dialog("close");
    },

    /**
     * Update the visible list of people according to what's selected in the filters
     */
    update_filters: function(t) {
        let o = t.data("o");
        $.each(o.rows, function(i, p) {
            let show = true;
            let selflag = String(o.flags.val()).trim().split(",");
            if (String(o.flags.val()).trim() && selflag.length > 0 && !common.array_overlap_all(selflag, p.ADDITIONALFLAGS.split("|"))) {
                show = false;
            } else {
                show = false;
                let searchkey = o.dialog.find(".personchoosermulti-searchinput").val();
                if (p.OWNERNAME.toLowerCase().includes(searchkey.toLowerCase())) {
                    show = true;
                } else if (p.OWNERADDRESS.toLowerCase().includes(searchkey.toLowerCase())) {
                    show = true;
                } else if (p.OWNERPOSTCODE.toLowerCase().replace(/ /g, "").includes(searchkey.toLowerCase().replace(/ /g, ""))) {
                    show = true;
                } else if (p.OWNERCODE.toLowerCase() == searchkey.toLowerCase()) {
                    show = true;
                }
            }
            o.dialog.find(".personselect[data='" + p.ID + "']").closest(".asm-personchoosermulti-result").toggle(show);
        });
    },

    /**
     * Updates the info strip at the top to show how many people selected
     */
    update_status: function(t) {
        let o = t.data("o");
        let c = o.selectedrows.length;
        let mc = _("{0} selected").replace("{0}", c);
        o.dialog.find(".totalselected").html(html.info(mc));
        o.results.find(".asm-personchoosermulti-selected").removeClass("asm-personchoosermulti-selected").removeClass("ui-state-highlight");
        o.results.find(":checked").each(function() {
            let tn = $(this);
            tn.closest(".asm-personchoosermulti-result").addClass("asm-personchoosermulti-selected").addClass("ui-state-highlight");
        });
    },

    /**
     * Selects people based on a comma separated list of ids as a string
     */
    selectbyids: function(t, personids, ignorechange=false) {
        let self = this, o = t.data("o");
        if (!ignorechange) { self.clear.call(self, t); }
        if (!personids) { return; }
        $.each(personids.split(","), function(i, v) {
            o.results.find("[data='" + v + "']").prop("checked", true);
        });
        self.update_status(t);
        if (!ignorechange) { t.trigger("change", [personids] ); }
    },

    load: function(t) {
        let self = this, o = t.data("o");
        o.dialog.find("img").show();
        let formdata = "mode=multiselect";
        $.ajax({
            type: "POST",
            url:  "person_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {

                let rv = jQuery.parseJSON(data);
                o.rows = rv.rows;

                // Flags list
                html.person_flag_options(null, rv.flags, o.flags);
                o.flags.on("change", function(e) {
                    self.find.call(self, t);
                });
                o.search.on("click", function(e) {
                    self.find.call(self, t);
                });
                o.display.on("click", ".personchooser-summaryexpander", function(e) {
                    if ($(this).attr("data") == "0") {
                        $(this).removeClass("ui-icon-triangle-1-e");
                        $(this).addClass("ui-icon-triangle-1-s");
                        $(this).attr("data", "1");
                        o.display.find(".personchoosermulti-details").fadeIn();
                    } else {
                        $(this).addClass("ui-icon-triangle-1-e");
                        $(this).removeClass("ui-icon-triangle-1-s");
                        $(this).attr("data", "0");
                        o.display.find(".personchoosermulti-details").fadeOut();
                    }
                });
                // personchooser-summaryexpander
                o.results.on("change", "input", function(e) {
                    let checkbox = $(e.currentTarget);
                    let rowid = checkbox.attr("data");
                    $.each(o.rows, function(i, r) {
                        if (r.ID == rowid) {
                            let rowpresent = common.get_row(o.selectedrows, r.ID) != null;
                            if (checkbox.prop("checked") && !rowpresent) {
                                o.selectedrows.push(r);
                            } else if (!checkbox.prop("checked") && rowpresent) {
                                // Iterating through a copy of selected rows so changes can be made
                                $.each([...o.selectedrows], function(c, s) {
                                    if (r.ID == s.ID) {
                                        o.selectedrows.splice(c, 1);
                                    }
                                });
                            }
                        }
                    });
                    self.update_status(t);
                });

                // Delegate event handler for the checkboxes
                o.results.off("click", "input[type='checkbox']");
                o.results.on("click", "input[type='checkbox']", function(e) {
                    self.update_status(t);
                });

                // Remove the spinner
                o.dialog.find(".spinner").hide();

                // Select all toggle
                o.dialog.find(".personchoosermulti-selectall").click(function(e) {
                    if (!self.select_all_toggle) {
                        self.select_all_toggle = true;
                        o.dialog.find(".personselect:visible").prop("checked", true).change();
                        self.update_status(t);
                    }
                    else {
                        self.select_all_toggle = false;
                        o.dialog.find(".personselect").prop("checked", false).change();
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
    },

    find: function(t) {
        let o = t.data("o");
        let self = this, 
            dialog = o.dialog,
            node = o.node,
            display = o.display;
        dialog.find("img").show();
        dialog.find("button").button("disable");
        let q = encodeURIComponent(dialog.find("input").val());
        let formdata = "mode=find&filter=all&type=all&q=" + q;
        $.ajax({
            type: "POST",
            url:  "person_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let people = jQuery.parseJSON(data);
                o.rows = people;
                $.each(people, function(i, p) {
                    h += "<tr class=\"asm-personchoosermulti-result\">";
                    h += "<td><input type=\"checkbox\" class=\"personselect\" data=\"" + p.ID + "\"";
                    $.each(o.selectedrows, function(i, r) {
                        if (r.ID == p.ID) { h += " checked"; }
                    });
                    h += "><a href=\"/person?id=" + p.ID + "\" data=\"" + p.ID + "\">" + p.OWNERNAME + "</a></td>";
                    h += "<td>" + p.OWNERCODE + "</td>";
                    h += "<td>" + p.OWNERADDRESS + "</td>";
                    h += "<td>" + p.OWNERPOSTCODE + "</td>";
                    h += "</tr>";
                });
                dialog.find("table > tbody").html(h);
                // Remove any existing events from previous searches
                dialog.off("click", "a");
                dialog.find("table").trigger("update");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                common.inject_target(); 
                self.update_filters(t);
            },
            error: function(jqxhr, textstatus, response) {
                // dialog.dialog("close");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                log.error(response);
            }
        });
    }
});