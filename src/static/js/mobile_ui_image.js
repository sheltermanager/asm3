/*global $, jQuery, controller */
/*global asm, common, config, format, html */
/*global _, mobile */
/*global mobile_ui_image: true */

"use strict";

const mobile_ui_image = {

    render_slider: function(rows, id) {
        let h = '<div id="' + id + '-imageslider">';
        let body = '<div id="' + id + '-imagesliderbody">' +
            '<a id="' + id + '-anchor" href="#" target="_blank">' +
            '<img id="' + id + '-image" style="max-width: 100%;" src=""></a>' +
            '<div id="' + id + '-notes"></div>' +
            '</div>';
        let head = '<div id="' + id + '-imagesliderheader" style="height: 120px; ' +
            'overflow-x: scroll; overflow-y: hidden; white-space: nowrap;">';
        head += '<div style="position: relative; display: inline-block; height: 100px; width: 50px; margin-right: 10px; margin-bottom: 10px;">' +
                '<div style="position: absolute; padding-left: 5px; padding-right: 5px;">' +
                '<button id="' + id + '-button-camera" class="btn btn-primary mt-1" style="display: block;margin-top: 0 !important;">' + 
                    '<i class="bi-camera media-button-icon"></i>' +
                    '<span class="spinner-border spinner-border-sm media-button-spinner" role="status" style="display: none;"></span>' +
                '</button>' +
                '<button id="' + id + '-button-gallery" class="btn btn-secondary mt-1" style="display: block;">' +
                    '<i class="bi-card-image media-button-icon"></i>' + 
                    '<span class="spinner-border spinner-border-sm media-button-spinner" role="status" style="display: none;"></span>' +
                '</button>' +
                '</div></div>' + 
                '<input id="' + id + '-input-camera" type="file" capture="environment" accept="image/*" style="display: none;">' +
                '<input id="' + id + '-input-gallery" type="file" accept="image/*" multiple="multiple" style="display: none;">';
        $.each(rows, function(i, row) {
            if (row.MEDIAMIMETYPE != 'image/jpeg') { return; }
            
            head += mobile_ui_image.render_thumbnail(row.ID, id, format.date(row.DATE), html.title(row.MEDIANOTES));
        });
        head += '</div>';
        return h + head + body + '</div>';
    },

    render_thumbnail: function(mid, id, date="", notes="") {
        if (date == "") { date = format.date_now(); }
        let newthumbnail = '<div class="media-thumb" style="position: relative; border-style: solid; border-width: 1px; ' +
        'border-color: #ffffffff; display: inline-block; height: 100px; width: 100px; ' +
        'background: url(\'/image?db=' + asm.useraccount + '&mode=media&id=' + mid + '\'); ' +
        'background-size: cover; background-position: center center; ' +
        'margin-right: 10px; margin-bottom: 10px;" ' +
        'data-imageid="' + mid + '" data-description="' + notes + '">' +
        '<div style="position: absolute;width:98px;bottom: 0;left: 0;background-color: white;" align="center">' + 
        date + '</div>' +
        '</div>';
        return newthumbnail;
    }

};
