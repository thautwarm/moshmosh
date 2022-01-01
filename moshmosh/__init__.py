from .ast_compat import ast
from .extension_register import *
from .extensions import template_python
from .extensions import lazy_import
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=SyntaxWarning)
    from .extensions import pattern_matching
from .extensions import scoped_operators
from .extensions import pipelines
from .extensions import only_block
from .extensions import quick_lambdas
