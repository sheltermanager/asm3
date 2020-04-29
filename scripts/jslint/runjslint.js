/*jslint laxbreak: true */

var fs, vm, sandbox, filedata, jslintCore = 'jslint-core.js';

fs = require('fs');
vm = require('vm');
sandbox = {};
res = vm.runInNewContext(fs.readFileSync(jslintCore), sandbox, jslintCore);
JSLINT = sandbox.JSLINT;

fs.readFile(process.argv[2], "utf8", function(err, data) {
    var ok = JSLINT(data)
      , i
      , error
      , errorType
      , nextError
      , errorCount
      , WARN = 'WARNING'
      , ERROR = 'ERROR';

    if (!ok) {
        errorCount = JSLINT.errors.length;
        for (i = 0; i < errorCount; i += 1) {
            error = JSLINT.errors[i];
            errorType = WARN;
            nextError = i < errorCount ? JSLINT.errors[i+1] : null;
            if (error && error.reason && error.reason.match(/^Stopping/) === null) {
                // If jslint stops next, this was an actual error
                if (nextError && nextError.reason && nextError.reason.match(/^Stopping/) !== null) {
                    errorType = ERROR;
                }
                console.log([error.line, error.character, errorType, error.reason].join(":"));
            }
        }
    }
});


