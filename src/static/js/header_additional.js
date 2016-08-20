/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, format, header, html, validate */
/*global additional: true */

$(function() {

    // If this is the login or database create page, don't do anything - they don't have headers, 
    // but for the sake of making life easy, they still include this file.
    if (common.current_url().indexOf("/login") != -1 ||
        common.current_url().indexOf("/database") != -1) {
        return;
    }

    /**
     * The additional object deals with rendering additional fields
     */
    additional = {

        YESNO: 0,
        TEXT: 1,
        NOTES: 2,
        NUMBER: 3,
        DATE: 4,
        MONEY: 5,
        LOOKUP: 6,
        MULTI_LOOKUP: 7,
        ANIMAL_LOOKUP: 8,
        PERSON_LOOKUP: 9,

        /**
         * Renders and lays out additional fields from data from the backend 
         * additional.get_additional_fields call as HTML controls. 
         * If there are no fields, an empty string is returned.
         * The output is a string containing a pair of tables to be rendered to the additional
         * section of a details page. One of the tables has a class of
         * additionalmove and its contents will be relocated to other
         * sections according to config later by the screen itself.
         */
        additional_fields: function(fields) {
            if (fields.length == 0) { return; }
            var add = [], other = [], addidx = 0;
            add.push('<table class="asm-additional-fields-container" width=\"100%\">\n<tr>\n');
            other.push('<table class=\"additionalmove\" style=\"display: none\"><tr>\n');
            $.each(fields, function(i, f) {
                // If this field is going to the additional tab on animal, animalcontrol, owner, lostanimal, foundanimal or waitinglist
                // then add it to our 3 column add table.
                if (f.LINKTYPE == 0 || f.LINKTYPE == 1 || f.LINKTYPE == 9 || f.LINKTYPE == 11 || f.LINKTYPE == 13 || f.LINKTYPE == 20) {
                    add.push(additional.render_field(f));
                    addidx += 1;
                    // Every 3rd column, drop a row
                    if (addidx == 3) {
                        add.push("</tr><tr>");
                        addidx = 0;
                    }
                }
                else {
                    other.push(additional.render_field(f));
                }
            });
            add.push("</tr></table>");
            other.push("</tr></table>");
            return add.join("\n") + other.join("\n");
        },

        /**
         * Renders and lays out mandatory additional fields from data from the backend 
         * additional.get_additional_fields call as HTML controls. 
         * If there are no fields, an empty string is returned.
         * The output is a serious of 2 column table rows with label/field
         */
        additional_mandatory_fields: function(fields) {
            if (fields.length == 0) { return; }
            var add = [], addidx = 0;
            $.each(fields, function(i, f) {
                if (f.MANDATORY == 1) {
                    add.push("<tr>");
                    add.push(additional.render_field(f));
                    add.push("</tr>");
                }
            });
            return add.join("\n");
        },


        /**
         * On multi-slider pages, additional fields can be relocated to different
         * sections according to their type. When rendered, these fields will have
         * a toX class on their td tags. There will be a corresponding
         * section with an additionaltarget class and a data attribute with the
         * number that corresponds to toX.
         * This method should be called by bind later on when the fields have
         * been placed in the DOM.
         */
        relocate_fields: function() {
            $(".additionaltarget").each(function() {
                var target = $(this);
                var targetname = target.attr("data");
                $(".additionalmove ." + targetname).each(function() {
                    // $(this) is the td containing the label
                    var label = $(this);
                    var item = $(this).next();
                    // For some reason, jquery gets confused if we reparent the row, so
                    // we have to add a new row to the table and then move our cells in.
                    target.append("<tr></tr>");
                    target.find("tr:last").append(label);
                    target.find("tr:last").append(item);
                });
            });
        },


        /**
         * Renders a field. Fields are always output as a pair of
         * table cells, so its upto the caller to handle table rows.
         * If a VALUE attribute is present, the field is rendered with
         * the correct value in place.
         * The data-post value will be set to a.(1 if mandatory).fieldid
         * f: A combined row from the additionalfield and additional tables
         */
        render_field: function(f) {
            var fieldname = f.ID,
                fieldid = "add_" + fieldname,
                fieldval = f.VALUE || f.DEFAULTVALUE,
                postattr = "a." + f.MANDATORY + "." + fieldname,
                fh = [];
            if (f.FIELDTYPE == additional.YESNO) {
                var checked = "";
                if (fieldval && fieldval !== "0") { checked = 'checked="checked"'; }
                fh.push('<td class="to' + f.LINKTYPE + '"></td><td>');
                fh.push('<input id="' + fieldid + '" type="checkbox" class="asm-checkbox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '" ' + checked + ' />');
                fh.push('<label for="' + fieldid + '" title="' + html.title(f.TOOLTIP) + '">' + f.FIELDLABEL + '</label></td>');
            }
            else if (f.FIELDTYPE == additional.TEXT) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="textbox" class="asm-textbox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
            }
            else if (f.FIELDTYPE == additional.DATE) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="textbox" class="asm-textbox asm-datebox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '" /></td>');
            }
            else if (f.FIELDTYPE == additional.NOTES) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<textarea id="' + fieldid + '" data-post="' + postattr + '" class="asm-textareafixed additional" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '">' + fieldval + '</textarea>');
            }
            else if (f.FIELDTYPE == additional.NUMBER) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="textbox" class="asm-textbox asm-numberbox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
            }
            else if (f.FIELDTYPE == additional.MONEY) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="textbox" class="asm-textbox asm-currencybox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + format.currency(fieldval) + '"/></td>');
            }
            else if (f.FIELDTYPE == additional.LOOKUP) {
                var opts = [], cv = $.trim(common.nulltostr(fieldval));
                $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                    vo = $.trim(vo);
                    if (cv == vo) {
                        opts.push('<option selected="selected">' + vo + '</option>');
                    }
                    else {
                        opts.push('<option>' + vo + '</option>');
                    }
                });
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<select id="' + fieldid + '" class="asm-selectbox additional" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '">');
                fh.push(opts.join("\n"));
                fh.push('</select></td>');
            }
            else if (f.FIELDTYPE == additional.MULTI_LOOKUP) {
                var mopts = [], mcv = $.trim(common.nulltostr(fieldval)).split(",");
                $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                    vo = $.trim(vo);
                    if ($.inArray(vo, mcv) != -1) {
                        mopts.push('<option selected="selected">' + vo + '</option>');
                    }
                    else {
                        mopts.push('<option>' + vo + '</option>');
                    }
                });
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<select id="' + fieldid + '" class="asm-bsmselect additional" multiple="multiple" data-post="' + postattr + '" ');
                fh.push('title="' + html.title(f.TOOLTIP) + '">');
                fh.push(mopts.join("\n"));
                fh.push('</select></td>');
            }
            else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="hidden" class="asm-animalchooser additional" data-post="' + postattr + '" ');
                fh.push('value="' + html.title(fieldval) + '"/></td>');
            }
            else if (f.FIELDTYPE == additional.PERSON_LOOKUP) {
                fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + '</label></td><td>');
                fh.push('<input id="' + fieldid + '" type="hidden" class="asm-personchooser additional" data-post="' + postattr + '" ');
                fh.push('value="' + html.title(fieldval) + '"/></td>');
            }
            return fh.join("\n");
        },


        /**
         * Evaluates all additional fields in the DOM and checks to
         * see if they are mandatory and if so whether or not they
         * are blank. Returns true if all is ok, or false if a field
         * fails a check.
         * If a field fails the manadatory check:
         * 1. Its label is highlighted
         * 2. The correct accordion section is opened
         * 3. An error message is displayed
         */
        validate_mandatory: function() {
            var valid = true;
            $(".additional").each(function() {
                var t = $(this), 
                    label = $("label[for='" + t.attr("id") + "']"),
                    acchead = $("#" + t.closest(".ui-accordion-content").prev().attr("id"));
                // ignore checkboxes
                if (t.attr("type") != "checkbox") {
                    var d = String(t.attr("data-post"));
                    // mandatory additional fields have a post attribute prefixed with a.1
                    if (d.indexOf("a.1") != -1) {
                        if ($.trim(t.val()) == "") {
                            header.show_error(_("{0} cannot be blank").replace("{0}", label.html()));
                            // Find the index of the accordion section this element is in and activate it
                            $("#asm-details-accordion").accordion("option", "active", acchead.index("#asm-details-accordion h3"));
                            label.addClass(validate.ERROR_LABEL_CLASS);
                            t.focus();
                            valid = false;
                            return false;
                        }
                    }
                }
            });
            return valid;
        }

    };

});
