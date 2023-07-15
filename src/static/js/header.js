/*global $, Mousetrap, Path, _, asm, common, config, controller, format, html */
/*global header: true */

var header;

$(function() {

"use strict";

// If this is the login or database create page, don't do anything - they don't have headers, 
// but for the sake of making life easy, they still include this file.
if (common.current_url().indexOf("/login") != -1 ||
    common.current_url().indexOf("/database") != -1) {
    return;
}

/** Functions related to rendering and binding to events for the page
 *  header for all screens (menu, search, etc).
 */
header = {

    QUICKLINKS_SET: {
        1: ["animal_find", "asm-icon-animal-find", _("Find animal")],
        2: ["animal_new", "asm-icon-animal-add", _("Add a new animal")],
        3: ["log_new?mode=animal", "asm-icon-log", _("Add a log entry")],
        4: ["litters", "asm-icon-litter", _("Edit litters")],
        5: ["person_find", "asm-icon-person-find", _("Find person")],
        6: ["person_new", "asm-icon-person-add", _("Add a new person")],
        7: ["lostanimal_find", "asm-icon-animal-lost-find", _("Find a lost animal")],
        8: ["foundanimal_find", "asm-icon-animal-found-find", _("Find a found animal")],
        9: ["lostanimal_new", "asm-icon-animal-lost-add", _("Add a lost animal")],
        10: ["foundanimal_new", "asm-icon-animal-found-add", _("Add a found animal")],
        11: ["lostfound_match", "asm-icon-match", _("Match lost and found animals")],
        12: ["diary_edit_my?newnote=1", "asm-icon-diary", _("Add a diary note")],
        13: ["diary_edit_my", "asm-icon-diary", _("My diary notes")],
        14: ["diary_edit", "asm-icon-diary", _("All diary notes")],
        15: ["diarytasks", "asm-icon-diary-task", _("Edit diary tasks")],
        16: ["waitinglist_new", "asm-icon-waitinglist", _("Add an animal to the waiting list")],
        17: ["waitinglist_results", "asm-icon-waitinglist", _("Edit the current waiting list")],
        18: ["move_reserve", "asm-icon-reservation", _("Reserve an animal")],
        19: ["move_foster", "asm-icon-movement", _("Foster an animal")],
        20: ["move_adopt", "asm-icon-person", _("Adopt an animal")],
        21: ["move_deceased", "asm-icon-death", _("Mark an animal deceased")],
        22: ["move_book_recent_adoption", "asm-icon-movement", _("Return an animal from adoption")],
        23: ["move_book_recent_other", "asm-icon-movement", _("Return an animal from another movement")],
        24: ["move_book_reservation", "asm-icon-reservation", _("Reservation book")],
        25: ["move_book_foster", "asm-icon-book", _("Foster book")],
        26: ["move_book_retailer", "asm-icon-book", _("Retailer book")],
        27: ["vaccination?newvacc=1", "asm-icon-vaccination", _("Add a vaccination")],
        28: ["vaccination", "asm-icon-vaccination", _("Vaccination book")],
        29: ["medical?newmed=1", "asm-icon-medical", _("Add a medical regimen")],
        30: ["medical", "asm-icon-medical", _("Medical book")],
        32: ["publish_options", "asm-icon-settings", _("Set publishing options")],
        31: ["search?q=forpublish", "asm-icon-animal", _("Up for adoption")],
        33: ["search?q=deceased", "asm-icon-death", _("Recently deceased")],
        34: ["search?q=notforadoption", "asm-icon-notforadoption", _("Not for adoption")],
        35: ["search?q=onshelter", "asm-icon-animal", _("Shelter animals")],
        36: ["accounts", "asm-icon-accounts", _("Accounts")],
        37: ["donation_receive", "asm-icon-donation", _("Receive a payment")],
        38: ["move_transfer", "asm-icon-movement", _("Transfer an animal")],
        39: ["medicalprofile", "asm-icon-medical", _("Medical profiles")],
        40: ["shelterview", "asm-icon-location", _("Shelter view")],
        41: ["move_book_trial_adoption", "asm-icon-trial", _("Trial adoption book")],
        42: ["incident_new", "asm-icon-call", _("Report a new incident")],
        43: ["incident_find", "asm-icon-call", _("Find an incident")],
        44: ["incident_map", "asm-icon-map", _("Map of active incidents")],
        45: ["traploan?filter=active", "asm-icon-traploan", _("Trap loans")],
        46: ["calendarview", "asm-icon-calendar", _("Calendar view")],
        47: ["calendarview?ev=d", "asm-icon-calendar", _("Diary calendar")],
        48: ["calendarview?ev=vmt", "asm-icon-calendar", _("Medical calendar")],
        49: ["calendarview?ev=p", "asm-icon-calendar", _("Payment calendar")],
        50: ["calendarview?ev=ol", "asm-icon-calendar", _("Animal control calendar")],
        51: ["stocklevel", "asm-icon-stock", _("Stock Levels")],
        52: ["transport", "asm-icon-transport", _("Transport Book")],
        53: ["timeline", "asm-icon-calendar", _("Timeline")],
        54: ["staff_rota", "asm-icon-rota", _("Staff Rota")],
        55: ["move_reclaim", "asm-icon-movement", _("Reclaim an animal")],
        56: ["donation", "asm-icon-donation", _("Payment book")],
        57: ["calendarview?ev=c", "asm-icon-calendar", _("Clinic Calendar")],
        58: ["move_book_soft_release", "asm-icon-movement", _("Soft release book")],
        59: ["event_find", "asm-icon-event-find", _("Find Event")],
        60: ["event_new", "asm-icon-event-add", _("Add a new event")],
        61: ["animal_observations", "asm-icon-animal", _("Daily Observations")],
        62: ["boarding", "asm-icon-boarding", _("Boarding book")],
        63: ["calendarview?ev=b", "asm-icon-calendar", _("Boarding calendar")]
    },

    show_error: function(text, duration) {
        if (!duration) { duration = 20000; }
        $("#asm-topline-error-text").html(text);
        // INFO: use of stop() to cancel delay() if show_info/error is called again before delay has finished
        $("#asm-topline-error").stop().fadeIn("slow").delay(duration).fadeOut("slow");
    },

    hide_error: function() {
        $("#asm-topline-error").stop().hide();
    },

    show_info: function(text, duration) {
        if (!duration) { duration = 5000; }
        $("#asm-topline-info-text").html(text);
        $("#asm-topline-info").stop().fadeIn("slow").delay(duration).fadeOut("slow");
    },

    show_loading: function(text) {
        if (text !== undefined && text !== null && text !== "") {
            $("#asm-topline-loading-text").text(text);
        }
        $("#asm-topline-loading").dialog({
            dialogClass: 'dialog-no-title dialogshadow',
            height: "auto",
            modal: true
        });
    },

    hide_loading: function() {
        $("#asm-topline-loading").dialog("close");
    },

    /** Renders menu items as a flat structure in with one or more columns 
     *  h: html list to append to
     *  items: the list of menu items
     *  o: options 
     */
    menu_html_flat_renderer: function(h, items, o) {
        var c = 0, breakafter = o.breakafter || 25;
        h.push("<div class=\"asm-menu-columns\">");
        h.push("<div class=\"asm-menu-column\">");
        h.push("<ul class=\"asm-menu-list\">");
        $.each(items, function(i, v) {
            var permission = v[0], accesskey = v[1], classes = v[2], url = v[3], icon = v[4], display = v[5], iconhtml = "";
            if (asm.superuser || asm.securitymap.indexOf(permission + " ") != -1) {
                c += 1;
                if (url == "-") {
                    h.push("<hr class=\"asm-menu-body-rule\" />\n");
                }
                else if (url == "--break") {
                    h.push("</ul>\n</div>\n<div class=\"asm-menu-column\">\n<ul class=\"asm-menu-list\">");
                    c = 0;
                }
                else if (url == "--cat") {
                    if (c > breakafter) {
                        c = 0;
                        h.push("</ul>\n</div>\n<div class=\"asm-menu-column\">\n<ul class=\"asm-menu-list\">");
                    }
                    if (icon != "") { 
                        iconhtml = "<span class=\"asm-icon " + icon + "\"></span>\n";
                    }
                    h.push("<li class=\"asm-menu-category " + classes + "\">" + iconhtml + " " + display + "</li>");
                }
                else {
                    if (icon != "") {
                        iconhtml = "<span class=\"asm-icon " + icon + "\"></span>";
                    }
                    var accesskeydisp = "", target = "";
                    if (accesskey != "") {
                        accesskeydisp = "<span class=\"asm-hotkey\">" + accesskey.toUpperCase() + "</span>";
                        Mousetrap.bind(accesskey, function(e) {
                            common.route(url);
                            return false;
                        });
                    }
                    if (url.indexOf("report") == 0 && config.bool("ReportNewBrowserTab")) {
                        target = " target=\"_blank\"";
                    }
                    h.push("<li class=\"asm-menu-item " + classes + "\"><a href=\"" + url + "\" " + target + ">" + iconhtml + " " + display + accesskeydisp + "</a></li>");
                }
            }
        });
        h.push("</ul>\n</div>\n</div>\n");
    },

    /** Renders menu items where each category becomes an accordion section 
     * h: The html list to append to
     * items: The menu items
     * name: The display name of the menu
     */
    menu_html_accordion_renderer: function(h, items, name) {
        var openac = false, outputhead = false;
        $.each(items, function(i, v) {
            var permission = v[0], accesskey = v[1], classes = v[2], url = v[3], icon = v[4], display = v[5], iconhtml = "";
            if (asm.superuser || asm.securitymap.indexOf(permission + " ") != -1) {
                if (url == "--cat") {
                    if (!outputhead) { 
                        h.push("<div class=\"asm-menu-accordion asm-menu-accordion-" + name + "\">");
                        outputhead = true;
                    }
                    if (openac) { 
                        h.push("</ul></div>"); 
                    }
                    if (icon != "") { 
                        iconhtml = "<span class=\"asm-icon " + icon + "\"></span>\n";
                    }
                    h.push("<h3>" + iconhtml + " " + display + "</h3>");
                    h.push("<div>");
                    h.push('<ul class="asm-menu-list">');
                    openac = true;
                }
                else {
                    if (icon != "") {
                        iconhtml = "<span class=\"asm-icon " + icon + "\"></span>";
                    }
                    var accesskeydisp = "", target = "";
                    if (accesskey != "") {
                        accesskeydisp = "<span class=\"asm-hotkey\">" + accesskey.toUpperCase() + "</span>";
                        Mousetrap.bind(accesskey, function(e) {
                            common.route(url);
                            return false;
                        });
                    }
                    if (url.indexOf("report") == 0 && config.bool("ReportNewBrowserTab")) {
                        target = " target=\"_blank\"";
                    }
                    h.push("<li class=\"asm-menu-item " + classes + "\"><a href=\"" + url + "\" " + target + ">" + iconhtml + " " + display + accesskeydisp + "</a></li>");
                }
            }
        });
        h.push("</ul>\n</div>\n</div>");
    },

    menu_html: function() {
        var menu = [], menus = [], self = this;
        // Go through each menu and render appropriately
        $.each(asm.menustructure, function(im, vm) {
            var permission = vm[0], name = vm[1], display = vm[2], items = vm[3];
            if (asm.superuser || asm.securitymap.indexOf(permission + " ") != -1) {
                // Render the menu button and body
                menu.push("<div id=\"asm-menu-" + name + "\" class=\"asm-menu-icon\">" + display + "</div>");
                menus.push("<div id=\"asm-menu-" + name + "-body\" class=\"asm-menu-body\">");
                // If the option is on or there are more than 120 items to show, 
                // render report and mail merge menus in accordions by category instead
                if ((config.bool("ReportMenuAccordion") || items.length > 120) && (name == "reports" || name == "mailmerge")) {
                    self.menu_html_accordion_renderer(menus, items, name);
                }
                else {
                    self.menu_html_flat_renderer(menus, items, { breakafter: 25 });
                }
                menus.push("</div>");
            }
        });
        return [ menu.join(""), menus.join("\n") ];
    },

    /** Finds all menu widgets (have classes of asm-menu-icon and asm-menu-body) and
     * initialises them into dropdown menus. This should be called by the render
     * function after menu_html so that the DOM contains all necessary elements.
     */
    menu_widgets: function() {

        $(".asm-menu-icon").asmmenu();
        $(".asm-menu-accordion").accordion({ active: false, collapsible: true, heightStyle: "content" });

        // Hide any publishers that are not enabled
        var ep = config.str("PublishersEnabled");
        $.each(asm.publishers, function(k, v) {
            if (ep.indexOf(k) == -1) {
                $("#asm-menu-publishing-body [href='publish?mode=" + k + "']").closest("li").hide(); 
            }
        });

        try {
            // If movements are disabled, remove the move menu
            if (config.bool("DisableMovements")) {
                $("#asm-menu-move").closest("td").hide();
            }
            // If lost and found is disabled, hide menu entries for it
            if (config.bool("DisableLostAndFound")) {
                $(".taglostfound").hide();  
            }
            // If boarding is disabled, hide menu entries for it
            if (config.bool("DisableBoarding")) {
                $(".tagboarding").hide();
            }
            // If clinic is disabled, hide menu entries for it
            if (config.bool("DisableClinic")) {
                $(".tagclinic").hide();
            }
            // If retailer is disabled, hide menu entries for it
            if (config.bool("DisableRetailer")) {
                $(".tagretailer").hide();
            }
            // If rota is disabled, hide menu entries for it
            if (config.bool("DisableRota")) {
                $(".tagrota").hide();
            }
            // If transport is disabled, hide menu entries for it
            if (config.bool("DisableTransport")) {
                $(".tagtransport").hide();
            }
            // If trial adoptions are not enabled, hide any menu entries
            if (!config.bool("TrialAdoptions")) {
                $(".tagtrial").hide();
            }
            // Same for soft releases
            if (!config.bool("SoftReleases")) {
                $(".tagsoftrelease").hide();
            }
            // Same for waiting list
            if (config.bool("DisableWaitingList")) {
                $(".tagwaitinglist").hide();
            }
            // Document repo
            if (config.bool("DisableDocumentRepo")) {
                $(".tagdocumentrepo").hide();
            }
            // Online forms
            if (config.bool("DisableOnlineForms")) {
                $(".tagonlineform").hide();
            }
            // Animal Control
            if (config.bool("DisableAnimalControl")) {
                $(".taganimalcontrol").hide();
            }
            // Trap Loans
            if (config.bool("DisableTrapLoan")) {
                $(".tagtraploan").hide();
            }
            // Animal control header (either animal control or incidents enabled)
            if (config.bool("DisableTrapLoan") && config.bool("DisableAnimalControl")) {
                $(".taganimalcontrolheader").hide();
            }
            // Accounts
            if (config.bool("DisableAccounts")) {
                $(".tagaccounts").hide();
                // If nothing is enabled, hide the whole financial menu
                if (config.bool("DisableStockControl")) { $("#asm-menu-financial").hide(); }
            }
            // Events
            if (config.bool("DisableEvents")){
                $(".tagevent").hide();
            }
            // Stock Control
            if (config.bool("DisableStockControl")) {
                $(".tagstock").hide();
            }
            // HMRC Gift Aid is en_GB only
            if (asm.locale != "en_GB") {
                $(".taggb").hide();
            }
        }
        catch (nc) {}
        $(".asm-menu-icon").show();
    },

    /**
     * Renders quicklinks as html
     */
    quicklinks_html:  function() {
        let s = "";
        let qls = config.str(asm.user + "_QuicklinksID");
        if (!qls) { qls = config.str("QuicklinksID"); } 
        if (!qls) { return ""; }
        $.each(qls.split(","), function(i, v) {
            var b = header.QUICKLINKS_SET[parseInt(v, 10)];
            if (!b) { return; }
            var url = b[0], image = b[1], text = b[2];
            s += "<a ";
            s += "href='" + url + "'>";
            if (image != "") {
                s += "<span class='asm-icon " + image + "'></span> ";
            }
            else {
                s += "<span class='asm-icon-blank'></span> ";
            }
            s += text + "</a>";
        });
        return s;
    },

    /**
     * Render HTML components of the header
     */
    render: function() {
        var homeicon = "static/images/logo/icon.svg",
            mh = this.menu_html(),
            menubuttons = mh[0],
            menubodies = mh[1];
        if (asm.hascustomlogo) {
            homeicon = "image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/logo.jpg";
        }
        var h = [
            '<div id="asm-topline" class="no-print" style="display: none">',
                '<div class="topline-element">',
                    '<a id="asm-topline-logo" href="main" title="' + _("Home") + '"><img src="' + homeicon + '" /></a>',
                '</div>',
                ' ',
                menubuttons,
                ' ',
                '<div class="topline-element">',
                    '<span style="white-space: nowrap">',
                    '<input id="topline-q" name="q" type="search" class="asm-textbox" title="' + 
                        html.title("ALT+SHIFT+S " + _("filters") + ": " +
                            "a:animal, ac:animalcontrol, p:person, wl:waitinglist, la:lostanimal, fa:foundanimal, " + 
                            "li:licence, lo:logs, vo:voucher " +
                            _("keywords") + ": " + "onshelter/os, notforadoption, aco, banned, donors, deceased, vets, " + 
                            "retailers, staff, fosterers, volunteers, homecheckers, members, drivers, overduedonations, " +
                            "signed, unsigned, activelost, activefound") +
                        '" placeholder="' + html.title(_("Search")) + '" />',
                    '<button id="searchgo" style="display: none">' + _("Search") + '</button>',
                    '</span>',
                '</div>',
                ' ',
                '<div class="topline-element">',
                    '<div id="asm-topline-user" class="asm-menu-icon"><img id="asm-topline-flag" /> <span id="asm-topline-username"></span></div>',
                '</div>',
                '<div class="topline-element">',
                    '<div id="asm-topline-help" class="asm-menu-icon">' + html.icon("callout") + '</div>',
                '</div>',
            '</div>',
            menubodies,
            '<div id="asm-topline-user-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li class="asm-menu-category">' + (asm.userreal ? asm.userreal : asm.user) + '</li>',
                    '<li id="asm-mysmcom" class="asm-menu-item"><a href="smcom_my" target="_blank"><nobr><span class="asm-icon asm-icon-logo"></span> ' + _("My sheltermanager.com account") + '</nobr></a></li>',
                    '<li id="asm-chpassword" class="asm-menu-item"><a href="change_password"><nobr><span class="asm-icon asm-icon-auth"></span> ' + _("Change Password") + '</nobr></a></li>',
                    '<li id="asm-chusersettings" class="asm-menu-item"><a href="change_user_settings"><nobr><span class="asm-icon asm-icon-settings"></span> ' + _("Change User Settings") + '</nobr></a></li>',
                    '<li id="asm-logout" class="asm-menu-item"><a href="logout"><nobr><span class="asm-icon asm-icon-logout"></span> ' + _("Logout") + '</nobr></a></li>',
                '</ul>',
            '</div>',
            '<div id="asm-topline-help-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li class="asm-menu-category">' + _("Help") + '</li>',
                    '<li class="asm-menu-item asm-manual asm-manualhtml"><a href="#" target="_blank"><span class="asm-icon asm-icon-help"></span> <nobr>' + _("View Manual") + '</nobr></a></li>',
                    '<li class="asm-menu-item asm-manual asm-manualpdf"><a href="#" target="_blank"><span class="asm-icon asm-icon-pdf"></span> <nobr>' + _("Printable Manual") + '</nobr></a></li>',
                    '<li class="asm-menu-item asm-manual asm-manualvideo"><a href="#" target="_blank"><nobr><span class="asm-icon asm-icon-youtube"></span> ' + _("View Training Videos") + '</nobr></a></li>',
                    '<li class="asm-menu-item asm-manual asm-manualfaq"><a href="#" target="_blank"><nobr><span class="asm-icon asm-icon-faq"></span> ' + _("Frequently Asked Questions") + '</nobr></a></li>',
                '</ul>',
            '</div>',
            '<div id="asm-topline-error" style="display: none" class="ui-widget">',
                '<div class="ui-state-error ui-corner-all">',
                    '<p style="padding: 5px">',
                        '<span class="ui-icon ui-icon-alert"></span>',
                        '<strong><span id="asm-topline-error-text"></span></strong>',
                    '</p>',
                '</div>',
            '</div>',
            '<div id="asm-topline-info" style="display: none" class="ui-widget">',
                '<div class="ui-state-highlight ui-corner-all">',
                    '<p style="padding: 5px">',
                        '<span class="ui-icon ui-icon-info"></span>',
                        '<strong><span id="asm-topline-info-text"></span></strong>',
                    '</p>',
                '</div>',
            '</div>',
            '<div id="asm-topline-locked" style="display: none" class="ui-widget">',
                '<div class="ui-state-error ui-corner-all">',
                    '<p style="padding: 5px">',
                        '<span class="ui-icon ui-icon-locked"></span>',
                        '<strong><span id="asm-topline-locked-text">',
                        _("This database is locked and in read-only mode. You cannot add, change or delete records."),
                        asm.smcom && asm.useraccount != "demo" ? ' ' + _("To continue using ASM, please renew {0}")
                            .replace("{0}", asm.smcompaymentlink) : "",
                        '</span></strong>',
                    '</p>',
                '</div>',
            '</div>',
            '<div class="emergencynotice ui-widget" style="display: none">',
                '<div class="ui-state-error ui-corner-all">',
                    '<p style="padding: 5px">',
                        '<span class="ui-icon ui-icon-alert"></span>',
                        '<span class="emergencynoticetext"></span>',
                    '</p>',
                '</div>',
            '</div>',
            '<div id="linkstips" class="no-print ui-state-highlight ui-corner-all" style="display: none; padding-left: 5px; padding-right: 5px">',
                '<p id="quicklinks" class="asm-quicklinks" style="display: none"><span class="ui-icon ui-icon-bookmark"></span>',
                    '<span id="quicklinks-label">' + _("Quick Links") + '</span>',
                    this.quicklinks_html(),
                '</p>',
                '<p id="tips" style="display: none"><span class="ui-icon ui-icon-lightbulb"></span>',
                    '<span style="font-weight: bold">' + _("Did you know?") + '</span><br/>',
                    '<span id="tip"></span>',
                '</p>',
            '</div>',
            '<div id="dialog-textarea-zoom" style="display: none" title="">',
                '<input id="textarea-zoom-id" type="hidden" />',
                '<textarea id="textarea-zoom-area" style="width: 98%; height: 98%;"></textarea>',
            '</div>',
            '<div id="dialog-unsaved" style="display: none" title="' + _("Unsaved Changes") + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("You have unsaved changes, are you sure you want to leave this page?"),
                '</p>',
            '</div>',
            '<div id="asm-topline-loading" style="display: none" title="' + _("Loading...") + '">',
                '<p class="centered">',
                    '<img style="height: 48px" src="static/images/wait/rolling_3a87cd.svg" />',
                    '<br /><br />',
                    '<span id="asm-topline-loading-text">' + _("Loading...") + '</span>',
                '</p>',
            '</div>',
            '<div id="asm-body-container"></div>'
        ];
        return h.join("");
    },

    /** Shows quicklinks for the main/home page */
    quicklinks_main: function() {
        if (config.bool("QuicklinksHomeScreen")) {
            $("#linkstips").show();
            $("#quicklinks").show();
            $("#quicklinks").on("mouseover", "a", function() {
                $(this).addClass("ui-state-hover");
            });
            $("#quicklinks").on("mouseout", "a", function() {
                $(this).removeClass("ui-state-hover");
            });
            // If there are more than our default items, hide the text to save space
            if (config.str("QuicklinksID").split(",").length > 7) {
                $("#quicklinks-label").hide();
            }
        }
        if (config.has() && !config.bool("DisableTips")) {
            $("#tips").show();
        }
    },

    quicklinks_other: function() {
        // All other non-login screens
        if (config.bool("QuicklinksAllScreens")) {
            $("#linkstips").show();
            $("#quicklinks").show();
            $("#quicklinks").on("mouseover", "a", function() {
                $(this).addClass("ui-state-hover");
            });
            $("#quicklinks").on("mouseout", "a", function() {
                $(this).removeClass("ui-state-hover");
            });
            // If there are more than our default items, hide the text to save space
            if (config.str("QuicklinksID").split(",").length > 7) {
                $("#quicklinks-label").hide();
            }
        }
    },

    quicklinks_show: function(path) {
        // Deal with whether we're showing quicklinks and tips
        $("#linkstips, #quicklinks, #tips").hide();
        if (!path) { path = common.current_url(); } 
        if (config.has() && path.indexOf("main") != -1) {
            this.quicklinks_main();
        }
        else if (path.indexOf("login") == -1) {
            this.quicklinks_other();
        }
    },

    bind: function() {
        
        var timezone = config.str("Timezone");
        if (timezone.indexOf("-") == -1) {
            timezone = "+" + timezone;
        }
        if (timezone.indexOf(".") == -1) {
            timezone += ":00";
        }
        else {
            timezone = timezone.replace(".25", ":15");
            timezone = timezone.replace(".5", ":30");
            timezone = timezone.replace(".75", ":45");
        }

        // Set flag icon
        $("#asm-topline-flag")
            .attr("src", "static/images/flags/" + asm.locale + ".png")
            .attr("title", asm.locale + " " + timezone);

        // Set user name
        $("#asm-topline-username").html(asm.user);

        Path.change(function(path) {
            header.hide_error();
            header.quicklinks_show(path);
        });

        this.quicklinks_show();
        this.bind_search();

        // Load the manual links
        $(".asm-manual").hide();
        if (asm.manualhtml) { $(".asm-manualhtml").show().find("a").prop("href", asm.manualhtml); }
        if (asm.manualpdf) { $(".asm-manualpdf").show().find("a").prop("href", asm.manualpdf); }
        if (asm.manualvideo) { $(".asm-manualvideo").show().find("a").prop("href", asm.manualvideo); }
        if (asm.manualfaq) { $(".asm-manualfaq").show().find("a").prop("href", asm.manualfaq); }
        
        // Hide the error and info boxes
        $("#asm-topline-error").hide();
        $("#asm-topline-info").hide();

        // Hide the My sheltermanager.com menu option for non-smcom and if this
        // user isn't the master user (same username as the database)
        if (!asm.smcom || asm.user != asm.useraccount) {
            $("#asm-mysmcom").hide();
        }

        // Hide the change user settings/password options for smcom demo database
        if (asm.smcom && asm.useraccount == "demo") {
            $("#asm-chusersettings, #asm-chpassword").hide();
        }

        // Hide the logout link if we're in the mobile app
        if (asm.mobileapp) {
            $("#asm-logout").hide();
        }

        // If the database is locked, show it
        if (config.has() && config.bool("SMDBLocked")) {
            $("#asm-topline-locked").fadeIn().delay(20000).slideUp();
        }

        // If there's an emergency notice, show it
        try {
            if (controller && controller.emergencynotice) {
                $(".emergencynoticetext").html(controller.emergencynotice);
                $(".emergencynotice").fadeIn();
            }
        }
        catch(err) {} 
    },

    bind_search: function() {

        const keywords = [ "activelost", "activefound", "donors", "deceased", "hold", "holdtoday", 
            "notforadoption", "onshelter", "quarantine", "forpublish", "reservenohomecheck", "notmicrochipped",
            "aco", "banned", "donors", "drivers", "homechecked", "homecheckers", 
            "fosterers", "homecheckers", "members", "people", "retailers", "shelters", "staff", 
            "vets", "volunteers" ] ;

        let previous = common.local_get("asmsearch").split("|");
        let searches = keywords.concat(previous);

        const dosearch = function(e) {
            // If the search is blank, do nothing
            let term = $("#topline-q").val();
            if (!term) { return; }
            // If we haven't seen this search term before, add it to our set
            if ($.inArray(term, previous) == -1) {
                previous.push(term);
                common.local_set("asmsearch", previous.join("|"));
            }
            // Use form dirty handling to make sure we're safe to leave this screen
            // validate.a_click_handler will handle routing to the URL
            if (validate.active && (!validate.a_click_handler(e, "search?q=" + encodeURIComponent(term)))) { 
                return;
            }
            common.route("search?q=" + encodeURIComponent(term));
        };

        // Search autocompletes to keywords and previous searches
        $("#topline-q").autocomplete({ source: searches, minLength: 3 });

        // Pressing enter starts the search
        $("#topline-q").keypress(function(e) {
            if (e.which == 13) {
                dosearch(e);
                return false;
            }
        });

        // Make ALT+SHIFT+S focus the search widget
        Mousetrap.bind([ "alt+shift+s" ], function() {
            $("#topline-q").focus();
            return false;
        });

        // If the option is on, show the go button for searching
        if (config.has() && config.bool("ShowSearchGo")) {
            $("#searchgo")
                .button({ icons: { primary: "ui-icon-search" }, text: false })
                .click(dosearch)
                .show();
        }
    }

};

// Render the page header above any content in the body tag
$("body").prepend(header.render());

// Setup the menu widgets
header.menu_widgets();
header.bind();

common.apply_label_overrides("topline");
$("#asm-topline").show();

});
