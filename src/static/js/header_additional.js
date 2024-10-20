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
    PERSON_ADOPTIONCOORDINATOR: 13,

    /**
     * Renders and lays out additional fields from data from the backend 
     * additional.get_additional_fields call as HTML controls for an 
     * additional slider section on a details screen.
     * If there are no fields, an empty string is returned.
     * The output is a string containing the 3 column layout of the fields.
     * includeids: if undefined or true, output id attributes for rendered fields
     * classes: classes to give rendered fields. undefined === "additional"
     */
    additional_fields: function(fields, includeids, classes) {
        if (fields.length == 0) { return ""; }
        let addidx = 1,
            col_start = '<div class="col"><table class="asm-additional-fields-container" width=\"100%\">',
            col_end = '</table></div>',
            col1 = [ col_start ], col2 = [ col_start ], col3 = [ col_start ];
        $.each(fields, function(i, f) {
            // If this field is going to the additional tab on animal, animalcontrol, owner, lostanimal, foundanimal or waitinglist
            // then add it to the next column in our 3 column output (we do it like this so that they stack on mobile)
            if (f.LINKTYPE == 0 || f.LINKTYPE == 1 || f.LINKTYPE == 9 || f.LINKTYPE == 11 || f.LINKTYPE == 13 || f.LINKTYPE == 20) {
                let fm = additional.render_field(f, includeids, classes);
                if (addidx == 1) { col1.push(fm); }
                else if (addidx == 2) { col2.push(fm); }
                else if (addidx == 3) { col3.push(fm); }
                addidx += 1;
                if (addidx == 4) { addidx = 1; }
            }
        });
        col1.push(col_end);
        col2.push(col_end);
        col3.push(col_end);
        return '<div class="row">' + col1.join("\n") + col2.join("\n") + col3.join("\n") + '</div>';
    },

    /**
     * Renders and lays out additional fields from data from the backend 
     * additional.get_additional_fields call as HTML controls. 
     * If there are no fields, an empty string is returned.
     * The output is a set of rows for the current column of fields
     * being output.
     * linktype: only output fields that match the linktype given
     * includeids: if undefined or true, output id attributes for rendered fields
     * classes: extra classes to give rendered fields. undefined === "additional"
     */
    additional_fields_linktype: function(fields, linktype, includeids, classes) {
        if (fields.length == 0) { return ""; }
        let add = [];
        $.each(fields, function(i, f) {
            if (f.LINKTYPE == linktype) {
                add.push(additional.render_field(f, includeids, classes));
            }
        });
        return add.join("\n");
    },

    /**
     * Renders additional fields in tableform dialogs (see tableform.fields_render)
     */
    additional_fields_tableform: function(fields, additionalfieldtype, includeids, classes) {
        if (!fields || fields.length == 0) { return ""; }
        if (additionalfieldtype === undefined) { additionalfieldtype = -1; }
        let add = [];
        $.each(fields, function(i, f) {
            if (f.FIELDTYPE == additionalfieldtype || additionalfieldtype == -1) {
                add.push(additional.render_field(f, includeids, classes));
            }
        });
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
            var element = $("#" + fieldid); 
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
                else if (f.FIELDTYPE == additional.PERSON_LOOKUP || f.FIELDTYPE == additional.PERSON_SPONSOR || f.FIELDTYPE == additional.PERSON_VET || f.FIELDTYPE == additional.PERSON_ADOPTIONCOORDINATOR) {
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
        if (fields.length == 0) { return ""; }
        var add = [], addidx = 0;
        $.each(fields, function(i, f) {
            if (f.NEWRECORD == 1) {
                add.push(additional.render_field(f, includeids, classes, true));
            }
        });
        return add.join("\n");
    },

    /**
     * Renders and lays out additional fields for the advanced search screens.
     * This call expects the backend to have already filtered and returned the
     * appropriate class (animal, etc).
     */
    additional_search_fields: function(fields) {
        if (fields.length == 0) { return ""; }
        if (!columns) { columns = 2; }
        let col = 0, h = [];
        $.each(fields, function(i, f) {
            if (!f.SEARCHABLE) { return; }
            if (f.HIDDEN) { return; } 
            // Text/Notes/Number fields
            if (f.FIELDTYPE == 1 || f.FIELDTYPE == 2 || f.FIELDTYPE == 3) {
                h.push(html.search_field_text("af_" + f.ID, f.FIELDLABEL));
            }
            // Lookup/Multilookup fields
            if (f.FIELDTYPE == 6 || f.FIELDTYPE == 7) {
                h.push(html.search_field_select("af_" + f.ID, f.FIELDLABEL, html.list_to_options(f.LOOKUPVALUES.split("|"))));
            }
        });
        return h.join("\n");
    },

    /**
     * Returns true if the additional field type t is a person ID
     */
    is_person_type: function(t) {
        return t == additional.PERSON_LOOKUP || t == additional.PERSON_SPONSOR || 
            t == additional.PERSON_VET || t == additional.PERSON_ADOPTIONCOORDINATOR;
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
            if (f.LINKTYPE==linktype) {
                var element = $("#" + fieldid); 
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
                        row[f.FIELDNAME.toUpperCase()] = ts; 
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
                    else if (f.FIELDTYPE == additional.PERSON_ADOPTIONCOORDINATOR) {
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
                let element = $("#" + fieldid); 
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
                    else if (f.FIELDTYPE == additional.PERSON_ADOPTIONCOORDINATOR) {
                        return_string += "&" + fid + '=' + element.val();
                    }
                }
            }
        });
        return return_string;
    },

    /**
     * Renders a field.  
     * If a VALUE column is present, the field is rendered with the correct value in place.
     * The data-post value will be set to a.(1 if mandatory).fieldid
     * f: A combined row from the additionalfield and additional tables
     * includeids: undefined or true - output an id attribute with the field
     * classes: one or more classes to give fields - undefined="additional" 
     * usedefault: if true, outputs the default value instead of the actual value
     * 
     * This is the original version of this method, that didn't use the abstractions
     * in tableform. The code has been left here for now in case
     * of compatibility issues with the new version of render_field so we can check
     * what the old behaviour was.
     * 
    render_field_old: function(f, includeids, classes, usedefault) {
        var fieldname = f.ID,
            fieldid = "add_" + fieldname,
            fieldattr = 'id="' + fieldid + '" ' + 'data-linktype="' + f.LINKTYPE + '" ',
            fieldval = f.VALUE,
            fieldlabel = '<label for="' + fieldid + '">' + f.FIELDLABEL + '</label>',
            postattr = "a." + f.MANDATORY + "." + fieldname,
            mi = "",
            fh = [ ],
            td1open = '<td>', 
            td2open = '<td>';
        if (f.HIDDEN == 1) { fh.push('<tr style="display: none">'); } else { fh.push('<tr>'); }
        if (classes === undefined) { classes = "additional"; }
        if (usedefault === undefined) { usedefault = false; }
        if (usedefault) { fieldval = f.DEFAULTVALUE; }
        if (includeids === false) { fieldattr = ""; } // includeids has to be explicitly false to disable id attrs
        if (f.MANDATORY == 1) { mi = '&nbsp;<span class="asm-has-validation">*</span>'; }
        fieldlabel = '<label for="' + fieldid + '">' + f.FIELDLABEL + mi + '</label>';
        if (f.FIELDTYPE == additional.YESNO) {
            var checked = "";
            if (fieldval && fieldval !== "0") { checked = 'checked="checked"'; }
            fh.push(td1open + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="checkbox" class="asm-checkbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" ' + checked + ' />');
            fh.push('<label for="' + fieldid + '" title="' + html.title(f.TOOLTIP) + '">' + f.FIELDLABEL + '</label></td>');
        }
        else if (f.FIELDTYPE == additional.TEXT) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.DATE) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-datebox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '" /></td>');
        }
        else if (f.FIELDTYPE == additional.TIME) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-timebox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '" /></td>');
        }
        else if (f.FIELDTYPE == additional.NOTES) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<textarea ' + fieldattr + ' data-post="' + postattr + '" class="asm-textareafixed ' + classes + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '">' + common.nulltostr(fieldval) + '</textarea>');
        }
        else if (f.FIELDTYPE == additional.NUMBER) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="text" class="asm-textbox asm-numberbox ' + classes + '" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '" value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.MONEY) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
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
            fh.push(td1open + fieldlabel + '</td>' + td2open);
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
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<select ' + fieldattr + ' class="asm-bsmselect ' + classes + '" multiple="multiple" data-post="' + postattr + '" ');
            fh.push('title="' + html.title(f.TOOLTIP) + '">');
            fh.push(mopts.join("\n"));
            fh.push('</select></td>');
        }
        else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-animalchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_LOOKUP) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_SPONSOR) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '" data-filter="sponsor"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_VET) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '" data-filter="vet"/></td>');
        }
        else if (f.FIELDTYPE == additional.PERSON_ADOPTIONCOORDINATOR) {
            fh.push(td1open + fieldlabel + '</td>' + td2open);
            fh.push('<input ' + fieldattr + ' type="hidden" class="asm-personchooser ' + classes + '" data-post="' + postattr + '" ');
            fh.push('value="' + html.title(fieldval) + '" data-filter="coordinator"/></td>');
        }
        fh.push('</tr>');
        return fh.join("\n");
    },
    */

    /**
     * Renders an additional field.  
     * If a VALUE column is present in f, the field is rendered with the correct value in place.
     * The data-post value will be set to a.(1 if mandatory).fieldid
     * f: A combined row from the additionalfield and additional tables
     * includeids: undefined or true - output an id attribute with the field
     *             (generally this is only false for special situations like when outputting
     *              additional new fields for the embedded add person on a person record so the
     *              id attributes don't clash as they aren't necessary for its operation)
     * classes: one or more classes to give fields - undefined="additional" 
     * usedefault: if true, outputs the default value instead of the actual value
     */
    render_field: function(f, includeids, classes, usedefault) {
        let v = {
            id: (includeids === undefined || includeids == true) ? "add_" + f.ID : "",
            post_field: "a." + f.MANDATORY + "." + f.ID,
            label: f.FIELDLABEL,
            classes: classes || "additional",
            rowclasses: f.HIDDEN ? "hidden" : "",
            value: usedefault ? f.DEFAULTVALUE : f.VALUE,
            xlabel: f.MANDATORY ? '&nbsp;<span class="asm-has-validation">*</span>' : "",
            callout: f.TOOLTIP,
            xattr: 'data-linktype="' + f.LINKTYPE + '"'
        };
        if (f.FIELDTYPE == additional.YESNO) { return tableform.render_check(v); }
        else if (f.FIELDTYPE == additional.TEXT) { return tableform.render_text(v); }
        else if (f.FIELDTYPE == additional.DATE) { return tableform.render_date(v); }
        else if (f.FIELDTYPE == additional.TIME) { return tableform.render_time(v); }
        else if (f.FIELDTYPE == additional.NOTES) { v.classes += " asm-textareafixed"; return tableform.render_textarea(v); }
        else if (f.FIELDTYPE == additional.NUMBER) { return tableform.render_number(v); }
        else if (f.FIELDTYPE == additional.MONEY) { return tableform.render_currency(v); }
        else if (f.FIELDTYPE == additional.ANIMAL_LOOKUP) { return tableform.render_animal(v); }
        else if (f.FIELDTYPE == additional.PERSON_LOOKUP) { return tableform.render_person(v); }
        else if (f.FIELDTYPE == additional.PERSON_SPONSOR) { v.personfilter = "sponsor"; return tableform.render_person(v); }
        else if (f.FIELDTYPE == additional.PERSON_VET) { v.personfilter = "vet"; return tableform.render_person(v); }
        else if (f.FIELDTYPE == additional.PERSON_ADOPTIONCOORDINATOR) { v.personfilter = "coordinator"; return tableform.render_person(v); }
        else if (f.FIELDTYPE == additional.LOOKUP) { 
            let opts = [], cv = common.trim(common.nulltostr(v.value));
            $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                vo = common.trim(vo);
                if (cv == vo) {
                    opts.push('<option selected="selected">' + vo + '</option>');
                }
                else {
                    opts.push('<option>' + vo + '</option>');
                }
            });
            v.options = opts.join("\n");
            return tableform.render_select(v); 
        }
        else if (f.FIELDTYPE == additional.MULTI_LOOKUP) {
            var mopts = [], mcv = common.trim(common.nulltostr(v.value)).split(",");
            $.each(f.LOOKUPVALUES.split("|"), function(io, vo) {
                vo = common.trim(vo);
                if ($.inArray(vo, mcv) != -1) {
                    mopts.push('<option selected="selected">' + vo + '</option>');
                }
                else {
                    mopts.push('<option>' + vo + '</option>');
                }
            });
            v.options = opts.join("\n");
            return tableform.render_selectmulti(v); 
        }
    },

    /**
     * Reset additional fields to their default values
     */
    reset_default: function(fields) {
        $.each(fields, function(i, v){
            $("#add_" + v.ID).val(v.DEFAULTVALUE);
            if(v.FIELDTYPE == additional.MONEY) { $("#add_" + v.ID).val(format.currency(v.DEFAULTVALUE)); }
        });
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

    /**
     * Validates all additional fields in a dialog and checks to
     * see if they are mandatory and if so whether or not they
     * are blank. Returns true if all is ok, or false if a field
     * fails a check.
     *
     * Deliberately ignores fields with the chooser class as this 
     * function is aimed at additional fields only.
     *
     * additionalclass: class that all additional fields should have ("additional" by default)
     * linktype: named additional field link type constant, eg: animal, movement, etc.
     */
    validate_mandatory_dialog: function(additionalclass) {
        var valid = true, message="";
        $("." + additionalclass).not(".chooser").each(function() {
            // only validate visible additional fields
            if ($(this).is(":visible")) {
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
                            tableform.dialog_error(message);
                            return false;
                        }
                    }
                }
            }
        });
        return valid;
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
