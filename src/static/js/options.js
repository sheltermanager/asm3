/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, mapping, validate */
/*global MASK_VALUE */

$(function() {

    "use strict";

    const options = {

        /** Where we have a list of pairs, first is value, second is label */
        two_pair_options: function(o, isflag) {
            let s = [];
            $.each(o, function(i, v) {
                let ds = "";
                if (isflag) {
                    ds = 'data-style="background-image: url(static/images/flags/' + v[0] + '.png)"';
                }
                s.push('<option value="' + v[0] + '" ' + ds + '>' + v[1] + '</option>');
            });
            return s.join("\n");
        },

        /** Sorts a list of pairs by the second element in each list */
        pair_sort_second: function(l) {
            return l.sort(function(a, b) {
                if (a[1] < b[1]) return -1;
                if (a[1] > b[1]) return 1;
                return 0;
            });
        },

        /** Reorders the list l and moves the selected items in configitem to the front */
        pair_selected_to_front: function(l, configitem) {
            let ci = configitem.split(",").reverse();
            $.each(ci, function(i, v) {
                v = String(v).trim();
                $.each(l, function(iv, vl) {
                    if (vl[0] == v) {
                        l.splice(iv, 1); // Remove matching element from the list
                        l.splice(0, 0, [ vl[0], vl[1] ]); // Reinsert it at the front
                        return false; // Break the loop
                    }
                });
            });
            return l;
        },

        /** Renders the list of quicklink options */
        quicklink_options: function() {
            let ql = [];
            $.each(header.QUICKLINKS_SET, function(k, v) {
                ql.push([ k, v[2] ]);
            });
            ql = this.pair_sort_second(ql);
            ql = this.pair_selected_to_front(ql, config.str("QuicklinksID"));
            return this.two_pair_options(ql);
        },

        watermark_colors: [
            "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond", "blue",
            "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk",
            "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgrey", "darkgreen", "darkkhaki",
            "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue",
            "darkslategray", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dimgrey",
            "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod",
            "gray", "grey", "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender",
            "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow",
            "lightgray", "lightgrey", "lightgreen", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray",
            "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon",
            "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue",
            "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin",
            "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
            "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue",
            "purple", "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen",
            "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen", "steelblue",
            "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow", "yellowgreen",
        ],

        render: function() {
            const emblemvalues = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@$%^&*!?#",
                emblemglyphs = [
                    8592,  // Left arrow
                    8593,  // Up arrow
                    8594,  // Right arrow
                    8595,  // Down arrow
                    8984,  // Place of interest
                    8987,  // Hourglass
                    8962,  // House
                    9113,  // Print
                    9114,  // Clear screen
                    9200,  // Alarm clock
                    9728,  // Sun
                    9729,  // Cloud
                    9731,  // Snowman
                    9733,  // Star
                    9742,  // Telephone
                    9760,  // Skull/Crossbones
                    9762,  // Radioactive
                    9763,  // Biohazard
                    9774,  // Peace
                    9785,  // Sad face
                    9787,  // Smiley face
                    9792,  // Female
                    9794,  // Male
                    9850,  // Recycling
                    9855,  // Disabled
                    9872,  // White flag
                    9873,  // Black flag
                    9875,  // Anchor
                    9877,  // Medical
                    9878,  // Scales
                    9888,  // Warning
                    9889,  // High Voltage
                    9917,  // Soccer ball
                    9951,  // Truck
                    9983,  // Striped flag
                    9986,  // Scissors
                    9989,  // White heavy check mark (green)
                    9990,  // Telephone location
                    9992,  // Airplane
                    9999,  // Pencil
                    10003, // Tick
                    10004, // Cross
                    10024, // Sparkles
                    10052, // Snowflake
                    10062, // White heavy cross
                    10084, // Heavy heart
                    127798, // Spicy pepper
                    127960, // House - buildings
                    127968, // House - building
                    128008, // Cat
                    128021, // Dog
                    128049, // Cat Face
                    128054, // Dog Face,
                    128137, // Syringe
                    128138, // Pill
                    128169, // Poop
                    128266, // Speaker with high volume
                    128272, // Lock with key
                    128308, // Red circle
                    128309, // Blue circle
                    128992, // Orange circle
                    128993, // Yellow circle
                    128994, // Green circle
                    128995, // Purple circle
                    128996, // Brown circle
                    128997, // Red square
                    128998, // Blue square
                    128999, // Orange square
                    129000, // Yellow square
                    129001, // Green square
                    129002, // Purple square
                    129003, // Brown square
                    128571, // Cat with heart eyes
                    129379, // Bowl and spoon
                    129387, // Can of food
                    129440, // Microbe
                    129460, // Bone
                    129514, // Test tube
                    129516, // DNA
                    129713, // Worm
                    129745  // Bell pepper
                ],
                emblemoptions = [],
                condoptions = '<option></option><option value="has">' + _("if animal has") + 
                    '</option><option value="not">' + _("if animal does not have") + '</option>';
            $.each(emblemglyphs, function(i, v) { emblemoptions.push('<option value="&#' + v + ';">&#' + v + ';</option>'); });
            for (let i = 0; i < emblemvalues.length; i=i+1) { emblemoptions.push('<option>' + emblemvalues[i] + '</option>'); }

            return [
                html.content_header(_("System Options")),
                tableform.buttons_render([
                    { id: "save", icon: "save", text: _("Save") }
                 ], { centered: false }),
                tableform.render_tabs([
                    { id: "tab-shelterdetails", title: _("Shelter Details"), fields: [
                        { id: "organisation", post_field: "Organisation", label: _("Organization"), type: "text", doublesize: true },
                        { id: "address", post_field: "OrganisationAddress", label: _("Address"), type: "textarea", doublesize: true },
                        { id: "city", post_field: "OrganisationTown", label: _("City"), type: "text" },
                        { id: "state", post_field: "OrganisationCounty", label: _("State"), type: "text", hideif: function() { return config.bool("USStateCodes"); }},
                        { id: "state", post_field: "OrganisationCounty", label: _("State"), type: "select", options: html.states_us_options(), hideif: function() { if (config.bool("USStateCodes") == true) {return false;} else {return true;} }},
                        { id: "zipcode", post_field: "OrganisationPostcode", label: _("Zipcode"), type: "text" },
                        { id: "country", post_field: "OrganisationCountry", label: _("Country"), type: "text" },
                        { id: "telephone", post_field: "OrganisationTelephone", label: _("Telephone"), type: "phone" },
                        { id: "telephone2", post_field: "OrganisationTelephone2", label: _("Telephone"), type: "phone" },
                        { id: "timezone", post_field: "Timezone", label: _("Server clock adjustment"), type: "select",
                            options: [
                                "-12|-12:00",
                                "-11|-11:00",
                                "-10|-10:00",
                                "-9.5|-09:30",
                                "-8|-08:00 (USA PST)",
                                "-7|-07:00 (USA MST)",
                                "-6|-06:00 (USA CST)",
                                "-5|-05:00 (USA EST)",
                                "-4|-04:00",
                                "-3.5|-03:30",
                                "-3|-03:00",
                                "-2.5|-02:30",
                                "-2|-02:00",
                                "-1|-01:00",
                                "0|" + ("No adjustment") + " (GMT/UTC)",
                                "1|+01:00 (CET)",
                                "2|+02:00 (EET)",
                                "3|+03:00 (FET)",
                                "3.5|+03:30",
                                "4|+04:00",
                                "4.5|+04:30",
                                "5|+05:00",
                                "5.5|+05:30 (IST)",
                                "5.75|+05:45",
                                "6|+06:00",
                                "6.5|+06:30",
                                "7|+07:00",
                                "8|+08:00 (AWST)",
                                "8.5|+08:30",
                                "8.75|+08:45",
                                "9|+09:00 (JST)",
                                "9.5|+09:30 (ACT)",
                                "10|+10:00 (AET)",
                                "10.5|+10:30",
                                "11|+11:00",
                                "12|+12:00",
                                "12.75|+12:45",
                                "13|+13:00",
                                "13.75|+13:45",
                                "14|+14:00",

                            ], rowclose: false
                        },
                        { id: "timezonedst", post_field: "TimezoneDST", label: _("auto adjust for daylight savings"), type: "check", justwidget: true },
                        { type: "rowclose" },
                        { id: "olocale", post_field: "Locale", label: _("Locale"), type: "select", options: this.two_pair_options(controller.locales, true), callout: _("The locale determines the language ASM will use when displaying text, dates and currencies."), classes: "asm-iconselectmenu" },
                        { type: "nextcol" },
                        { type: "raw", justwidget: true, markup: '<tr><td colspan="2" style="min-width: 474px;"><div id="embeddedmap" style="z-index: 1; width: 100%; height: 300px; color: #000"></div></td></tr>'},
                    ]},
                    { id: "tab-accounts", title: _("Accounts"), fields: [
                        { id: "disableaccounts", post_field: "rc:DisableAccounts", label: _("Enable accounts functionality"), type: "check", fullrow: true },
                        { id: "createdonations", post_field: "CreateDonationTrx", label: _("Creating payments and payments types creates matching accounts and transactions"), type: "check", fullrow: true },
                        { id: "createcost", post_field: "CreateCostTrx", label: _("Creating cost and cost types creates matching accounts and transactions"), type: "check", fullrow: true },
                        { id: "donationtrxoverride", post_field: "DonationTrxOverride", label: _("When receiving payments, allow the deposit account to be overridden"), type: "check", fullrow: true },
                        { id: "donationquantities", post_field: "DonationQuantities", label: _("When receiving payments, allow a quantity and unit price to be set"), type: "check", fullrow: true },
                        { id: "donationfees", post_field: "DonationFees", label: _("When receiving payments, allow a transaction fee to be set"), type: "check", fullrow: true },
                        { id: "vatenabled", post_field: "VATEnabled", label: _("When receiving payments, allow recording of sales tax"), type: "check", fullrow: true },
                        { id: "vatexclusive", post_field: "VATExclusive", label: _("When calculating sales tax, assume the payment amount is net and add it"), type: "check", fullrow: true },
                        { id: "donationdateoverride", post_field: "DonationDateOverride", label: _("When receiving multiple payments, allow the due and received dates to be set"), type: "check", fullrow: true },
                        { id: "accountperiodtotals", post_field: "AccountPeriodTotals", label: _("Only show account totals for the current period, which starts on "), type: "check", fullrow: true, xmarkup: '<input type="text" class="asm-field asm-textbox asm-datebox controlshadow controlborder" id="accountingperiod" data-post="AccountingPeriod" autocomplete="off">' },
                        { id: "defaulttrxview", post_field: "DefaultAccountViewPeriod", label: _("Default transaction view"), type: "select", options:[
                            "0|" + _("This Month"),
                            "1|" + _("This Week"),
                            "2|" + _("This Year"),
                            "3|" + _("Last Month"),
                            "4|" + _("Last Week"),
                        ] },
                        { id: "csourceaccount", post_field: "CostSourceAccount", label: _("Default source account for costs"), type: "select", options: html.list_to_options(controller.accounts, "ID", "CODE") },
                        { id: "destinationaccount", post_field: "DonationTargetAccount", label: _("Default destination account for payments"), type: "select", options: html.list_to_options(controller.accounts, "ID", "CODE") },
                        { id: "vataccount", post_field: "DonationVATAccount", label: _("Income account for sales tax"), type: "select", options: html.list_to_options(controller.accountsinc, "ID", "CODE") },
                        { id: "feeaccount", post_field: "DonationFeeAccount", label: _("Expense account for transaction fees"), type: "select", options: html.list_to_options(controller.accountsexp, "ID", "CODE") },
                        { id: "mapdt1", xattr: 'data-idx="1"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac1" data-idx="1" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt2", xattr: 'data-idx="2"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac2" data-idx="2" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt3", xattr: 'data-idx="3"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac3" data-idx="3" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt4", xattr: 'data-idx="4"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac4" data-idx="4" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt5", xattr: 'data-idx="5"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac5" data-idx="5" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt6", xattr: 'data-idx="6"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac6" data-idx="6" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt7", xattr: 'data-idx="7"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac7" data-idx="7" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt8", xattr: 'data-idx="8"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac8" data-idx="8" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                        { id: "mapdt9", xattr: 'data-idx="9"', classes: "donmap", label: _("Payments of type"), type: "select", options: '<option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), 
                            xmarkup: ' ' + _("are sent to") + ' <select id="mapac9" data-idx="9" class="asm-selectbox"><option value="-1">' + _("[None]") + '</option>' + html.list_to_options(controller.accounts, "ID", "CODE") + '</select>'
                        }, 
                    ]},
                    { id: "tab-adding", title: _("Add Animal"), fields: [
                        { id: "aashowbreed", post_field: "AddAnimalsShowBreed", label: _("Show the breed fields"), type: "check" },
                        { type: "raw", markup: "<br>" },
                        { id: "singlebreed", post_field: "UseSingleBreedField", label: _("Use a single breed field"), type: "check" },
                        { type: "raw", markup: "OR only show the second breed field for these species of animals" },
                        { id: "crossbreedspecies", post_field: "CrossbreedSpecies", type: "selectmulti", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") },
                        { type: "raw", markup: "<br>" },
                        { id: "aashowcoattype", post_field: "AddAnimalsShowCoatType", label: _("Show the coat type field"), type: "check" },
                        { id: "aashowcolour", post_field: "AddAnimalsShowColour", label: _("Show the color field"), type: "check" },
                        { id: "aashowfee", post_field: "AddAnimalsShowFee", label: _("Show the adoption fee field"), type: "check" },
                        { id: "aashowlocation", post_field: "AddAnimalsShowLocation", label: _("Show the internal location field"), type: "check" },
                        { id: "aashowlocationunit", post_field: "AddAnimalsShowLocationUnit", label: _("Show the location unit field"), type: "check" },
                        { id: "aashowfosterer", post_field: "AddAnimalsShowFosterer", label: _("Allow a fosterer to be selected"), type: "check" },
                        { id: "aashowcoordinator", post_field: "AddAnimalsShowCoordinator", label: _("Allow an adoption coordinator to be selected"), type: "check" },
                        { id: "aashowacceptance", post_field: "AddAnimalsShowAcceptance", label: _("Show the litter ID field"), type: "check" },
                        { id: "aashowsize", post_field: "AddAnimalsShowSize", label: _("Show the size field"), type: "check" },
                        { id: "aashowweight", post_field: "AddAnimalsShowWeight", label: _("Show the weight field"), type: "check" },
                        { id: "aashowneutered", post_field: "AddAnimalsShowNeutered", label: _("Show the altered fields"), type: "check" },
                        { id: "aashowmicrochip", post_field: "AddAnimalsShowMicrochip", label: _("Show the microchip fields"), type: "check" },
                        { id: "aashowtattoo", post_field: "AddAnimalsShowTattoo", label: _("Show the tattoo fields"), type: "check" },
                        { id: "aashowentrycategory", post_field: "AddAnimalsShowEntryCategory", label: _("Show the entry category field"), type: "check" },
                        { id: "aashowentrytype", post_field: "AddAnimalsShowEntryType", label: _("Show the entry type field"), type: "check" },
                        { id: "aashowjurisdiction", post_field: "AddAnimalsShowJurisdiction", label: _("Show the jurisdiction field"), type: "check" },
                        { id: "aashowpickup", post_field: "AddAnimalsShowPickup", label: _("Show the pickup fields"), type: "check" },
                        { id: "aashowdatebroughtin", post_field: "AddAnimalsShowDateBroughtIn", label: _("Show the date brought in field"), type: "check" },
                        { id: "aashowtimebroughtin", post_field: "AddAnimalsShowTimeBroughtIn", label: _("Show the time brought in field"), type: "check" },
                        { id: "aashoworiginalowner", post_field: "AddAnimalsShowOriginalOwner", label: _("Show the original owner field"), type: "check" },
                        { id: "aashowbroughtinby", post_field: "AddAnimalsShowBroughtInBy", label: _("Show the brought in by field"), type: "check" },
                        { id: "aashowhold", post_field: "AddAnimalsShowHold", label: _("Show the hold fields"), type: "check" },
                        { id: "warnsimilaranimal", post_field: "WarnSimilarAnimalName", label: _("Warn if the name of the new animal is similar to one entered recently"), type: "check" }
                    ]},
                    { id: "tab-ageegroups", title: _("Age Groups"), info: _("Age groups are assigned based on the age of an animal. The figure in the left column is the upper limit in years for that group."), fields: [
                        { id: "agegroup1", post_field: "AgeGroup1", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup1Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup2", post_field: "AgeGroup2", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup2Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup3", post_field: "AgeGroup3", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup3Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup4", post_field: "AgeGroup4", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup4Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup5", post_field: "AgeGroup5", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup5Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup6", post_field: "AgeGroup6", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup6Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup7", post_field: "AgeGroup7", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup7Name"', justwidget: true, placeholder: _("Name") }) },
                        { id: "agegroup8", post_field: "AgeGroup8", label: "", type: "text", placeholder: _("Upper Age"), 
                            xmarkup: ' ' + tableform.render_text({xattr: 'data="AgeGroup8Name"', justwidget: true, placeholder: _("Name") })  }
                    ]},
                    { id: "tab-animalcodes", title: _("Animal Codes"), fields: [
                        { id: "codeformat", post_field: "CodingFormat", label: _("Animal code format"), type: "text",
                            callout: _("Code format tokens:") + '<br />' +
                            _("T = first letter of animal type") + '<br />' +
                            _("TT = first and second letter of animal type") + '<br />' + 
                            _("E = first letter of animal entry category") + '<br />' +
                            _("EE = first and second letter of animal entry category") + '<br />' + 
                            _("S = first letter of animal species") + '<br />' +
                            _("SS = first and second letter of animal species") + '<br />' + 
                            _("YY or YYYY = current year") + '<br />' +
                            _("MM = current month") + '<br />' +
                            _("DD = current day") + '<br />' + 
                            _("UUUUUUUUUU or UUUU = unique number") + '<br />' +
                            _("XXXX, XXX or XX = number unique for this year") + '<br />' +
                            _("OOO or OO = number unique for this month") + '<br />' +
                            _("NNNN, NNN or NN = number unique for this type of animal for this year") + '<br />' +
                            _("PPPP, PPP or PP = number unique for this species of animal for this year") + '<br />' +
                            _("Defaults formats for code and shortcode are TYYYYNNN and NNT")
                         },
                         { id: "shortformat", post_field: "ShortCodingFormat", label: _("Animal shortcode format"), type: "text",
                            callout: _("Code format tokens:") + '<br />' +
                            _("T = first letter of animal type") + '<br />' +
                            _("TT = first and second letter of animal type") + '<br />' + 
                            _("E = first letter of animal entry category") + '<br />' +
                            _("EE = first and second letter of animal entry category") + '<br />' + 
                            _("S = first letter of animal species") + '<br />' +
                            _("SS = first and second letter of animal species") + '<br />' + 
                            _("YY or YYYY = current year") + '<br />' +
                            _("MM = current month") + '<br />' +
                            _("DD = current day") + '<br />' + 
                            _("UUUUUUUUUU or UUUU = unique number") + '<br />' +
                            _("XXXX, XXX or XX = number unique for this year") + '<br />' +
                            _("OOO or OO = number unique for this month") + '<br />' +
                            _("NNNN, NNN or NN = number unique for this type of animal for this year") + '<br />' +
                            _("PPPP, PPP or PP = number unique for this species of animal for this year") + '<br />' +
                            _("Defaults formats for code and shortcode are TYYYYNNN and NNT")
                         },
                         { id: "incidentcodeformat", post_field: "IncidentCodingFormat", label: _("Incident code format"), type: "text",
                            callout: _("Code format tokens:") + '<br />' +
                            _("YY or YYYY = current year") + '<br />' +
                            _("MM = current month") + '<br />' +
                            _("DD = current day") + '<br />' + 
                            _("UUUUUUUUUU or UUUU = unique number") + '<br />' +
                            _("XXX or XX = number unique for this year") + '<br />' +
                            _("OOO or OO = number unique for this month") + '<br />' +
                            _("Defaults formats for incident codes are YYMM-XXX")
                         },
                         { id: "manualcodes", post_field: "ManualCodes", label: _("Manually enter codes (do not generate)"), type: "check", fullrow: true },
                         { id: "shortcodes", post_field: "UseShortShelterCodes", label: _("Show short shelter codes on screens"), type: "check", fullrow: true },
                         { id: "disableshortcodes", post_field: "DisableShortCodesControl", label: _("Remove short shelter code box from the animal details screen"), type: "check", fullrow: true },
                         { id: "shelterviewshowcodes", post_field: "ShelterViewShowCodes", label: _("Show codes on the shelter view screen"), type: "check", fullrow: true },
                         { id: "lockcodes", post_field: "LockCodes", label: _("Once assigned, codes cannot be changed"), type: "check", fullrow: true },
                         { id: "duplicatechip", post_field: "AllowDuplicateMicrochip", label: _("Allow duplicate microchip numbers"), type: "check", fullrow: true },
                         { id: "uniquelicence", post_field: "rc:UniqueLicenceNumbers", label: _("Allow duplicate license numbers"), type: "check", fullrow: true }
                    ]},
                    { id: "tab-animalemblems", title: _("Animal Emblems"), fields: [
                        { type: "raw", markup: html.textbar(_("Animal emblems are the little icons that appear next to animal names in shelter view, the home page and search results."), {maxwidth: "470px"}) },
                        { id: "alwaysshowlocation", post_field: "EmblemAlwaysLocation", type: "check", 
                            label: html.icon("location", "On Shelter") + html.icon("person", "Fostered") + html.icon("movement", "Adopted") + " " + _("Location") },
                        { id: "showadoptable", post_field: "EmblemAdoptable", label: html.icon("adoptable") + " " + _("Adoptable"), type: "check" },
                        { id: "showboarding", post_field: "EmblemBoarding", label: html.icon("boarding") + " " + _("Boarding"), type: "check" },
                        { id: "showbonded", post_field: "EmblemBonded", label: html.icon("bonded") + " " + _("Bonded"), type: "check" },
                        { id: "showcourtesy", post_field: "EmblemCourtesy", label: html.icon("share") + " " + _("Courtesy Listing"), type: "check" },
                        { id: "showcrueltycase", post_field: "EmblemCrueltyCase", label: html.icon("case") + " " + _("Cruelty Case"), type: "check" },
                        { id: "showdeceased", post_field: "EmblemDeceased", label: html.icon("death") + " " + _("Deceased"), type: "check" },
                        { id: "showfutureintake", post_field: "EmblemFutureIntake", label: html.icon("animal-add") + " " + _("Future Intake"), type: "check" },
                        { id: "showfutureadoption", post_field: "EmblemHold", label: html.icon("movement") + " " + _("Future Adoption"), type: "check" },
                        { id: "showhold", post_field: "EmblemFutureAdoption", label: html.icon("hold") + " " + _("Hold"), type: "check" },
                        { id: "longterm", post_field: "EmblemLongTerm", label: html.icon("calendar") + " " + _("Long Term"), type: "check" },
                        { id: "shownevervacc", post_field: "EmblemNeverVacc", label: html.icon("novaccination") + " " + _("Never Vaccinated"), type: "check" },
                        { id: "shownonshelter", post_field: "EmblemNonShelter", label: html.icon("nonshelter") + " " + _("Non-Shelter"), type: "check" },
                        { id: "shownotforadoption", post_field: "EmblemNotForAdoption", label: html.icon("notforadoption") + " " + _("Not For Adoption"), type: "check" },
                        { id: "showunmicrochipped", post_field: "EmblemNotMicrochipped", label: html.icon("microchip") + " " + _("Not Microchipped"), type: "check" },
                        { id: "showpositivetest", post_field: "EmblemPositiveTest", label: html.icon("positivetest") + " " + _("Positive for Heartworm, FIV or FLV"), type: "check" },
                        { id: "showquarantine", post_field: "EmblemQuarantine", label: html.icon("quarantine") + " " + _("Quarantine"), type: "check" },
                        { id: "showrabies", post_field: "EmblemRabies", label: html.icon("rabies") + " " + _("Rabies not given"), type: "check" },
                        { id: "showreserved", post_field: "EmblemReserved", label: html.icon("reservation") + " " + _("Reserved"), type: "check" },
                        { id: "showspecialneeds", post_field: "EmblemSpecialNeeds", label: html.icon("health") + " " + _("Special Needs"), type: "check" },
                        { id: "showtrialadoption", post_field: "EmblemTrialAdoption", label: html.icon("trial") + " " + _("Trial Adoption"), type: "check" },
                        { id: "showunneutered", post_field: "EmblemUnneutered", label: html.icon("unneutered") + " " + _("Unaltered"), type: "check" },
                        { type: "nextcol" },
                        { type: "raw", markup: html.info(_("You can assign a custom emblem to your additional animal flags")) },
                        { post_field: "EmblemsCustomValue1", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond1" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag1" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue2", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond2" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag2" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue3", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond3" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag3" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue4", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond4" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag4" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue5", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond5" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag5" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue6", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond6" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag6" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue7", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond7" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag7" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue8", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond8" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag8" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue9", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond9" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag9" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue10", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond10" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag10" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue11", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond11" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag11" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue12", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond12" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag12" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue13", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond13" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag13" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue14", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond14" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag14" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue15", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond15" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag15" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue16", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond16" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag16" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue17", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond17" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag17" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue18", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond18" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag18" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue19", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond19" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag19" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        },
                        { post_field: "EmblemsCustomValue20", type: "select", options: emblemoptions.join(""),
                            xmarkup: ' <select data="EmblemsCustomCond20" class="asm-selectbox">' + condoptions + '</select>' + ' <select data="EmblemsCustomFlag20" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>'
                        }

                    ]},
                    { id: "tab-boarding", title: _("Boarding"), fields: [
                        { id: "boardingpaytype", post_field: "BoardingPaymentType", label: _("Boarding payment type"), type: "select", options: html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"), callout: _("The payment type used when creating payments from boarding records")
                        }
                    ]},
                    { id: "tab-checkout", title: _("Checkout"), info: _("This feature allows you to email an adopter to have them sign their adoption paperwork, pay the adoption fee and make an optional donation."), fields: [
                        { id: "AdoptionCheckoutProcessor", post_field: "AdoptionCheckoutProcessor", label: _("Payment processor"), type: "select", 
                            options: html.list_to_options([
                                "paypal|" + _("PayPal"),
                                "square|" + _("Square"),
                                "stripe|" + _("Stripe")
                            ]) + "<option value='cardcom' class='israel'>" + _("Cardcom") + "</option>"
                        },
                        { id: "AdoptionCheckoutTemplateID", post_field: "AdoptionCheckoutTemplateID", label: _("Adoption paperwork template"), type: "select", 
                            options: edit_header.template_list_options(controller.templates)
                        }, 
                        { id: "AdoptionCheckoutFeeID", post_field: "AdoptionCheckoutFeeID", label: _("Adoption fee payment type"), type: "select", 
                            options: html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME")
                        }, 
                        { id: "LicenceCheckoutFeeID", post_field: "LicenceCheckoutFeeID", label: _("License fee payment type"), type: "select", 
                            options: html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME")
                        }, 
                        { id: "AdoptionCheckoutDonationID", post_field: "AdoptionCheckoutDonationID", label: _("Donation payment type"), type: "select", 
                            options: html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME")
                        }, 
                        { id: "AdoptionCheckoutPaymentMethod", post_field: "AdoptionCheckoutPaymentMethod", label: _("Payment method"), type: "select", 
                            options: html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME")
                        }, 
                        { id: "AdoptionCheckoutDonationMsg", post_field: "AdoptionCheckoutDonationMsg", label: _("Donation message"), type: "textarea", callout: _("The text to show adopters when requesting a donation. Simple HTML formatting is allowed.") }, 
                        { id: "AdoptionCheckoutDonationTiers", post_field: "AdoptionCheckoutDonationTiers", label: _("Donation tiers"), type: "textarea" }
                    ]},
                    { id: "tab-costs", title: _("Costs"), fields: [
                        { id: "dailyboardingcost", post_field: "DefaultDailyBoardingCost", label: _("Default daily boarding cost"), type: "currency", callout: _("The daily cost for every day a shelter animal is in care")
                        },
                        { id: "costtype", post_field: "BoardingCostType", label: _("Boarding cost type"), type: "select", 
                            options: html.list_to_options(controller.costtypes, "ID", "COSTTYPENAME"), 
                            callout: _("The cost type used when creating a cost record of the total daily boarding cost for adopted animals")
                        },
                        { id: "costonadoption", post_field: "CreateBoardingCostOnAdoption", label: _("Create boarding cost record when animal is adopted"), type: "check", fullrow: true },
                        { id: "showcostamount", post_field: "ShowCostAmount", label: _("Show a cost field on medical/test/vaccination screens"), type: "check", fullrow: true },
                        { id: "showcostpaid", post_field: "ShowCostPaid", label: _("Show a separate paid date field with costs"), type: "check", fullrow: true }
                    ]},
                    { id: "tab-daily-observations", title: _("Daily Observations"), info: _("These are the values that can be recorded for animals on the daily observations screen"), fields: [
                        { id: "behavelogtype", post_field: "BehaveLogType", label: _("Log Type"), type: "select", options: html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME")},
                        { id: "suppressblankobservations", post_field: "SuppressBlankObservations", label: _("Suppress blank observations"), type: "check" }, 
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave1Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave1Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave2Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave2Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave3Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave3Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave4Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave4Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave5Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave5Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave6Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave6Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave7Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave7Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave8Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave8Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave9Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave9Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) },
                        { type: "raw", fullrow: true, markup: tableform.render_text({xattr: 'data="Behave10Name"', justwidget: true, placeholder: _("Name")}) + ' ' + 
                            tableform.render_text({xattr: 'data="Behave10Values"', doublesize: true, justwidget: true, placeholder: _("Values")}) }
                    ]},
                    { id: "tab-data-protection", title: _("Data Protection"), fields: [
                        { id: "anonymisepersonaldata", post_field: "AnonymisePersonalData", label: _("Anonymize personal data after this many years"), type: "check", callout: _("This many years after creation of a person record, the name, address and telephone data will be anonymized."), xmarkup: '<input data="AnonymiseAfterYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />' }, 
                        { id: "anonymiseadopters", post_field: "rc:AnonymiseAdopters", label: _("Never anonymize people who adopted an animal"), type: "check" }, 
                        { id: "autoremovedocumentmedia", post_field: "AutoRemoveDocumentMedia", label: _("Remove HTML and PDF document media after this many years"), type: "check", xmarkup: '<input data="AutoRemoveDMYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />' }, 
                        { id: "autoremoveanimalmediaexit", post_field: "AutoRemoveAnimalMediaExit", label: _("Remove animal media this many years after the animal dies or leaves the shelter"), type: "check", xmarkup: '<input data="AutoRemoveAMExitYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />' }, 
                        { id: "autoremovepeoplecancresv", post_field: "AutoRemovePeopleCancResv", label: _("Remove people with a cancelled reservation who have not had any other contact after this many years"), type: "check", xmarkup: '<input data="AutoRemovePeopleCRYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />' }, 
                        { id: "showgdprcontact", post_field: "ShowGDPRContactOptIn", label: _("Show GDPR Contact Opt-In field on person screens"), type: "check" }, 
                        { id: "gdprcontactchangelog", post_field: "GDPRContactChangeLog", label: _("When I set a new GDPR Opt-In contact option, make a note of it in the log with this type"), type: "check", xmarkup: '<select data="GDPRContactChangeLogType" id="gdprcontactchangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }
                    ]}, 
                    { id: "tab-defaults", title: _("Defaults"), info:_("These are the default values for these fields when creating new records."), fields: [
                        { id: "DefaultAnimalAge", post_field: "DefaultAnimalAge", label: _("Age"), type: "number", min: 0, max: 10 }, 
                        { id: "defaultbreed", post_field: "AFDefaultBreed", label: _("Breed"), type: "select", options: html.list_to_options(controller.breeds, "ID", "BREEDNAME") }, 
                        { id: "defaultclinictype", post_field: "AFDefaultClinicType", label: _("Clinic Appointment"), type: "select", options: html.list_to_options(controller.clinictypes, "ID", "CLINICTYPENAME") }, 
                        { id: "defaultcoattype", post_field: "AFDefaultCoatType", label: _("Coat Type"), type: "select", options: html.list_to_options(controller.coattypes, "ID", "COATTYPE") }, 
                        { id: "defaultcolour", post_field: "AFDefaultColour", label: _("Color"), type: "select", options: html.list_to_options(controller.colours, "ID", "BASECOLOUR") }, 
                        { id: "defaultdeath", post_field: "AFDefaultDeathReason", label: _("Death Reason"), type: "select", options: html.list_to_options(controller.deathreasons, "ID", "REASONNAME") }, 
                        { id: "defaultdiary", post_field: "AFDefaultDiaryPerson", label: _("Diary Person"), type: "select", options: html.list_to_options(controller.usersandroles, "USERNAME", "USERNAME") }, 
                        { id: "defaultentryreason", post_field: "AFDefaultEntryReason", label: _("Entry Reason"), type: "select", options: html.list_to_options(controller.entryreasons, "ID", "REASONNAME") }, 
                        { id: "defaultentrytype", post_field: "AFDefaultEntryType", label: _("Entry Type"), type: "select", options: html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME") },
                        { id: "defaultincident", post_field: "DefaultIncidentType", label: _("Incident Type"), type: "select", options: html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME") }, 
                        { id: "defaultjurisdiction", post_field: "DefaultJurisdiction", label: _("Jurisdiction"), type: "select", options: html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME") }, 
                        { id: "defaultlocation", post_field: "AFDefaultLocation", label: _("Location"), type: "select", options: html.list_to_options(controller.locations, "ID", "LOCATIONNAME") }, 
                        { id: "defaultlog", post_field: "AFDefaultLogFilter", label: _("Log Filter"), type: "select", options: '<option value="-1">' + _("(all)") + '</option>' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") }, 
                        { type: "nextcol" }, 
                        { id: "defaultlogtype", post_field: "AFDefaultLogType", label: _("Log Type"), type: "select", options: html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") }, 
                        { id: "systemlogtype", post_field: "SystemLogType", label: _("System Log Type"), type: "select", options: html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") }, 
                        { id: "defaultpaymentmethod", post_field: "AFDefaultPaymentMethod", label: _("Payment Method"), type: "select", options: html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME") }, 
                        { id: "defaultdonation", post_field: "AFDefaultDonationType", label: _("Payment Type"), type: "select", options: html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME") }, 
                        { id: "defaultreservation", post_field: "AFDefaultReservationStatus", label: _("Reservation Status"), type: "select", options: html.list_to_options(controller.reservationstatuses, "ID", "STATUSNAME") }, 
                        { id: "defaultreturn", post_field: "AFDefaultReturnReason", label: _("Return Reason"), type: "select", options: html.list_to_options(controller.entryreasons, "ID", "REASONNAME") }, 
                        { id: "defaultsize", post_field: "AFDefaultSize", label: _("Size"), type: "select", options: html.list_to_options(controller.sizes, "ID", "SIZE") }, 
                        { id: "defaultspecies", post_field: "AFDefaultSpecies", label: _("Species"), type: "select", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") }, 
                        { id: "defaulttaxrate", post_field: "AFDefaultTaxRate", label: _("Tax Rate"), type: "select", options: html.list_to_options(controller.taxrates, "ID", "TAXRATENAME") }, 
                        { id: "defaulttest", post_field: "AFDefaultTestType", label: _("Test Type"), type: "select", options: html.list_to_options(controller.testtypes, "ID", "TESTNAME") }, 
                        { id: "defaulttransport", post_field: "AFDefaultTransportType", label: _("Transport Type"), type: "select", options: html.list_to_options(controller.transporttypes, "ID", "TRANSPORTTYPENAME") }, 
                        { id: "defaulttype", post_field: "AFDefaultType", label: _("Type"), type: "select", options: html.list_to_options(controller.types, "ID", "ANIMALTYPE") }, 
                        { id: "defaultvaccination", post_field: "AFDefaultVaccinationType", label: _("Vaccination Type"), type: "select", options: html.list_to_options(controller.vaccinationtypes, "ID", "VACCINATIONTYPE") }, 
                        
                        { type: "nextcol"}, 
                        { id: "DefaultBroughtInBy", post_field: "DefaultBroughtInBy", label: _("Default Brought In By"), type: "person" }, 
                        { id: "defaultshift", post_field: "DefaultShiftStart", label: _("Default Rota Shift"), type: "text", classes: "asm-textbox asm-halftextbox asm-timebox", xmarkup: '<input id="defaultshiftend" data="DefaultShiftEnd" type="text" class="asm-textbox asm-halftextbox asm-timebox" />' }, 

                        { id: "autonotadopt", post_field: "AutoNotForAdoption", label: _("Mark new animals as not for adoption"), type: "check", fullrow: true }, 
                        { id: "autoimagesnotforpublish", post_field: "AutoNewImagesNotForPublish", label: _("Exclude new animal photos from publishing"), type: "check", fullrow: true }, 
                        { id: "automedianotes", post_field: "AutoMediaNotes", label: _("Prefill new media notes for animal images with animal comments if left blank"), type: "check", fullrow: true },
                        { id: "medianotesfile", post_field: "DefaultMediaNotesFromFile", label: _("Prefill new media notes with the filename if left blank"), type: "check", fullrow: true }
                    ]}, 
                    { id: "tab-diaryandmessages", title: _("Diary and Messages"), fields: [
                        { id: "alldiaryhomepage", post_field: "AllDiaryHomePage", label: _("Show the full diary (instead of just my notes) on the home page"), type: "check" }, 
                        { id: "diarycompleteondeath", post_field: "DiaryCompleteOnDeath", label: _("Auto complete diary notes linked to animals when they are marked deceased"), type: "check" }, 
                        { id: "emaildiarynotes", post_field: "EmailDiaryNotes", label: _("Email users their outstanding diary notes once per day"), type: "check" }, 
                        { id: "emaildiaryonchange", post_field: "EmailDiaryOnChange", label: _("Email users immediately when a diary note assigned to them is created or updated"), type: "check" }, 
                        { id: "emaildiaryoncomplete", post_field: "EmailDiaryOnComplete", label: _("Email diary note creators when a diary note is marked complete"), type: "check" }, 
                        { id: "emailmessages", post_field: "EmailMessages", label: _("When a message is created, email it to each matching user"), type: "check" }, 
                    ]}, 
                    { id: "tab-display", title: _("Display"), fields: [
                        { id: "disableeffects", post_field: "rc:DisableEffects", label: _("Enable visual effects"), type: "check", fullrow: true }, 
                        { id: "disablehtml5scaling", post_field: "rc:DontUseHTML5Scaling", label: _("Use HTML5 client side image scaling where available to speed up image uploads"), type: "check", fullrow: true }, 
                        { id: "picsinbooksclinic", post_field: "PicturesInBooksClinic", label: _("Show animal thumbnails in clinic books"), type: "check", fullrow: true }, 
                        { id: "picsinbooks", post_field: "PicturesInBooks", label: _("Show animal thumbnails in movement and medical books"), type: "check", fullrow: true }, 
                        { id: "sexborder", post_field: "ShowSexBorder", label: _("Show pink and blue borders around animal thumbnails to indicate sex"), type: "check", fullrow: true }, 
                        { id: "minimap", post_field: "ShowPersonMiniMap", label: _("Show a minimap of the address on person screens"), type: "check", fullrow: true }, 
                        { id: "usstatecodes", post_field: "USStateCodes", label: _("When entering addresses, restrict states to valid US 2 letter state codes"), type: "check", fullrow: true, hideif: function() { return asm.locale != "en"; } },
                        { id: "latlong", post_field: "ShowLatLong", label: _("Allow editing of latitude/longitude with minimaps"), type: "check", fullrow: true }, 
                        { id: "mediatablemode", post_field: "MediaTableMode", label: _("Default to table mode when viewing media tabs"), type: "check", fullrow: true }, 
                        { id: "showlbs", post_field: "ShowWeightInLbs", label: _("Show weights as lb and oz"), type: "check", fullrow: true }, 
                        { id: "showlbsf", post_field: "ShowWeightInLbsFraction", label: _("Show weights as decimal lb"), type: "check", fullrow: true }, 
                        { id: "showfullcommentstables", post_field: "ShowFullCommentsInTables", label: _("Show complete comments in table views"), type: "check", fullrow: true }, 
                        { id: "showviewsaudittrail", post_field: "ShowViewsInAuditTrail", label: _("Show record views in the audit trail"), type: "check", fullrow: true }, 
                        { id: "showlookupdataid", post_field: "ShowLookupDataID", label: _("Show ID numbers when editing lookup data"), type: "check", fullrow: true }, 
                        { id: "floatingheaders", post_field: "StickyTableHeaders", label: _("Keep table headers visible when scrolling"), type: "check", fullrow: true }, 
                        { id: "tablesreflow", post_field: "TablesReflow", label: _("Tables stack vertically on portrait smartphones"), type: "check", fullrow: true }, 
                        { id: "recordnewbrowsertab", post_field: "RecordNewBrowserTab", label: _("Open records in a new browser tab"), type: "check", fullrow: true }, 
                        { id: "reportnewbrowsertab", post_field: "ReportNewBrowserTab", label: _("Open reports in a new browser tab"), type: "check", fullrow: true }, 
                        { id: "locationfilters", post_field: "LocationFiltersEnabled", label: _("Enable location filters"), type: "check", fullrow: true }, 
                        { id: "multisite", post_field: "MultiSiteEnabled", label: _("Enable multiple sites"), type: "check", fullrow: true }, 
                        { id: "formatphonenumbers", post_field: "FormatPhoneNumbers", label: _("Format telephone numbers according to my locale"), type: "check", fullrow: true }, 
                        { id: "inactivitytimer", post_field: "InactivityTimer", label: _("Auto log users out after this many minutes of inactivity"), type: "check", fullrow: true, xmarkup: '<input data="InactivityTimeout" id="inactivitytimeout" data-min="0" data-max="1440" class="asm-textbox asm-numberbox" />' }, 
                        { id: "ownernameformat", post_field: "OwnerNameFormat", label: _("When displaying person names, use the format"), type: "select", options:
                            '<option value="{ownertitle} {ownerforenames} {ownersurname}">' + _("Title First Last") + '</option>' + 
                            '<option value="{ownertitle} {ownerinitials} {ownersurname}">' + _("Title Initials Last") + '</option>' + 
                            '<option value="{ownerforenames} {ownersurname}">' + _("First Last") + '</option>' + 
                            '<option value="{ownersurname}, {ownerforenames}">' + _("Last, First") + '</option>' + 
                            '<option value="{ownersurname} {ownerforenames}">' + _("Last First") + '</option>', 
                            xmarkup: 
                            '<select data="OwnerNameMarriedFormat" id="ownernamemarriedformat" type="text" class="asm-selectbox">' + 
                            '<option value="{ownerforenames1} & {ownerforenames2} {ownersurname}">' + _("First & First Last") + '</option>' + 
                            '<option value="{ownersurname}, {ownerforenames1} & {ownerforenames2}">' + _("Last, First & First") + '</option>' + 
                            '</select> '
                        }, 
                        { id: "ownernameformat", post_field: "FirstDayOfWeek", label: _("When displaying calendars, the first day of the week is"), type: "select", options: html.list_to_options(['0|' + _("Sunday"), '1|' + _("Monday")]) }
                    ]}, 
                    { id: "tab-documents", title: _("Documents"), fields: [
                        { id: "allowodttemp", post_field: "AllowODTDocumentTemplates", label: _("Allow use of OpenOffice document templates"), type: "check" }, 
                        { id: "jswprint", post_field: "JSWindowPrint", label: _("Printing word processor documents uses hidden iframe and window.print"), type: "check" }, 
                        { id: "pdfinline", post_field: "PDFInline", label: _("Show PDF files inline instead of sending them as attachments"), type: "check" }, 
                        { id: "includeincompletemedical", post_field: "IncludeIncompleteMedicalDoc", label: _("Include incomplete medical records when generating document templates"), type: "check" }, 
                        { id: "notifycoordicatorondocsign", post_field: "DocumentSignedNotifyCoordinator", label: _("Notify adoption coordinator when documents are signed"), type: "check" }, 
                        { id: "generatedocumentlog", post_field: "GenerateDocumentLog", label: _("When I generate a document, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="GenerateDocumentLogType" id="generatedocumentlogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { type: "raw", markup: _("Default zoom level when converting documents to PDF") + ' <input type="text" class="asm-field asm-textbox asm-numberbox controlshadow controlborder" style="" id="pdfzoom" data-post="PDFZoom"">%' }
                    ]}, 
                    { id: "tab-email", title: _("Email"), fields: [
                        { id: "emailaddress", post_field: "EmailAddress", label: _("Email address"), type: "text", doublesize: true, 
                            callout: "This email address is the default From address when sending emails" }, 
                        { id: "emailbcc", post_field: "EmailBCC", label: _("BCC messages to"), type: "text", doublesize: true, 
                            callout: "BCC this address when sending email. This is useful if you want to archive your emails with another service." }, 
                        { id: "emailsig", post_field: "EmailSignature", label: _("Email signature"), type: "richtextarea", doublesize: true, height: "150px", 
                            callout: "This text will be added to the bottom of all send email dialogs" }, 
                        { type: "nextcol" },
                        { id: "emailfromadd", post_field: "EmailFromAddresses", label: _("From address book"), type: "textarea", doublesize: true, 
                            callout: "Comma separated list of extra addresses that the From email field of send email dialogs will prompt with" }, 
                        { id: "emailtoadd", post_field: "EmailToAddresses", label: _("To address book"), type: "textarea", doublesize: true, 
                            callout: "Comma separated list of extra addresses that the To and CC email fields of send email dialogs will prompt with" }, 
                        { type: "nextcol" },
                        { id: "smtpoverride", post_field: "SMTPOverride", label: _("Specify an SMTP server for sending emails"), type: "check", callout: _("Please do not enable this option if you do not understand what this means."), rowclasses: "smcom" }, 
                        { id: "smtpserver", post_field: "SMTPServer", label: _("SMTP Server"), type: "text", rowclasses: "smcom" }, 
                        { id: "smtpport", post_field: "SMTPPort", label: _("Port"), type: "select", options: "<option>25</option><option>587</option><option>2525</option>", rowclasses: "smcom" }, 
                        { id: "smtptls", post_field: "SMTPUseTLS", label: _("Use TLS"), type: "check", rowclasses: "smcom" }, 
                        { id: "smtpuser", post_field: "SMTPUsername", label: _("Username"), type: "text", rowclasses: "smcom" }, 
                        { id: "smtppass", post_field: "SMTPPassword", label: _("Password"), type: "text", rowclasses: "smcom" }, 
                        { id: "smtpreplyasfrom", post_field: "SMTPReplyAsFrom", label: _("Set the FROM header from the email dialog"), type: "check", callout: _("Allow the user to override the From header. Emails will fail if you try to send email from a domain you do not own."), rowclasses: "smcom" }
                    ]},
                    { id: "tab-findscreens", title: _("Find Screens"), fields: [
                        { id: "findanimalcols", post_field: "SearchColumns", label: _("Find animal columns"), type: "selectmulti", options: this.two_pair_options(controller.animalfindcolumns) }, 
                        { id: "findfoundanimalcols", post_field: "FoundAnimalSearchColumns", label: _("Find found animal columns"), type: "selectmulti", options: this.two_pair_options(controller.foundanimalfindcolumns) }, 
                        { id: "findlostanimalcols", post_field: "LostAnimalSearchColumns", label: _("Find lost animal columns"), type: "selectmulti", options: this.two_pair_options(controller.foundanimalfindcolumns) }, 
                        { id: "findincidentcols", post_field: "IncidentSearchColumns", label: _("Find incident columns"), type: "selectmulti", options: this.two_pair_options(controller.incidentfindcolumns) }, 
                        { id: "findpersoncols", post_field: "OwnerSearchColumns", label: _("Find person columns"), type: "selectmulti", options: this.two_pair_options(controller.personfindcolumns) }, 
                        { id: "findeventcols", post_field: "EventSearchColumns", label: _("Find event columns"), type: "selectmulti", options: this.two_pair_options(controller.eventfindcolumns) }, 
                        { id: "advancedfindanimal", post_field: "AdvancedFindAnimal", label: _("Default to advanced find animal screen"), type: "check", fullrow: true }, 
                        { id: "advancedfindanimalos", post_field: "AdvancedFindAnimalOnShelter", label: _("Advanced find animal screen defaults to on shelter"), type: "check", fullrow: true }, 
                        { id: "advancedfindperson", post_field: "AdvancedFindOwner", label: _("Default to advanced find person screen"), type: "check", fullrow: true }, 
                        { id: "aficomplete", post_field: "AdvancedFindIncidentIncomplete", label: _("Find an incident screen defaults to incomplete incidents"), type: "check", fullrow: true }, 
                        { id: "animalsearchnewtab", post_field: "AnimalSearchResultsNewTab", label: _("Open animal find screens in a new tab"), type: "check", fullrow: true }, 
                        { id: "personsearchnewtab", post_field: "PersonSearchResultsNewTab", label: _("Open person find screens in a new tab"), type: "check", fullrow: true }
                    ]}, 
                    { id: "tab-homepage", title: _("Home page"), fields: [
                        { id: "disabletips", post_field: "rc:DisableTips", label: _("Show tips on the home page"), type: "check", fullrow: true }, 
                        { id: "showalerts", post_field: "ShowAlertsHomePage", label: _("Show alerts on the home page"), type: "check", fullrow: true }, 
                        { id: "showoverview", post_field: "ShowOverviewHomePage", label: _("Show overview counts on the home page"), type: "check", fullrow: true }, 
                        { id: "showtimeline", post_field: "ShowTimelineHomePage", label: _("Show timeline on the home page"), type: "check", fullrow: true }, 
                        { id: "showhdeceased", post_field: "rc:ShowDeceasedHomePage", label: _("Hide deceased animals from the home page"), type: "check", fullrow: true }, 
                        { id: "showhfinancial", post_field: "rc:ShowFinancialHomePage", label: _("Hide financial stats from the home page"), type: "check", fullrow: true }, 
                        { type: "raw", fullrow: true, markup: '<p class="asm-header">' + _("Alerts") + '</p>' },
                        { id: "alertmicrochip", post_field: "AlertSpeciesMicrochip", label: _("Show an alert when these species of animals are not microchipped"), type: "selectmulti", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") }, 
                        { id: "alertentire", post_field: "AlertSpeciesNeuter", label: _("Show an alert when these species of animals are not altered"), type: "selectmulti", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") }, 
                        { id: "alertnevervacc", post_field: "AlertSpeciesNeverVacc", label: _("Show an alert when these species of animals do not have a vaccination of any type"), type: "selectmulti", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") }, 
                        { id: "alertrabies", post_field: "AlertSpeciesNeverVacc", label: _("Show an alert when these species of animals do not have a rabies vaccination"), type: "selectmulti", options: html.list_to_options(controller.species, "ID", "SPECIESNAME") }, 
                        { type: "raw", fullrow: true, markup: '<p class="asm-header">' + _("Stats") + '</p>' },
                        { type: "raw", fullrow: true, markup: html.info(_("Stats show running figures for the selected period of animals entering and leaving the shelter on the home page.")) },
                        { id: "statmode", post_field: "ShowStatsHomePage", label: _("Stats period"), type: "select", options: 
                            '<option value="none">' + _("Do not show") + '</option>' + 
                            '<option value="today">' + _("Today") + '</option>' + 
                            '<option value="thisweek">' + _("This week") + '</option>' + 
                            '<option value="thismonth">' + _("This month") + '</option>' + 
                            '<option value="thisyear">' + _("This year") + '</option>' + 
                            '<option value="alltime">' + _("All time") + '</option>'
                        }, 
                        { type: "raw", fullrow: true, markup: '<p class="asm-header">' + _("Animal Links") + '</p>' },
                        { id: "linkmode", post_field: "MainScreenAnimalLinkMode", label: _("Type of animal links to show"), type: "select", options: 
                            '<option value="none">' + _("Do not show") + '</option>' + 
                            '<option value="recentlychanged">' + _("Recently Changed") + '</option>' + 
                            '<option value="recentlyentered">' + _("Recently Entered Shelter") + '</option>' + 
                            '<option value="recentlyadopted">' + _("Recently Adopted") + '</option>' + 
                            '<option value="recentlyfostered">' + _("Recently Fostered") + '</option>' + 
                            '<option value="adoptable">' + _("Up for adoption") + '</option>' + 
                            '<option value="longestonshelter">' + _("Longest On Shelter") + '</option>'
                        }, 
                        { id: "linkmax", post_field: "MainScreenAnimalLinkMax", label: _("Number of animal links to show"), type: "number", min: 0, max: 200 }, 
                    ]}, 
                    { id: "tab-insurance", title: _("Insurance"), info: _("These numbers are for shelters who have agreements with insurance companies and are given blocks of policy numbers to allocate."), fields: [
                        { id: "autoinsurance", post_field: "UseAutoInsurance", label: _("Use Automatic Insurance Numbers"), type: "check" }, 
                        { id: "insurancestart", post_field: "UseAutoAutoInsuranceStartInsurance", label: _("Start at"), type: "number" }, 
                        { id: "insuranceend", post_field: "AutoInsuranceEnd", label: _("End at"), type: "number" }, 
                        { id: "insurancenext", post_field: "AutoInsuranceNext", label: _("Next"), type: "number" } 
                    ]}, 
                    { id: "tab-logs", title: _("Logs"), fields: [
                        { id: "flagchangelog", post_field: "FlagChangeLog", label: _("When I change the flags on an animal or person, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="FlagChangeLogType" id="flagchangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "holdchangelog", post_field: "HoldChangeLog", label: _("When I mark an animal held, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="HoldChangeLogType" id="holdchangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "locationchangelog", post_field: "LocationChangeLog", label: _("When I change the location of an animal, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="LocationChangeLogType" id="locationchangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "animalnamechangelog", post_field: "AnimalNameChangeLog", label: _("When I change the name of an animal, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="AnimalNameChangeLogType" id="animalnamechangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "weightchangelog", post_field: "WeightChangeLog", label: _("When I change the weight of an animal, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="WeightChangeLogType" id="weightchangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "addresschangelog", post_field: "AddressChangeLog", label: _("When I change the address of a person, make a note of it in the log with this type"), type: "check", xmarkup: ' <select data="AddressChangeLogType" id="addresschangelogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                        { id: "logemailbydefault", post_field: "LogEmailByDefault", label: _("When I send an email, record it in the log with this type"), type: "check", xmarkup: ' <select data="EmailLogType" id="emaillogtype" class="asm-selectbox">' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME") + '</select>' }, 
                    ]}, 
                    { id: "tab-lostandfound", title: _("Lost and Found"), fields: [
                        { id: "disablelostfound", post_field: "rc:DisableLostAndFound", label: _("Enable lost and found functionality"), type: "check", fullrow: true }, 
                        { id: "matchshelter", post_field: "MatchIncludeShelter", label: _("When matching lost animals, include shelter animals"), type: "check", fullrow: true }, 
                        { id: "matchpointfloor", post_field: "MatchPointFloor", label: _("Points required to appear on match report"), type: "number", colclasses: "bottomborder", classes: "strong" }, 
                        { id: "matchmicrochip", post_field: "MatchMicrochip", label: _("Points for matching microchip"), type: "number" }, 
                        { id: "matchspecies", post_field: "MatchSpecies", label: _("Points for matching species"), type: "number" }, 
                        { id: "matchbreed", post_field: "MatchBreed", label: _("Points for matching breed"), type: "number" }, 
                        { id: "matchcolour", post_field: "MatchColour", label: _("Points for matching color"), type: "number" }, 
                        { id: "matchagegroup", post_field: "MatchAge", label: _("Points for matching age group"), type: "number" }, 
                        { id: "matchsex", post_field: "MatchSex", label: _("Points for matching sex"), type: "number" }, 
                        { id: "matcharea", post_field: "MatchAreaLost", label: _("Points for matching lost/found area"), type: "number" }, 
                        { id: "matchfeatures", post_field: "MatchFeatures", label: _("Points for matching features"), type: "number" }, 
                        { id: "matchpostcode", post_field: "MatchPostcode", label: _("Points for matching zipcode"), type: "number" }, 
                        { id: "match2weeks", post_field: "MatchWithin2Weeks", label: _("Points for being found within 2 weeks of being lost"), type: "number" }, 
                    ]}, 
                    { id: "tab-medical", title: _("Medical"), fields: [
                        { id: "includeoffsheltermedical", post_field: "IncludeOffShelterMedical", label: _("Include off-shelter animals in medical calendar and books"), type: "check", fullrow: true }, 
                        { id: "precreatetreat", post_field: "MedicalPrecreateTreatments", label: _("Pre-create all treatments when creating fixed-length medical regimens"), type: "check", fullrow: true }, 
                        { id: "reloadmedical", post_field: "ReloadMedical", label: _("Reload the medical book/tab automatically after adding new medical items"), type: "check", fullrow: true }, 
                        { id: "autodefaultvaccbatch", post_field: "AutoDefaultVaccBatch", label: _("When entering vaccinations, default the last batch number and manufacturer for that type"), type: "check", fullrow: true }, 
                        { type: "raw", fullrow: true, markup: '<p class="asm-header">' + _("Weekly Fosterer Email") + '</p>' },
                        { id: "fostereremails", post_field: "FostererEmails", label: _("Send a weekly email to fosterers with medical information about their animals"), type: "check", fullrow: true }, 
                        { id: "fostereremailskipnomedical", post_field: "FostererEmailSkipNoMedical", label: _("Do not send an email if there are no medical items due for animals in the care of this fosterer"), type: "check", fullrow: true }, 
                        { id: "femailreplyto", post_field: "FostererEmailsReplyTo", label: _("Replies to the fosterer email should go to"), type: "text", callout: _("If blank, the address from the Email tab will be used") }, 
                        { id: "femailsendday", post_field: "FostererEmailSendDay", label: _("Send the email on"), type: "select", 
                            options: '<option value="0">' + _("Monday") + '</option>' + 
                            '<option value="1">' + _("Tuesday") + '</option>' + 
                            '<option value="2">' + _("Wednesday") + '</option>' + 
                            '<option value="3">' + _("Thursday") + '</option>' + 
                            '<option value="4">' + _("Friday") + '</option>' + 
                            '<option value="5">' + _("Saturday") + '</option>' + 
                            '<option value="6">' + _("Sunday") + '</option>' 
                        }, 
                        { id: "femailmsg", post_field: "FostererEmailsMsg", label: _("Add an extra message to the fosterer email"), type: "richtextarea" }
                    ]}, 
                    { id: "tab-movements", title: _("Movements"), fields: [
                        { id: "cancelunadopted", post_field: "AutoCancelReservesDays", label: _("Cancel unadopted reservations after"), type: "number", halfsize: true, callout: _("Cancel unadopted reservations after this many days, or 0 to never cancel"), xmarkup: _(" days.") }, 
                        { id: "reservesoverdue", post_field: "ReservesOverdueDays", label: _("Highlight unadopted reservations after"), type: "number", halfsize: true, xmarkup: _(" days.") }, 
                        { id: "autoremoveholddays", post_field: "AutoRemoveHoldDays", label: _("Remove holds after"), type: "number", halfsize: true, callout: _("Cancel holds on animals this many days after the brought in date, or 0 to never cancel"), xmarkup: _(" days.") }, 
                        { id: "defaulttriallength", post_field: "DefaultTrialLength", label: _("Trial adoptions last for"), type: "number", halfsize: true, callout: _("When creating trial adoptions, default the end date to this many days from the trial start"), xmarkup: _(" days.") }, 
                        { id: "longtermdays", post_field: "LongTermDays", label: _("Animals are long term after"), type: "number", halfsize: true, callout: _("Show an alert and emblem for animals who have been on shelter for this period"), xmarkup: _(" days.") }, 
                        { id: "futureonshelter", post_field: "FutureOnShelter", label: _("Treat animals with a future intake date as part of the shelter inventory"), type: "check", fullrow: true }, 
                        { id: "fosteronshelter", post_field: "FosterOnShelter", label: _("Treat foster animals as part of the shelter inventory"), type: "check", fullrow: true }, 
                        { id: "retaileronshelter", post_field: "RetailerOnShelter", label: _("Treat animals at retailers as part of the shelter inventory"), type: "check", fullrow: true }, 
                        { id: "trialadoptions", post_field: "TrialAdoptions", label: _("Our shelter does trial adoptions, allow us to mark these on movement screens"), type: "check", fullrow: true }, 
                        { id: "trialonshelter", post_field: "TrialOnShelter", label: _("Treat trial adoptions as part of the shelter inventory"), type: "check", fullrow: true }, 
                        { id: "softreleases", post_field: "SoftReleases", label: _("Our shelter does soft releases, allow us to mark these on movement screens"), type: "check", fullrow: true }, 
                        { id: "softreleaseonshelter", post_field: "SoftReleaseOnShelter", label: _("Treat soft releases as part of the shelter inventory"), type: "check", fullrow: true }, 
                        { id: "persononlyreserve", post_field: "MovementPersonOnlyReserves", label: _("Allow reservations to be created that are not linked to an animal"), type: "check", fullrow: true }, 
                        { id: "cancelresadopt", post_field: "CancelReservesOnAdoption", label: _("Automatically cancel any outstanding reservations on an animal when it is adopted"), type: "check", fullrow: true }, 
                        { id: "returnfosteradopt", post_field: "ReturnFostersOnAdoption", label: _("Automatically return any outstanding foster movements on an animal when it is adopted"), type: "check", fullrow: true }, 
                        { id: "returnfostertransfer", post_field: "ReturnFostersOnTransfer", label: _("Automatically return any outstanding foster movements on an animal when it is transferred"), type: "check", fullrow: true }, 
                        { id: "returnretaileradopt", post_field: "ReturnRetailerOnAdoption", label: _("Automatically return any outstanding retailer movements on an animal when it is adopted"), type: "check", fullrow: true }, 
                        { id: "donationsdue", post_field: "MovementDonationsDefaultDue", label: _("When creating payments from the Move menu screens, mark them due instead of received"), type: "check", fullrow: true }, 
                        { id: "donationmovereserve", post_field: "DonationOnMoveReserve", label: _("Allow creation of payments on the Move{0}Reserve screen").replace("{0}", html.icon("right")), type: "check", fullrow: true }, 
                        { id: "moveadoptdonationsenabled", post_field: "MoveAdoptDonationsEnabled", label: _("Allow editing of payments after creating an adoption on the Move{0}Adopt an animal screen").replace("{0}", html.icon("right")), type: "check", fullrow: true }, 
                        { id: "moveadoptgeneratepaperwork", post_field: "MoveAdoptGeneratePaperwork", label: _("Allow requesting signed paperwork when creating an adoption on the Move{0}Adopt an animal screen").replace("{0}", html.icon("right")), type: "check", fullrow: true }, 
                        { id: "movementoverride", post_field: "MovementNumberOverride", label: _("Allow overriding of the movement number on the Move menu screens"), type: "check", fullrow: true }, 
                        { type: "raw", markup: '<tr><td colspan="2"><p class="asm-header">' + _("Warnings") + "</p></td></tr>"}, 
                        { id: "warnunaltered", post_field: "WarnUnaltered", label: _("Warn when adopting an unaltered animal"), type: "check", fullrow: true }, 
                        { id: "warnnomicrochip", post_field: "WarnNoMicrochip", label: _("Warn when adopting an animal who has not been microchipped"), type: "check", fullrow: true }, 
                        { id: "warnosmedical", post_field: "WarnOSMedical", label: _("Warn when adopting an animal who has outstanding medical treatments"), type: "check", fullrow: true }, 
                        { id: "warnnohomecheck", post_field: "WarnNoHomeCheck", label: _("Warn when adopting to a person who has not been homechecked"), type: "check", fullrow: true }, 
                        { id: "warnbaddress", post_field: "WarnBannedAddress", label: _("Warn when adopting to a person who lives at the same address as a banned person"), type: "check", fullrow: true }, 
                        { id: "warnbanned", post_field: "WarnBannedOwner", label: _("Warn when adopting to a person who has been banned from adopting animals"), type: "check", fullrow: true }, 
                        { id: "warnoopostcode", post_field: "WarnOOPostcode", label: _("Warn when adopting to a person who lives in the same area as the original owner"), type: "check", fullrow: true }, 
                        { id: "warnbroughtin", post_field: "WarnBroughtIn", label: _("Warn when adopting to a person who has previously brought an animal to the shelter"), type: "check", fullrow: true }, 
                        { id: "warnnoreserve", post_field: "WarnNoReserve", label: _("Warn when adopting an animal with reservations and this person is not one of them"), type: "check", fullrow: true }, 
                        { id: "warnmultiplereseves", post_field: "WarnMultipleReserves", label: _("Warn when creating multiple reservations on the same animal"), type: "check", fullrow: true }
                    ]}, 
                    { id: "tab-onlineforms", title: _("Online Forms"), fields: [
                        { id: "autoremoveforms", post_field: "AutoRemoveIncomingFormsDays", label: _("Remove incoming forms after"), type: "number", halfsize: true, xmarkup: _(" days.") }, 
                        { id: "deleteonprocess", post_field: "OnlineFormDeleteOnProcess", label: _("Remove forms immediately when I process them"), type: "check", fullrow: true }, 
                        { id: "removeprocessedforms", post_field: "rc:DontRemoveProcessedForms", label: _("Remove processed forms when I leave the incoming forms screens"), type: "check", fullrow: true }, 
                        { id: "hashprocessedforms", post_field: "AutoHashProcessedForms", label: _("When storing processed forms as media, apply tamper proofing and make them read only"), type: "check", fullrow: true }, 
                        { id: "spamhoneytrap", post_field: "OnlineFormSpamHoneyTrap", label: _("Spambot protection: Invisible textbox"), type: "check", fullrow: true }, 
                        { id: "spamuacheck", post_field: "OnlineFormSpamUACheck", label: _("Spambot protection: UserAgent check"), type: "check", fullrow: true }, 
                        { id: "spamfirstname", post_field: "OnlineFormSpamFirstnameMixCase", label: _("Spambot protection: Person name mixed case"), type: "check", fullrow: true }, 
                        { id: "spampostcode", post_field: "OnlineFormSpamPostcode", label: _("Spambot protection: Zipcode contains numbers"), type: "check", fullrow: true }
                    ]}, 
                    { id: "tab-processors", title: _("Payment Processors"), info: _("ASM can talk to payment processors and request payment from your customers and donors."), fields: [
                        { id: "currencycode", post_field: "CurrencyCode", label: _("Request payments in"), doublesize: true, type: "select", options: html.list_to_options(controller.currencies, "CODE", "DISPLAY") }, 
                        { id: "paymentreturn", post_field: "PaymentReturnUrl", label: _("Redirect to this URL after successful payment"), doublesize: true, type: "text", colclasses: "bottomborder" }, 
                        { type: "raw", fullrow: true, rowclasses: "paypal-options", 
                            markup: '<p class="centered"><img height="25px" src="static/images/ui/logo_paypal_100.png" /></p>' }, 
                        { id: "paypalemail", post_field: "PayPalEmail", label: _("PayPal Business Email"), doublesize: true, type: "text", rowclasses: "paypal-options" }, 
                        { type: "raw", fullrow: true, rowclasses: "paypal-options", colclasses: "bottomborder",
                            markup: '<p class="centered">' + _("In your PayPal account, enable Instant Payment Notifications with a URL of {0}").replace("{0}", "<br/><b>" + controller.pp_paypal + "</b>") + '</p>' }, 
                        { type: "raw", fullrow: true, rowclasses: "stripe-options", 
                            markup: '<p class="centered"><img height="25px" src="static/images/ui/logo_stripe_103.png" /></p>' }, 
                        { id: "stripekey", post_field: "StripeKey", label: _("Stripe Key"), type: "text", doublesize: true, rowclasses: "stripe-options" }, 
                        { id: "stripesecretkey", post_field: "StripeSecretKey", label: _("Stripe Secret Key"), type: "text", doublesize: true, rowclasses: "stripe-options" }, 
                        { type: "raw", fullrow: true, rowclasses: "stripe-options", colclasses: "bottomborder",
                            markup: '<p class="centered">' + _("In the Stripe dashboard, create a webhook to send 'checkout.session.completed' events to {0}").replace("{0}", "<br/><b>" + controller.pp_stripe + "</b>") + '</p>' }, 
                        { type: "raw", fullrow: true, rowclasses: "square-options", 
                            markup: '<p class="centered"><img height="25px" src="static/images/ui/logo_square_100.png" /></p>' }, 
                        { id: "squareaccesstoken", post_field: "SquareAccessToken", label: _("Square Access Token"), type: "text", doublesize: true, rowclasses: "square-options" }, 
                        { id: "squarelocationid", post_field: "SquareLocationID", label: _("Square Location ID"), type: "text", doublesize: true, rowclasses: "square-options" }, 
                        { type: "raw", fullrow: true, rowclasses: "square-options", colclasses: "bottomborder", 
                            markup: '<p class="centered">' + _("In your Square account, enable a webhook to send 'payment.updated' events to {0}").replace("{0}", "<br/><b>" + controller.pp_square + "</b>") + '</p>' }, 
                        { type: "raw", fullrow: true, rowclasses: "cardcom-options israel", 
                            markup: '<p class="centered strong">' + _("Cardcom Payment Gateway") + '</p>' }, 
                        { id: "CardcomTerminalNumber", post_field: "CardcomTerminalNumber", label: _("Cardcom Terminal Number"), type: "text", rowclasses: "cardcom-options israel" }, 
                        { id: "CardcomUserName", post_field: "CardcomUserName", label: _("Cardcom User Name"), type: "text", rowclasses: "cardcom-options israel"}, 
                        { id: "CardcomDocumentType", post_field: "CardcomDocumentType", label: _("Cardcom User Type"), type: "text", rowclasses: "cardcom-options israel" }, 
                        { id: "CardcomSuccessURL", post_field: "CardcomSuccessURL", label: _("Cardcom Success URL"), type: "text", rowclasses: "cardcom-options israel" }, 
                        { id: "CardcomErrorURL", post_field: "CardcomErrorURL", label: _("Cardcom Error URL"), type: "text", rowclasses: "cardcom-options israel" }, 
                        { id: "cardcomusetoken", post_field: "CardcomUseToken", label: _("Allow use of tokens"), type: "check", rowclasses: "cardcom-options israel" }
                    ]}, 
                    { id: "tab-quicklinks", title: _("Quick Links"), info: _("Quicklinks are shown on the home page and allow quick access to areas of the system."), fields: [
                        { id: "disablequicklinkshome", post_field: "QuicklinksHomeScreen", label: _("Show quick links on the home page"), type: "check", fullrow: true }, 
                        { id: "disablequicklinksall", post_field: "QuicklinksAllScreens", label: _("Show quick links on all pages"), type: "check", fullrow: true }, 
                        { id: "quicklinksid", post_field: "QuicklinksID", label: _("Show quick links on all pages"), type: "selectmulti", options: this.quicklink_options() }, 

                    ]}, 
                    { id: "tab-reminders", title: _("Reminder Emails"), info: _("Reminder emails can be automatically sent to groups of people a number of days before or after a key event."), fields: [
                        { type: "raw", markup: '<tr><th colspan="2"></th><th>' + _("Days") + '</th><th>' + _("Template") + '</th></tr>' }, 
                        { id: "adopterfollowup", post_field: "EmailAdopterFollowup", label: _("Send a followup email to new adopters after X days"), type: "check", xmarkup: '</td><td><input data="EmailAdopterFollowupDays" id="adopterfollowupdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" /></td><td><select data="EmailAdopterFollowupTemplate" class="asm-selectbox">' + edit_header.template_list_options(controller.templates) + '</select>' }, 
                        { type: "raw", markup: '<tr><td colspan="2">' + _("Only for these species of adopted animal") + '</td><td><select id="adopterfollowupspecies" multiple="multiple" class="asm-bsmselect" data="EmailAdopterFollowupSpecies">' + html.list_to_options(controller.species, "ID", "SPECIESNAME") + '</select></td><td></td></tr>' }, 
                        { id: "vaccinationfollowup", post_field: "EmailVaccinationFollowup", label: _("Send a reminder email to owners X days before a vaccination is due"), type: "check", xmarkup: '</td><td><input data="EmailVaccinationFollowupDays" id="vaccinationfollowupdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" /></td><td><select data="EmailVaccinationFollowupTemplate" class="asm-selectbox">' + edit_header.template_list_options(controller.templates) + '</select>' }, 
                        { id: "clinicreminder", post_field: "EmailClinicReminder", label: _("Send a reminder email to people with clinic appointments in X days"), type: "check", xmarkup: '</td><td><input data="EmailClinicReminderDays" id="clinicreminderdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" /></td><td><select data="EmailClinicReminderTemplate" class="asm-selectbox">' + edit_header.template_list_options(controller.templatesclinic) + '</select>' }, 
                        { id: "duepayment", post_field: "EmailDuePayment", label: _("Send a reminder email to people with payments due in X days"), type: "check", xmarkup: '</td><td><input data="EmailDuePaymentDays" id="duepaymentdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" /></td><td><select data="EmailDuePaymentTemplate" class="asm-selectbox">' + edit_header.template_list_options(controller.templateslicence) + '</select>' }, 
                        { id: "licencereminder", post_field: "EmailLicenceReminder", label: _("Send a reminder email to people with licenses expiring in X days"), type: "check", xmarkup: '</td><td><input data="EmailLicenceReminderDays" id="licencereminderdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" /></td><td><select data="EmailLicenceReminderTemplate" class="asm-selectbox">' + edit_header.template_list_options(controller.templateslicence) + '</select>' }, 
                    ]}, 
                    { id: "tab-unwanted", title: _("Remove"), fields: [
                        { type: "raw", markup: '<p class="asm-header">' + _("System") + '</p>' }, 
                        { id: "disableboarding", post_field: "DisableBoarding", label: _("Remove boarding functionality from screens and menus"), type: "check" }, 
                        { id: "disableclinic", post_field: "DisableClinic", label: _("Remove clinic functionality from screens and menus"), type: "check" }, 
                        { id: "disablemovements", post_field: "DisableMovements", label: _("Remove move menu and the movements tab from animal and person screens"), type: "check" }, 
                        { id: "disableretailer", post_field: "DisableRetailer", label: _("Remove retailer functionality from the movement screens and menus"), type: "check" }, 
                        { id: "disabledocumentrepo", post_field: "DisableDocumentRepo", label: _("Remove the document repository functionality from menus"), type: "check" }, 
                        { id: "disableonlineforms", post_field: "DisableOnlineForms", label: _("Remove the online form functionality from menus"), type: "check" }, 
                        { id: "disableanimalcontrol", post_field: "DisableAnimalControl", label: _("Remove the animal control functionality from menus and screens"), type: "check" }, 
                        { id: "disableevents", post_field: "DisableEvents", label: _("Remove the event management functionality from menus and screens"), type: "check" }, 
                        { id: "disabletraploan", post_field: "DisableTrapLoan", label: _("Remove the equipment loan functionality from menus and screens"), type: "check" }, 
                        { id: "disablerota", post_field: "DisableRota", label: _("Remove the rota functionality from menus and screens"), type: "check" }, 
                        { id: "disablestockcontrol", post_field: "DisableStockControl", label: _("Remove the stock control functionality from menus and screens"), type: "check" }, 
                        { id: "disabletransport", post_field: "DisableTransport", label: _("Remove the transport functionality from menus and screens"), type: "check" }, 
                        { type: "raw", markup: '<p class="asm-header">' + _("People") + '</p>' }, 
                        { id: "towncounty", post_field: "HideTownCounty", label: _("Remove the city/state fields from person details"), type: "check" }, 
                        { id: "hcountry", post_field: "HideCountry", label: _("Remove the country field from person details"), type: "check" }, 
                        { id: "hcouhpdobntry", post_field: "HidePersonDateOfBirth", label: _("Remove the date of birth field from person details"), type: "check" }, 
                        { id: "hidehwphone", post_field: "HideHomeWorkPhone", label: _("Remove the home and work telephone number fields from person details"), type: "check" }, 
                        { id: "hhomechecked", post_field: "HideHomeCheckedNoFlag", label: _("Remove the homechecked/by fields from person type according to the homechecked flag"), type: "check" }, 
                        { id: "hidnumber", post_field: "HideIDNumber", label: _("Remove the identification number field from person details"), type: "check" }, 
                        { id: "insuranceno", post_field: "DontShowInsurance", label: _("Remove the insurance number field from the movement screens"), type: "check" }, 
                        { id: "lookingforno", post_field: "HideLookingFor", label: _("Remove the looking for functionality from the person menus and screens"), type: "check" }, 
                        { type: "nextcol" }, 
                        { type: "raw", markup: '<p class="asm-header">' + _("Animals") + '</p>' }, 
                        { id: "disableasilomar", post_field: "DisableAsilomar", label: _("Remove the asilomar fields from the entry/deceased sections"), type: "check", classes: "us" }, 
                        { id: "disableentryhistory", post_field: "DisableEntryHistory", label: _("Remove the entry history section from animal records"), type: "check" }, 
                        { id: "entrytype", post_field: "DontShowEntryType", label: _("Remove the entry type field from animal entry details"), type: "check" }, 
                        { id: "coattype", post_field: "DontShowCoatType", label: _("Remove the coat type field from animal details"), type: "check" }, 
                        { id: "size", post_field: "DontShowSize", label: _("Remove the size field from animal details"), type: "check" }, 
                        { id: "weight", post_field: "DontShowWeight", label: _("Remove the weight field from animal details"), type: "check" }, 
                        { id: "microchip", post_field: "DontShowMicrochip", label: _("Remove the microchip fields from animal identification details"), type: "check" }, 
                        { id: "microchipstatus", post_field: "DontShowMicrochipStatus", label: _("Remove the microchip status from animal identification details"), type: "check" }, 
                        { id: "microchipmf", post_field: "DontShowMicrochipSupplier", label: _("Remove the microchip supplier info from animal identification details"), type: "check" }, 
                        { id: "tattoo", post_field: "DontShowTattoo", label: _("Remove the tattoo fields from animal identification details"), type: "check" }, 
                        { id: "neutered", post_field: "DontShowNeutered", label: _("Remove the neutered fields from animal health details"), type: "check" }, 
                        { id: "declawed", post_field: "DontShowDeclawed", label: _("Remove the declawed box from animal health details"), type: "check" }, 
                        { id: "rabiestag", post_field: "DontShowRabies", label: _("Remove the Rabies Tag field from animal health details"), type: "check" }, 
                        { id: "goodwith", post_field: "DontShowGoodWith", label: _("Remove the good with fields from animal notes"), type: "check" }, 
                        { id: "heartworm", post_field: "DontShowHeartworm", label: _("Remove the heartworm test fields from animal health details"), type: "check" }, 
                        { id: "combitest", post_field: "DontShowCombi", label: _("Remove the FIV/L test fields from animal health details"), type: "check" }, 
                        { id: "fee", post_field: "DontShowAdoptionFee", label: _("Remove the adoption fee field from animal details"), type: "check" }, 
                        { id: "coordinator", post_field: "DontShowAdoptionCoordinator", label: _("Remove the adoption coordinator field from animal entry details"), type: "check" }, 
                        { id: "litterid", post_field: "DontShowLitterID", label: _("Remove the Litter ID field from animal details"), type: "check" }, 
                        { id: "subunit", post_field: "DontShowLocationUnit", label: _("Remove the location unit field from animal details"), type: "check" }, 
                        { id: "bonded", post_field: "DontShowBonded", label: _("Remove the bonded with fields from animal entry details"), type: "check" }, 
                        { id: "jurisdiction", post_field: "DontShowJurisdiction", label: _("Remove the jurisdiction field from animal entry details"), type: "check" }, 
                        { id: "pickup", post_field: "DontShowPickup", label: _("Remove the picked up fields from animal entry details"), type: "check" }
                    ]}, 
                    { id: "tab-reports", title: _("Reports"), fields: [
                        { id: "emptyreports", post_field: "EmailEmptyReports", label: _("Email scheduled reports with no data"), type: "check" }, 
                        { id: "reportmenuaccordion", post_field: "ReportMenuAccordion", label: _("Show report menu items in collapsed categories"), type: "check" }
                    ]}, 
                    { id: "tab-search", title: _("Search"), info: _("These options change the behaviour of the search box at the top of the page."), fields: [
                        { id: "showsearchgo", post_field: "ShowSearchGo", label: _("Display a search button at the right side of the search box"), type: "check" }, 
                        { id: "searchsort", post_field: "SearchSort", label: _("Search sort order"), type: "select", 
                            options:  '<option value="0">' + _("Alphabetically A-Z") + '</option>' + 
                                '<option value="1">' + _("Alphabetically Z-A") + '</option>' + 
                                '<option value="2">' + _("Least recently changed") + '</option>' + 
                                '<option value="3">' + _("Most recently changed") + '</option>' + 
                                '<option value="6">' + _("Most relevant") + '</option>'
                        }
                    ]}, 
                    { id: "tab-security", title: _("Security"), fields: [
                        { id: "force2fa", post_field: "Force2FA", label: _("Force users to enable 2 factor authentication"), type: "check" }, 
                        { id: "forcestrongpasswords", post_field: "ForceStrongPasswords", label: _("Force users to set strong passwords (8+ characters of mixed case and numbers)"), type: "check" }, 
                        { id: "incidentpermissions", post_field: "IncidentPermissions", label: _("Enable access permissions for incident records"), type: "check" }, 
                        { id: "personpermissions", post_field: "PersonPermissions", label: _("Enable access permissions for person records"), type: "check" }
                    ]}, 
                    { id: "tab-shelterview", title: _("Shelter view"), fields: [
                        { id: "shelterviewdefault", post_field: "ShelterViewDefault", label: _("Default view"), type: "select", options: html.shelter_view_options() }, 
                        { id: "shelterviewdragdrop", post_field: "ShelterViewDragDrop", label: _("Allow drag and drop to move animals between locations"), type: "check", fullrow: true }, 
                        { id: "shelterviewreserves", post_field: "ShelterViewReserves", label: _("Allow units to be reserved and sponsored"), type: "check", fullrow: true }, 
                        { id: "shelterviewempty", post_field: "ShelterViewShowEmpty", label: _("Show empty locations"), type: "check", fullrow: true }
                    ]}, 
                    { id: "tab-stock", title: _("Stock"), fields: [
                        { id: "stockmovementusagetypeid", post_field: "StockMovementUsageTypeID", label: _("Stock movement usage type"), type: "select", options: html.list_to_options(controller.stockusagetypes, "ID", "USAGETYPENAME"), callout: _("The pseudo usagetype used to represent internal movements") }, 
                        { id: "defaultproducttypeid", post_field: "StockDefaultProductTypeID", label: _("Default product type"), type: "select", options: html.list_to_options(controller.producttypes, "ID", "PRODUCTTYPENAME") }
                    ]}, 
                    { id: "tab-waitinglist", title: _("Waiting List"), fields: [
                        { id: "disablewl", post_field: "rc:DisableWaitingList", label: _("Enable the waiting list functionality"), type: "check", fullrow: true }, 
                        { id: "wlrank", post_field: "WaitingListRankBySpecies", label: _("Separate waiting list rank by species"), type: "check", fullrow: true }, 
                        { id: "wlupdate", post_field: "WaitingListUrgencyUpdatePeriod", label: _("Waiting list urgency update period in days"), type: "number", min: 0, max: 365, callout: _("Set to 0 to never update urgencies.") }, 
                        { id: "wldu", post_field: "WaitingListDefaultUrgency", label: _("Default urgency"), type: "select", options: html.list_to_options(controller.urgencies, "ID", "URGENCY") }, 
                        { id: "wlremoval", post_field: "WaitingListDefaultRemovalWeeks", label: _("Default removal after weeks without contact"), type: "number", min: 0, max: 52, callout: _("Set to 0 to never auto remove.") }, 
                        { id: "wlcolumns", post_field: "WaitingListViewColumns", label: _("Columns displayed"), type: "selectmulti", options: this.two_pair_options(controller.waitinglistcolumns) }
                    ]}, 
                    { id: "tab-watermark", title: _("Watermark"), fields: [
                        { id: "watermarkxoffset", post_field: "WatermarkXOffset", label: _("Watermark logo X offset"), type: "number", min: 0, max: 9999, callout: _("Relative to bottom right corner of the image") }, 
                        { id: "watermarkyoffset", post_field: "WatermarkYOffset", label: _("Watermark logo Y offset"), type: "number", min: 0, max: 9999, callout: _("Relative to bottom right corner of the image") }, 
                        { id: "watermarkfontfillcolor", post_field: "WatermarkFontFillColor", label: _("Watermark font fill color"), type: "select", options: html.list_to_options_array(this.watermark_colors), xmarkup: '<span id="fontfillcolorsample" style="border: 1px solid black; margin-left: 25px; padding: 0 20px; background: ' + html.decode(config.str('WatermarkFontFillColor')) + '" />' }, 
                        { id: "watermarkfontshadowcolor", post_field: "WatermarkFontShadowColor", label: _("Watermark font outline color"), type: "select", options: html.list_to_options_array(this.watermark_colors), xmarkup: '<span id="fontshadowcolorsample" style="border: 1px solid black; margin-left: 25px; padding: 0 20px; background: ' + html.decode(config.str('WatermarkFontShadowColor')) + '" />' }, 
                        { id: "watermarkfontstroke", post_field: "WatermarkFontStroke", label: _("Watermark font outline width"), type: "number", min: 0, max: 20 }, 
                        { id: "watermarkfontfile", post_field: "WatermarkFontFile", label: _("Watermark font"), type: "select", doublesize: true, options: html.list_to_options_array(asm.fontfiles), xmarkup: '<img id="watermarkfontpreview" src="" style="height: 40px; width: 200px; border: 1px solid #000; vertical-align: middle" />' }, 
                        { id: "watermarkfontoffset", post_field: "WatermarkFontOffset", label: _("Watermark name offset"), type: "number", min: 0, max: 100, callout: _("Offset from left edge of the image") }, 
                        { id: "watermarkfontmaxsize", post_field: "WatermarkFontMaxSize", label: _("Watermark name max font size"), type: "number", min: 0, max: 999 }
                    ]}
                ], {full_width: false}),
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const get_donation_mappings = function() {
                let mappings = "";
                $(".donmap").each(function() {
                    let mapname = $(this).val();
                    let idx = $(this).attr("data-idx");
                    let mapvalue = $("#mapac" + idx).val();
                    if (mapname && mapname != "-1" && mapvalue && mapvalue != "-1") {
                        if (mappings != "") { mappings += ","; }
                        mappings += mapname + "=" + mapvalue;
                    }
                });
                return encodeURIComponent(mappings);
            };

            validate.save = async function(callback) {
                validate.dirty(false);
                let formdata = "mode=save&" + $("input, select, textarea, .asm-richtextarea").not(".chooser").toPOST(true);
                formdata += "&DonationAccountMappings=" + get_donation_mappings();
                try {
                    let response = await common.ajax_post("options", formdata);
                    callback(response);
                }
                catch(err) {
                    console.log(err);
                    log.error(err, err);
                    validate.dirty(true);
                }
            };

            // Toolbar buttons
            $("#button-save").button().click(async function() {
                header.show_loading(_("Saving..."));
                validate.save(function() {
                    common.route_reload(true); // Needs full reload to get config.js to update
                }); 
            });

            // Load default values from the config settings
            $("input, select, textarea, .asm-richtextarea").each(function() {
                if ($(this).attr("data") || $(this).attr("data-post")) {
                    let d = $(this).attr("data");
                    if (!d) { d = $(this).attr("data-post");}
                    if ($(this).is(".asm-currencybox")) {
                        $(this).val( html.decode(config.currency(d)));
                    }
                    else if ($(this).is(".asm-richtextarea")) {
                        $(this).richtextarea("value", config.str(d));
                    }
                    else if ($(this).is("input:text")) {
                        if ($(this).is(".asm-mask") && config.str(d)) { $(this).val(MASK_VALUE); }
                        else { $(this).val( html.decode(config.str(d))); }
                    }
                    else if ($(this).is("input:checkbox")) {
                        if (d.indexOf("rc:") != -1) {
                            // it's a reverse checkbox, not it before setting
                            if (!config.bool(d.substring(3))) {
                                $(this).attr("checked", "checked");
                            }
                        }
                        else if (config.bool(d)) {
                            $(this).attr("checked", "checked");
                        }
                    }
                    else if ($(this).is("input:hidden")) {
                        $(this).val( config.str(d));
                    }
                    else if ($(this).is(".asm-selectbox") && $(this).is(".decode")) {
                        $(this).select("value", html.decode(config.str(d)));
                    }
                    else if ($(this).is(".asm-selectbox") || $(this).is(".asm-doubleselectbox")) {
                        $(this).select("value", config.str(d));
                    }
                    else if ($(this).is(".asm-bsmselect")) {
                        let ms = config.str(d).split(",");
                        let bsm = $(this);
                        $.each(ms, function(i, v) {
                            bsm.find("option[value='" + common.trim(v + "']")).attr("selected", "selected");
                        });
                        $(this).change();
                    }
                    else if ($(this).is("textarea")) {
                        $(this).val( html.decode(config.str(d)));
                    }
                    else if ($(this).is(".asm-richtextarea")) {
                        $(this).richtextarea("value", config.str(d));
                    }
                }
            });

            // Set donation type maps from DonationAccountMappings field
            let donmaps = config.str("DonationAccountMappings");
            if (donmaps != "") {
                let maps = donmaps.split(",");
                $.each(maps, function(i, v) {
                    let dt = v.split("=")[0];
                    let ac = v.split("=")[1];
                    let idx = i + 1;
                    $("#mapdt" + idx).select("value", dt);
                    $("#mapac" + idx).select("value", ac);
                });
            }

            // Hide options not applicable for some locales
            if (asm.locale != "en") {
                $(".us").hide();
            }
            if (asm.locale != "he" && asm.locale != "en_IL") {
                $(".israel").hide();
            }

            // Hide other non-relevant options
            if (!controller.haspaypal) {
                $(".paypal-options").hide();
            }
            if (!controller.hassquare) {
                $(".square-options").hide();
            }
            if (!asm.smcom) {
                $(".smcom").hide();
            }

            // Show sample colours and fonts when selected
            $("#watermarkfontfillcolor").change(function() {
                $("#fontfillcolorsample").css("background-color", $("#watermarkfontfillcolor").select("value"));
            });
            $("#watermarkfontshadowcolor").change(function() {
                $("#fontshadowcolorsample").css("background-color", $("#watermarkfontshadowcolor").select("value"));
            });
            $("#watermarkfontfile").change(function() {
                $("#watermarkfontpreview").prop("src", "options_font_preview?fontfile=" + $("#watermarkfontfile").val());
            });
            $("#watermarkfontfile").change();

            // By default, we have a style that constrains the width of 
            // multi-select widgets to 300px - remove it for this screen so that
            // the find screens and quick links can take up more room.
            $(".asmContainer").css("max-width", "800px");

            validate.bind_dirty();

        },

        sync: function() {

        },

        delay: function() {
            // Show the mini map
            let latlong = config.str("OrganisationLatLong"), 
                popuptext = "<b>" + config.str("Organisation") + "</b><br>" + config.str("OrganisationAddress");
            mapping.draw_map("embeddedmap", 15, latlong, [{ 
                latlong: latlong, popuptext: popuptext, popupactive: true }]);
        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#DefaultBroughtInBy", "personchooser");
        },

        name: "options",
        animation: "options",
        autofocus: "#organisation",
        title: function() { return _("Options"); },
        routes: {
            "options": function() { common.module_loadandstart("options", "options"); }
        }

    };

    common.module_register(options);

});
