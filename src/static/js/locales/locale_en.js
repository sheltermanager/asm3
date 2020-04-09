// en - no po needed

i18n_lang = {};

        _ = function(key) {
            try {
                var v = key;
                if (i18n_lang.hasOwnProperty(key)) {
                    if ($.trim(i18n_lang[key]) != "" && i18n_lang[key].indexOf("??") != 0 && i18n_lang[key].indexOf("(??") != 0) {
                        v = i18n_lang[key];
                    }
                    else {
                        v = key;
                    }
                }
                else {
                    v = key;
                }
                return $("<div></div>").html(v).text();
            }
            catch (err) {
                return "[error]";
            }
        };
        
