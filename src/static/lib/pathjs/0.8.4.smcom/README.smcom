This is path.js 0.8.4 from https://github.com/mtrpcic/pathjs

For ASM, we've made some modifications:

1. Querystrings are extracted from paths and turned into an object, 
   accessible in your route callbacks as this.qs.[param] or in their
   raw form as this.rawqs

2. Path.rescue() receives the unmatched path as the first argument.

3. Path.change(function(path) {}) allows you to listen for any changes
   to the current route and take action.

4. Path.reload() - reloads the current route as if it was navigated to
   again, but without a new history state.

5. Path.popState() - includes the querystring when returning to the
   previous state.

6. Both Path.reload() and Path.popState() use a new function Path.path_to_route
   to turn document.location.pathname into a matching route. If your
   routes all being with / and start at the bottom of the path you may
   want to alter this routine to just return 
   document.location.pathname + document.location.search

