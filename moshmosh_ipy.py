"""
Move this script to the directory
    $USER/.ipython/profile_default/startup/ ,
and you can use moshmosh syntax in IPython
"""

import sys
import os
import ast
from IPython import get_ipython
from IPython.core.interactiveshell import InputRejected

_moshmosh_ipy = None
def moshmosh_input_transf(lines):
    global _moshmosh_ipy
    if _moshmosh_ipy is None:
        from moshmosh.repl_apis import IPythonSupport
        _moshmosh_ipy = IPythonSupport({})
    return _moshmosh_ipy.input_transform(lines)

class MoshmoshASTTransf(ast.NodeTransformer):
    @staticmethod
    def visit(node):
        try:
            node = _moshmosh_ipy.ast_transform(node)
            return node
        except Exception as e:
            raise InputRejected

ip = get_ipython()
ip.input_transformers_post.append(moshmosh_input_transf)
ip.ast_transformers.append(MoshmoshASTTransf)
