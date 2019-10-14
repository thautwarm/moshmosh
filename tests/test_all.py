import moshmosh.extension_register
import unittest
import sys

class Test(unittest.TestCase):
    def test_extensions(self):
        import tests.lazy_import
        import tests.match
        import tests.template_python
        import tests.pipelines
        import tests.quick_lambdas
        import tests.scoped_operators
        if sys.version_info < (3, 5):
            import tests.complex_match_py34
        else:
            import tests.complex_match
        import tests.list_view
        import tests.incremental