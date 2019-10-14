"""
Move this script to the directory
    $USER/.ipython/profile_default/startup/ ,
and you can use moshmosh syntax in IPython
"""

import sys
from IPython import get_ipython
_moshmosh_exts = {}
def incr_moshmosh(lines):
    from moshmosh.extension_incremental import perform_extension_incr
    src = perform_extension_incr(
        _moshmosh_exts,
        '\n'.join(lines),
        incr_moshmosh.__code__.co_filename
    )
    return [line+'\n' for line in src.splitlines()]

ip = get_ipython()
ip.input_transformers_post.append(incr_moshmosh)