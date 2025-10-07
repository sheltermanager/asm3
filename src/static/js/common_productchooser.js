/*global $, console, jQuery */
/*global _, asm, additional, common, config, dlgfx, edit_header, format, html, header, log, validate, escape, unescape */

"use strict";

/**
 * Person chooser widget. To create one
 */
$.widget("asm.productchooser", {

    selected: null,

    options: {
        id: 0,
        rec: {},
        title: _("Find product"),
        addtitle: _("Add product")
    },

    _create: function() {
        let self = this;

        let h = [
            '<div class="productchooser asm-chooser-container">',
            '<div class="productchooser-noperm" style="display: none">' + _("Forbidden") + '</div>',
            '<table class="productchooser-perm" style="margin-left: 0px; margin-right: 0px; width: 100%; ">',
            '<tr>',
            '<td class="productchooser-display"></td>',
            '<td valign="top" style="text-align: end; white-space: nowrap">',
            '<button class="productchooser-link-find">' + _("Select a product") + '</button>',
            '<button class="productchooser-link-clear">' + _("Clear") + '</button>',
            '</td>',
            '</tr>',
            '</table>',
            '<div class="productchooser-find" style="display: none" title="' + this.options.title + '">',
            '<input class="asm-textbox" type="text" />',
            '<button>' + _("Search") + '</button>',
            '<img style="height: 16px" src="static/images/wait/rolling_3a87cd.svg" />',
            '<table width="100%">',
            '<thead>',
                '<tr class="ui-widget-header">',
                    '<th>' + _("Product") + '</th>',
                    '<th>' + _("Type") + '</th>',
                    '<th>' + _("Current Stock") + '</th>',
                '</tr>',
            '</thead>',
            '<tbody></tbody>',
            '</table>',
            '</div>',
            '</div>'
        ].join("\n");
        
        let node = $(h);
        this.options.node = node;
        let dialog = node.find(".productchooser-find");
        
        this.options.dialog = dialog;
        this.options.display = node.find(".productchooser-display");
        this.element.parent().append(node);

        // Disable based on view person permission
        if (!common.has_permission("vo")) {
            node.find(".personchooser-perm").hide();
            node.find(".personchooser-noperm").show();
        }
        
        // Create the find dialog
        let pcbuttons = {};
        pcbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        dialog.dialog({
            autoOpen: false,
            height: common.vheight(600),
            width: common.vwidth(800),
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: pcbuttons
        });
        dialog.find("table").table({ sticky_header: false });
        dialog.find("input").keydown(function(event) { if (event.keyCode == 13) { self.find(); return false; }});
        dialog.find("button").button().click(function() { self.find(); });
        dialog.find("img").hide();

        node.find(".productchooser-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                dialog.dialog("open");
            });
        
        node.find(".productchooser-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear(true);
            });
        
    },
    clear: function(fireclearedevent) {
        this.element.val("0");
        this.options.id = 0;
        this.options.display.html("");
        this.selected = null;
        if (fireclearedevent) { this._trigger("cleared", null); }
    },
    loadbyid: function(productid) {
        if (!productid || productid == "0" || productid == "") { return; }
        this.clear();
        this.element.val(productid);
        let self = this, node = this.options.node, display = this.options.display, dialog = this.options.dialog;
        let formdata = "mode=id&id=" + productid;
        $.ajax({
            type: "POST",
            url:  "product_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let people = jQuery.parseJSON(data);
                let rec = people[0];
                self.element.val(rec.ID);
                display.html(self.render_display(rec));
                common.inject_target();
                self._trigger("loaded", null, rec);
                self.selected = rec;
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },
    find: function() {
        let self = this, 
            dialog = this.options.dialog, 
            node = this.options.node, 
            display = this.options.display;
        dialog.find("img").show();
        dialog.find("button").button("disable");
        let q = encodeURIComponent(dialog.find("input").val());
        let formdata = "mode=find&filter=" + this.options.filter + "&type=" + this.options.type + "&q=" + q;
        $.ajax({
            type: "POST",
            url:  "product_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                let h = "";
                let products = jQuery.parseJSON(data);
                $.each(products, function(i, p) {
                    let balance = 0;
                    if (p.BALANCE) { 
                        balance = p.BALANCE;
                    }
                    h += "<tr>";
                    h += "<td><a href=\"#\" data=\"" + i + "\">" + p.PRODUCTNAME + "</a></td>";
                    h += "<td>" + p.PRODUCTTYPENAME + "</td>";
                    h += "<td>" + balance + "</td>";
                    h += "</tr>";
                });
                dialog.find("table > tbody").html(h);
                // Remove any existing events from previous searches
                dialog.off("click", "a");
                // Use delegation to bind click events for 
                // the product once clicked. Triggers the change callback
                dialog.on("click", "a", function(e) {
                    let rec = products[$(this).attr("data")];
                    self.element.val(rec.ID);
                    self.options.rec = rec;
                    display.html(self.render_display(rec));
                    try { validate.dirty(true); } catch(exp) { }
                    dialog.dialog("close");
                    self._trigger("change", null, rec);
                    self.selected = rec;
                    return false;
                });
                dialog.find("table").trigger("update");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                common.inject_target();
            },
            error: function(jqxhr, textstatus, response) {
                dialog.dialog("close");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
                log.error(response);
            }
        });
    },
    render_display: function(rec) {
        let disp = "<span class=\"justlink\">";
        disp += "<a class=\"asm-embed-name\" href=\"product?id=" + rec.ID + "\">" + rec.PRODUCTNAME + "</a></span>";
        return disp;
    }
});
