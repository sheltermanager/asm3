var Path = {
    'version': "0.8.4.smcom",
    'map': function (path) {
        if (Path.routes.defined.hasOwnProperty(path)) {
            return Path.routes.defined[path];
        } else {
            return new Path.core.route(path);
        }
    },
    'root': function (path) {
        Path.routes.root = path;
    },
    'rescue': function (fn) {
        Path.routes.rescue = fn;
    },
     /** RRT 2015-05-09: change route is called every time the route changes */
    'change': function(fn) {
        Path.routes.change = fn;
    },
    'history': {
        // RRT 2015-05-23: No longer needed
        //'initial':{}, // Empty container for "Initial Popstate" checking variables.
        'pushState': function(state, title, path){
            if(Path.history.supported){
                if(Path.dispatch(path)){
                    history.pushState(state, title, path);
                }
            } else {
                if(Path.history.fallback){
                    window.location.hash = "#" + path;
                }
            }
        },
        'popState': function(event){
            // RRT: 2015-05-23 if no state is passed, this is Safari and 
            // popState has been fired during page load - ignore it
            if (!event.state) { return; }
            //var initialPop = !Path.history.initial.popped && location.href == Path.history.initial.URL;
            //Path.history.initial.popped = true;
            //if(initialPop) return;
            // RRT: 2015-05-10 Use a new function to transform current location to a route
            Path.dispatch(Path.path_to_route());
        },
        'listen': function(fallback){
            Path.history.supported = !!(window.history && window.history.pushState);
            Path.history.fallback  = fallback;

            if(Path.history.supported){
                // RRT: 2015-05-23 not needed - check event.state
                // Path.history.initial.popped = ('state' in window.history), Path.history.initial.URL = location.href;
                window.onpopstate = Path.history.popState;
            } else {
                if(Path.history.fallback){
                    for(route in Path.routes.defined){
                        if(route.charAt(0) != "#"){
                          Path.routes.defined["#"+route] = Path.routes.defined[route];
                          Path.routes.defined["#"+route].path = "#"+route;
                        }
                    }
                    Path.listen();
                }
            }
        }
    },
    'match': function (path, parameterize) {
        var params = {}, route = null, possible_routes, slice, i, j, compare, q = "", qs = {};
        // RRT: 2015-05-08 If the path has a query string in it:
        //      1. Remove it from the path for route matching purposes
        //      2. Call splitqs() on it to turn it into an object
        //      3. Assign it to this.qs similar to this.params
        //      4. Assign the raw querystring as this.rawqs
        var splitqs = function(a) {
            var i = 0, b = {};
            if (!a) { return {}; }
            $.each(a.split("&"), function(i, v) {
                var x = v.split("=");
                b[x[0]] = decodeURIComponent(x[1].replace(/\+/g, " "));
            });
            return b;
        };
        if (path.indexOf("?") != -1) {
            q = path.substring(path.indexOf("?")+1);
            path = path.substring(0, path.indexOf("?"));
            qs = splitqs(q);
        }
        // RRT: End changes
        for (route in Path.routes.defined) {
            if (route !== null && route !== undefined) {
                route = Path.routes.defined[route];
                possible_routes = route.partition();
                for (j = 0; j < possible_routes.length; j++) {
                    slice = possible_routes[j];
                    compare = path;
                    if (slice.search(/:/) > 0) {
                        for (i = 0; i < slice.split("/").length; i++) {
                            if ((i < compare.split("/").length) && (slice.split("/")[i].charAt(0) === ":")) {
                                params[slice.split('/')[i].replace(/:/, '')] = compare.split("/")[i];
                                compare = compare.replace(compare.split("/")[i], slice.split("/")[i]);
                            }
                        }
                    }
                    if (slice === compare) {
                        if (parameterize) {
                            route.params = params;
                            route.qs = qs;
                            route.rawqs = q;
                        }
                        return route;
                    }
                }
            }
        }
        return null;
    },
    'dispatch': function (passed_route) {
        var previous_route, matched_route;
        if (Path.routes.current !== passed_route) {
            Path.routes.previous = Path.routes.current;
            Path.routes.current = passed_route;
            matched_route = Path.match(passed_route, true);

            if (Path.routes.previous) {
                previous_route = Path.match(Path.routes.previous);
                if (previous_route !== null && previous_route.do_exit !== null) {
                    previous_route.do_exit();
                }
            }

            if (matched_route !== null) {
                /** RRT 2015-05-09: Fire the "change" route every time we go somewhere */
		        if (Path.routes.change) { 
                    Path.routes.change(passed_route);
                }
                matched_route.run();
                return true;
            } else {
                if (Path.routes.rescue !== null) {
                    // RRT: 2015-05-09 - pass the non-matching path to the rescue route
                    Path.routes.rescue(passed_route);
                }
            }
        }
    },
    /** RRT 2015-05-10: Reruns the current route, if path is set uses that instead */
    'reload': function() {
        var path = Path.path_to_route();
        var matched_route = Path.match(path, true);
        if (matched_route) {
            matched_route.run();
        }
    },
    /** RRT 2015-05-11: Transforms the current path to one of our routes. path.js
     *  normally assumes that pathname matches routes and you're doing /route from
     *  the host. We don't do that, but never leave the first path element.*/
    'path_to_route': function() {
        var path = document.location.pathname;
        if (path.lastIndexOf("/") != -1) { path = path.substring(path.lastIndexOf("/")+1); }
        if (document.location.search) { path += document.location.search; }
        return path;
    },
    'listen': function () {
        var fn = function(){ Path.dispatch(location.hash); }

        if (location.hash === "") {
            if (Path.routes.root !== null) {
                location.hash = Path.routes.root;
            }
        }

        // The 'document.documentMode' checks below ensure that PathJS fires the right events
        // even in IE "Quirks Mode".
        if ("onhashchange" in window && (!document.documentMode || document.documentMode >= 8)) {
            window.onhashchange = fn;
        } else {
            setInterval(fn, 50);
        }

        if(location.hash !== "") {
            Path.dispatch(location.hash);
        }
    },
    'core': {
        'route': function (path) {
            this.path = path;
            this.action = null;
            this.do_enter = [];
            this.do_exit = null;
            this.params = {};
            Path.routes.defined[path] = this;
        }
    },
    'routes': {
        'current': null,
        'root': null,
        'rescue': null,
        'previous': null,
        'change': null, // RRT: 2015-05-09
        'defined': {}
    }
};
Path.core.route.prototype = {
    'to': function (fn) {
        this.action = fn;
        return this;
    },
    'enter': function (fns) {
        if (fns instanceof Array) {
            this.do_enter = this.do_enter.concat(fns);
        } else {
            this.do_enter.push(fns);
        }
        return this;
    },
    'exit': function (fn) {
        this.do_exit = fn;
        return this;
    },
    'partition': function () {
        var parts = [], options = [], re = /\(([^}]+?)\)/g, text, i;
        while (text = re.exec(this.path)) {
            parts.push(text[1]);
        }
        options.push(this.path.split("(")[0]);
        for (i = 0; i < parts.length; i++) {
            options.push(options[options.length - 1] + parts[i]);
        }
        return options;
    },
    'run': function () {
        var halt_execution = false, i, result, previous;

        if (Path.routes.defined[this.path].hasOwnProperty("do_enter")) {
            if (Path.routes.defined[this.path].do_enter.length > 0) {
                for (i = 0; i < Path.routes.defined[this.path].do_enter.length; i++) {
                    result = Path.routes.defined[this.path].do_enter[i].apply(this, null);
                    if (result === false) {
                        halt_execution = true;
                        break;
                    }
                }
            }
        }
        if (!halt_execution) {
            Path.routes.defined[this.path].action();
        }
    }
};
