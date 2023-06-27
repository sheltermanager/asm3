/*global $, _, asm, common, config, format, header, html, validate */
/*global additional: true */

var additional;

$(function() {

"use strict";

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
    TIME: 10,
    PERSON_SPONSOR: 11,
    PERSON_VET: 12,

    /**
     * Renders and lays out additional fields from data from the backend 
     * additional.get_additional_fields call as HTML controls. 
     * If there are no fields, an empty string is returned.
     * The output is a string containing a pair of tables to be rendered to the additional
     * section of a details page. One of the tables has a class of
     * additionalmove and its contents will be relocated to other
     * sections according to config later by the screen itself.
     * includeids: if undefined or true, output id attributes for rendered fields
     * classes: classes to give rendered fields. undefined === "additional"
     */
    additional_fields: function(fields, includeids, classes) {
        if (fields.length == 0) { return; }
        var add = [], other = [], addidx = 0;
        add.push('<table class="asm-additional-fields-container" width=\"100%\">\n<tr>\n');
        other.push('<table class=\"additionalmove\" style=\"display: none\"><tr>\n');
        $.each(fields, function(i, f) {
            // If this field is going to the additional tab on animal, animalcontrol, owner, lostanimal, foundanimal or waitinglist
            // then add it to our 3 column add table.
            if (f.LINKTYPE == 0 || f.LINKTYPE == 1 || f.LINKTYPE == 9 || f.LINKTYPE == 11 || f.LINKTYPE == 13 || f.LINKTYPE == 20) {
                add.push(additional.render_field(f, includeids, classes));
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
     * Renders additional fields in tableform dialogs (see tableform.fields_render)
     */
    tableform_additional_fields: function(fields, additionalfieldtype, includeids, classes) {
        if (!fields || fields.length == 0) { return; }
        if (additionalfieldtype === undefined) { additionalfieldtype = -1; }
        var add = [], other = [], addidx = 0;
        //add.push('<table class="asm-additional-fields-container" width=\"100%\">\n<tr>\n');
        add.push('<tr>');
        $.each(fields, function(i, f) {
            if (f.FIELDTYPE == additionalfieldtype || additionalfieldtype == -1)
            {
                add.push(additional.render_field(f, includeids, classes));
                addidx += 1;
                // Every 3rd column, drop a row
                // if (addidx == 3) {
                    add.push("</tr><tr>");
                    addidx = 0;
                // }
            }
        });
        add.push("</tr>");
        //add.push("</tr></table>");
        return add.join("\n");
    },

    /**
     *  Sets on screen additional fields (in dialog) to their default values
     **/
    additional_fields_populate_from_json: function(fields) {
        fields.forEach(function(f) {
            var id = f.ID;
            var fieldid = "add_" + id;
            var fieldval = f.VALUE;
            var element = $("#" + fieldid); //document.getElementById(fieldid);
            if (element) {
                if (f.FIELDTYPE == additional.YESNO) {
                    element.prop("checked", (fieldval && fieldval == "1"));
                }
                else if (f.FIELDTYPE == additional.TEXT ||  f.FIELDTYPE == additional.NUMBER) {
                    element.val(html.decode(fieldval));
                }
                else if (f.FIELDTYPE == additional.NOTES) {
                    var s = fieldval;
                    if (!s) { s = ""; }
                    s = s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    element.val(html.decode(s));
                }
                else if (f.FIELDTYPE == additional.DATE) {
                    element.val(fieldval);
                    //element.val(format.date(fieldval));
                }
                else if (f.FIELDTYPE == additional.TIME) {
                    element.val(fieldval);
                    //element.val(format.time(fieldval));
                }
                else if (f.FIELDTYPE == additional.MONEY) {
                    element.currency("value", fieldval);
                }
                else if (f.FIELDTYPE == additional.LOOKUP) {
                    element.select("value", html.decode(fieldval)); 
                }
                else if (f.FIELDTYPE == additional.MULTI_LOOKUP) {
                    element.children().prop("selected", false);
                    var mcv = common.trim(common.nulltostr(fieldval)).split(",");
                    $.each(String(mcv).split(/[|,]+/), function(mi, mv) {
                        element.find("option").each(function() {
                            var ot = $(this), ov = $(this).prop("value");
                            if (html.decode(mv) == html.decode(ov)) {
                                ot.prop("selected", true);
                            }
                        });
                    });
                    element.change();
                }
                else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                    element.animalchooser("clear", false);
                    element.animalchooser("loadbyid", fieldval);
                }
                else if (f.FIELDTYPE == additional.PERSON_LOOKUP || f.FIELDTYPE == additional.PERSON_SPONSOR || f.FIELDTYPE == additional.PERSON_VET) {
                    element.personchooser("clear", false);
                    element.personchooser("loadbyid", fieldval);
                }
            }
        });
    },

    /**
     * Renders and lays out additional fields from the
     * additional.get_additional_fields call as HTML controls for 
     * new record screens. 
     * If there are no fields, an empty string is returned.
     * The output is a series of 2 column table rows with label/field
     */
    additional_new_fields: function(fields, includeids, classes) {
        if (fields.length == 0) { return; }
        var add = [], addidx = 0;
        $.each(fields, function(i, f) {
            if (f.NEWRECORD == 1) {
                add.push("<tr>");
                add.push(additional.render_field(f, includeids, classes, true));
                add.push("</tr>");
            }
        });
        return add.join("\n");
    },

    /**
     * Renders and lays out additional fields for the advanced search screens.
     * This call expects the backend to have already filtered and returned the
     * appropriate class (animal, etc).
     * columns: number of columns per row, 2 if not supplied
     */
    additional_search_fields: function(fields, columns) {
        if (fields.length == 0) { return; }
        if (!columns) { columns = 2; }
        let col = 0, h = [ '<tr class="asm3-search-additional-row">' ];
        $.each(fields, function(i, f) {
            if (!f.SEARCHABLE) { return; }
            // Text/Notes/Number fields
            if (f.FIELDTYPE == 1 || f.FIELDTYPE == 2 || f.FIELDTYPE == 3) {
                h.push('<td><label for="af_' + f.ID + '">' + f.FIELDLABEL + '</label></td>');
                h.push('<td><input type="text" id="af_' + f.ID + '" data="af_' + f.ID + '" class="asm-textbox" /></td>');
            }
            // Lookup/Multilookup fields
            if (f.FIELDTYPE == 6 || f.FIELDTYPE == 7) {
                h.push('<td><label for="af_' + f.ID + '">' + f.FIELDLABEL + '</label></td>');
                h.push('<td><select id="af_' + f.ID + '" data="af_' + f.ID + '" class="asm-selectbox">');
                h.push('<option value="">' + _("(all)") + '</option>');
                h.push( html.list_to_options(f.LOOKUPVALUES.split("|")) );
                h.push('</select></td>');
            }
            // Drop a row at each column boundary
            col += 1;
            if (col == columns) { 
                h.push('</tr><tr class="asm3-search-additional-row">'); 
                col = 0; 
            }
        });
        h.push("</tr>");
        return h.join("\n");
    },

    /**
     * Returns true if the additional field type t is a person ID
     */
    is_person_type: function(t) {
        return t == additional.PERSON_LOOKUP || t == additional.PERSON_SPONSOR || t == additional.PERSON_VET;
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
     * Merges additional field definitions (returned by asm3.additional.get_field_definitions in backend)
     * and values from a row (array of simple key/values) to use additional fields in add/edit dialogs used with tables
     * where additional fields are available.
     **/
    merge_definitions_and_values: function (additional, row) {
        // return additional.map((item) => ({ ...item, VALUE: (row.hasOwnProperty(item.FIELDNAME.toUpperCase()) ? row[item.FIELDNAME.toUpperCase()] : "") }));
        $.each(additional, function(i, a) {
            let fieldname = a.FIELDNAME.toUpperCase();
            a.VALUE = "";
            if (row.hasOwnProperty(fieldname)) { 
                a.VALUE = row[fieldname];
            }
        });
        return additional;
    },

    /**
     * Toggles visibility of elements by their linktype data attribute
     **/
    toggle_elements_by_linktype: function(classname, linktype) {
        var elements = $('.' + classname);
        elements.each(function() {
            if ($(this).data('linktype') === linktype) {
                $(this).closest('tr').show();
            } else {
                $(this).closest('tr').hide();
            }
        });        
    },

    /**
     * Updates a result row containing additional fields from the on-screen fields
     * - equivalent to tableform.fields_update_row
     */
    additional_fields_update_row: function(fields, linktype, row) {
        fields.forEach(function(f) {
            var id = f.ID;
            var fieldid = "add_" + id;
            if (f.LINKTYPE==linktype)
            {
                var element = $("#" + fieldid); //document.getElementById(fieldid);
                if (element) {
                    var fid = element.attr('data-post');
                    if (f.FIELDTYPE == additional.YESNO) {
                        row[f.FIELDNAME.toUpperCase()] = (element.is(":checked") ? "1" : "");
                    }
                    else if (f.FIELDTYPE == additional.TEXT || f.FIELDTYPE == additional.NOTES || f.FIELDTYPE == additional.NUMBER) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.DATE) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.TIME) {
                        var ts = element.val();
                        if (!ts) { ts = "00:00:00"; }
                        row[f.FIELDNAME.toUpperCase()] = ts; //format.date_iso_settime(row[f.FIELDNAME.toUpperCase()], ts);
                    }
                    else if (f.FIELDTYPE == additional.MONEY) {
                        row[f.FIELDNAME.toUpperCase()] = element.currency("value");
                    }
                    else if (f.FIELDTYPE == additional.LOOKUP) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.MULTI_LOOKUP) {
                        var selected_items = "";
                        if (!element.val()) { 
                            selected_items = ""; 
                        }
                        else if ($.isArray(element.val())) {
                            selected_items = element.val().join("|");
                        }
                        else {
                            selected_items = element.val();
                        }
                        row[f.FIELDNAME.toUpperCase()] = selected_items;
                    }
                    else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_LOOKUP) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_SPONSOR) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_VET) {
                        row[f.FIELDNAME.toUpperCase()] = element.val();
                    }
                }
            }
        });
    },

    /**
     * Returns a URI encoded string with additional field keys and values to post.
     * Only returns the ones relevant to the linktype so that others will be reset by backend.
     * fields is the list of results from the additionalfield table.
     **/
    additional_fields_post: function(fields, linktype) {
        let return_string = "";
        $.each(fields, function(i, f) {
            let id = f.ID;
            let fieldid = "add_" + id;
            if (f.LINKTYPE==linktype) {
                let element = $("#" + fieldid); //document.getElementById(fieldid);
                if (element) {
                    let fid = element.attr('data-post');
                    if (f.FIELDTYPE == additional.YESNO) {
                        return_string += "&" + fid + "=" + (element.is(":checked") ? "on" : "");
                    }
                    else if (f.FIELDTYPE == additional.TEXT || f.FIELDTYPE == additional.DATE || f.FIELDTYPE == additional.TIME || f.FIELDTYPE == additional.NOTES || f.FIELDTYPE == additional.NUMBER) {
                        return_string += "&" + fid + "=" + element.val();
                    }
                    else if (f.FIELDTYPE == additional.MONEY) {
                        return_string += "&" + fid + "=" + element.currency("value");
                    }                    
                    else if (f.FIELDTYPE == additional.LOOKUP || f.FIELDTYPE == additional.MULTI_LOOKUP) {
                        return_string += "&" + fid + "=" + element.val();
                        // for (var i = 0; i < element.options.length; i++) {
                        //     if (element.options[i].selected) {
                        //         return_string += element.options[i].value + ',';
                        //     }
                        // }
                    }
                    else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
                        return_string += "&" + fid + '=' + element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_LOOKUP) {
                        return_string += "&" + fid + '=' + element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_SPONSOR) {
                        return_string += "&" + fid + '=' + element.val();
                    }
                    else if (f.FIELDTYPE == additional.PERSON_VET) {
                        return_string += "&" + fid + '=' + element.val();
                    }
                }
            }
        });
        return return_string;
    },

    /**
     * Renders a field. Fields are always output as a pair of
     * table cells, so its upto the caller to handle table rows.
     * If a VALUE attribute is present, the field is rendered with
     * the correct value in place.
     * The data-post value will be set to a.(1 if mandatory).fieldid
     * f: A combined row from the additionalfield and additional tables
     * includeids: undefined or true - output an id attribute with the field
     * classes: one or more classes to give fields - undefined="additional" 
     * usedefault: if true, outputs the default value instead of the actual value
     */
    render_field: function(f, includeids, classes, usedefault) {
        var fieldname = f.ID,
            fieldid = "add_" + fieldname,
            fieldattr = 'id="' + fieldid + '" ' + 'data-linktype="' + f.LINKTYPE + '" ',
            fieldval = f.VALUE,
            postattr = "a." + f.MANDATORY + "." + fieldname,
            mi = "",
            fh = [];
        if (classes === undefined) { classes = "additional"; }
        if (usedefault === undefined) { usedefault = false; }
        if (usedefault) { fieldval = f.DEFAULTVALUE; }
        if (includeids === false) { fieldattr = ""; } // includeids has to be explicitly false to disable id attrs
        if (f.MANDATORY == 1) { mi = '&nbsp;<span class="asm-has-validation">*</span>'; }
        if (f.FIELDTYPE == additional.YESNO) {
            var checked = "";
            if (fieldval && fieldval !== "0") { checked = 'checked="checked"'; }
            fh.push('<td class="to' + f.LINKTYPE + '"></td><td>');
            fh.push('<input ' + fieldattr + ' type="checkbox" class="asm-checkbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" ' + checked + ' />');
            fh.push('<label for="' + fieldid + '" title="' + html.title(f.TOOLTIP) + '">' + f.FIELDLABEL + '</label></td>');
        }
        else if (f.FIELDTYPE == additional.TEXT) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.DATE) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi +'</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-datebox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '" /></td>');
        }
        else if (f.FIELDTYPE == additional.TIME) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-timebox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '" /></td>');
        }
        else if (f.FIELDTYPE == additional.NOTES) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<textarea ' + fieldattr + ' data-post="' + postattr + '" class="asm-textareafixed ' + classes + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '">' + common.nulltostr(fieldval) + '</textarea>');
        }
        else if (f.FIELDTYPE == additional.NUMBER) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-numberbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.MONEY) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-currencybox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + format.currency(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.LOOKUP) {
            var opts = [], cv = common.trim(common.nulltostr(fieldval));
            $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                vo = common.trim(vo);
                if (cv == vo) {
                    opts.push('<option selected="selected">' + vo + '</option>');
                }
                else {
                    opts.push('<option>' + vo + '</option>');
                }
            });
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<select ' + fieldattr + ' class="asm-selectbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '">');
            fh.push(opts.join("\n"));
            fh.push('</select></td>');
        }
        else if (f.FIELDTYPE == additional.MULTI_LOOKUP) {
            var mopts = [], mcv = common.trim(common.nulltostr(fieldval)).split(",");
            $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                vo = common.trim(vo);
                if ($.inArray(vo, mcv) != -1) {
                    mopts.push('<option selected="selected">' + vo + '</option>');
                }
                else {
                    mopts.push('<option>' + vo + '</option>');
                }
            });
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<select ' + fieldattr + ' class="asm-bsmselect ' + classes + '" multiple="multiple" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '">');
            fh.push(mopts.join("\n"));
            fh.push('</select></td>');
        }
        else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-animalchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_LOOKUP) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_SPONSOR) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '" data-filter="sponsor"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_VET) {
            fh.push('<td class="to' + f.LINKTYPE + '"><label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label></td><td>');
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '" data-filter="vet"/></td>');
        }
        return fh.join("\n");
    },

    /**
     * Validates all additional fields in a dialog and checks to
     * see if they are mandatory and if so whether or not they
     * are blank. Returns true if all is ok, or false if a field
     * fails a check.
     *
     * Deliberately ignores fields with the chooser class as this 
     * function is aimed at additional fields only.
     *
     * additional_field_class: class that all additional fields should have ("additional" by default)
     * linktype: named additional field link type constant, eg: animal, movement, etc.
     *
     * If a field fails the manadatory check its label is highlighted and an error is 
     * returned. { valid: false, message: "X cannot be blank" }
     */
    validate_mandatory_dialog: function(additional_field_class, linktype) {
        var valid = true, message="";
        $("." + additional_field_class).not(".chooser").each(function() {
            // only validate visible additional fields
            if ($(this).data('linktype') === linktype) {
                var t = $(this), 
                    label = $("label[for='" + t.attr("id") + "']");
                // ignore checkboxes
                if (t.attr("type") != "checkbox") {
                    var d = String(t.attr("data-post"));
                    // mandatory additional fields have a post attribute prefixed with a.1
                    if (d.indexOf("a.1") != -1) {
                        if (common.trim(t.val()) == "") {
                            label.addClass(validate.ERROR_LABEL_CLASS);
                            t.focus();
                            valid = false;
                            message = _("{0} cannot be blank").replace("{0}", label.html());
                            return false;
                        }
                    }
                }
            }
        });
        return {"valid": valid, "message": message};
    },

    /**
     * Validates all additional fields in the DOM and checks to
     * see if they are mandatory and if so whether or not they
     * are blank. Returns true if all is ok, or false if a field
     * fails a check.
     *
     * Deliberately ignores fields with the chooser class as this 
     * function is aimed at additional fields in bottom level forms
     * like animal, waiting list, etc.
     *
     * If a field fails the manadatory check:
     * 1. Its label is highlighted
     * 2. The correct accordion section is opened
     * 3. An error message is displayed
     */
    validate_mandatory: function() {
        var valid = true;
        $(".additional").not(".chooser").each(function() {
            var t = $(this), 
                label = $("label[for='" + t.attr("id") + "']"),
                acchead = $("#" + t.closest(".ui-accordion-content").prev().attr("id"));
            // ignore checkboxes
            if (t.attr("type") != "checkbox") {
                var d = String(t.attr("data-post"));
                // mandatory additional fields have a post attribute prefixed with a.1
                if (d.indexOf("a.1") != -1) {
                    if (common.trim(t.val()) == "") {
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
    },

    reset: function(){
        $.each(controller.additional, function(i, v){
            $("#add_" + v.ID).val(v.DEFAULTVALUE);
            if(v.FIELDTYPE == additional.MONEY)
                $("#add_" + v.ID).val($("#add_" + v.ID).attr("value"));
        });
    },

    /**
     * Validates additional fields inside the node given. Returns true 
     * if all is ok, or false if a field fails a check.
     * On failure an error message is displayed and the previous label highlighted.
     */
    validate_mandatory_node: function(node) {
        var valid = true;
        node.find(".additional").each(function() {
            var t = $(this), 
                label = t.closest("tr").find("label");
            // ignore checkboxes
            if (t.attr("type") != "checkbox") {
                var d = String(t.attr("data-post"));
                // mandatory additional fields have a post attribute prefixed with a.1
                if (d.indexOf("a.1") != -1) {
                    if (common.trim(t.val()) == "") {
                        header.show_error(_("{0} cannot be blank").replace("{0}", label.html()));
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
