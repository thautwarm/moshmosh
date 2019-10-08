
from ast import *
a = Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=4, col_offset=0, id='PM140085921707568.0', ctx=Store())],
            value=Tuple(
                lineno=1,
                col_offset=0,
                elts=[
                    Num(lineno=4, col_offset=11, n=1),
                    Num(lineno=4, col_offset=14, n=2),
                ],
                ctx=Load(),
            ),
        ),
        Expr(
            lineno=314,
            col_offset=12,
            value=[
                If(
                    lineno=242,
                    col_offset=16,
                    test=Call(
                        lineno=242,
                        col_offset=19,
                        func=Name(lineno=242, col_offset=19, id='isinstance', ctx=Load()),
                        args=[
                            Name(lineno=4, col_offset=0, id='PM140085921707568.0', ctx=Load()),
                            Name(lineno=242, col_offset=19, id='tuple', ctx=Load()),
                        ],
                        keywords=[],
                    ),
                    body=[
                        Expr(
                            lineno=243,
                            col_offset=20,
                            value=[

                            ],
                        ),
                    ],

                ),
            ],
        ),

    ],
)

compile(a, "x", "exec")