import moshmosh
import sys

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
