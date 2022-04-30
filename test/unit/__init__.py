import os
import pkgutil
import inspect
import unittest

# Add *all* subdirectories to this module's path
__path__ = [x[0] for x in os.walk(os.path.dirname(__file__))]

def load_tests(loader, suite, pattern):
    for imp, modname, _ in pkgutil.walk_packages(__path__):
        mod = imp.find_module(modname).load_module(modname)
        for memname, memobj in inspect.getmembers(mod):
            if inspect.isclass(memobj):
                if issubclass(memobj, unittest.TestCase):
                    print("Found TestCase: {}".format(memobj))
                    for test in loader.loadTestsFromTestCase(memobj):
                        print("  Found Test: {}".format(test))
                        suite.addTest(test)

    print("=" * 70)
    return suite