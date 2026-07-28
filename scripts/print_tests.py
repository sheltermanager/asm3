#!/usr/bin/env python3
"""
script to get all the tests from the test suite
and print them to the console in a format that can be supplied to `python -m unittest`
to be run in parallel with `xargs` or GNU `parallel`

https://github.com/python/cpython/tree/main/Lib/unittest
https://docs.python.org/3/library/unittest.html#classes-and-functions

USAGE:

./print_tests.py tests/ | xargs -n 1 -P 4 python3 -m unittest

./print_tests.py tests/test_foo.py | xargs -n 1 -P 4 python3 -m unittest

"""
import sys
from unittest import TestLoader
from unittest.main import _convert_name
from unittest.util import strclass
from unittest.suite import TestSuite
args = sys.argv[1:]
testSource = args[0] # "tests/" or "tests/test_foo.py"

loader = TestLoader()

# load all the test suites from the provided input
needsPrefix = False # if we need to prepend the source name to the final label ; this is needed for dir path inputs
if testSource.endswith(".py"):
    testSuite = loader.loadTestsFromName(_convert_name(testSource))
else:
    needsPrefix = True
    testSuite = loader.discover(testSource)

# recursive generator to get all the TestCase entries from all the TestSuites; TestSuites can contain arbitrary levels of nested TestSuites's that contain TestCases
def get_all_tests(testSuite):
    for item in testSuite:
        if not isinstance(item, TestSuite):
            yield item
        else:
            yield from get_all_tests(item)

testsList = [ i for i in get_all_tests(testSuite)]

# make text labels for each test case that we can use to run the test case from the CLI
testLabels = []
for t in testsList:
    label = strclass(t.__class__) + '.' + t._testMethodName
    if needsPrefix:
        label = _convert_name(testSource).rstrip("/") + '.' + label
    testLabels.append(label)

for label in testLabels:
    print(label)
