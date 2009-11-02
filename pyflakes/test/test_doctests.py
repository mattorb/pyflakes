import textwrap

from pyflakes.test.test_other import Test as TestOther
from pyflakes.test.test_imports import Test as TestImports
from pyflakes.test.test_undefined_names import Test as TestUndefinedNames

import pyflakes.messages as m

class Test(TestOther, TestImports, TestUndefinedNames):

    def doctestify(self, input):
        lines = []
        for line in textwrap.dedent(input).splitlines():
            if line.strip() == '':
                pass
            elif (line.startswith(' ') or
                  line.startswith('except:') or
                  line.startswith('except ') or
                  line.startswith('finally:') or
                  line.startswith('else:') or
                  line.startswith('elif ')):
                line = "... %s" % line
            else:
                line = ">>> %s" % line
            lines.append(line)
        doctestificator = '''
def doctest_something():
    """
       %s
    """
'''
        return doctestificator % "\n       ".join(lines)

    def flakes(self, input, *expectedOutputs):
        return super(Test, self).flakes(self.doctestify(input),
                                        *expectedOutputs)

    def test_doubleNestingReportsClosestName(self):
        """
        Lines in doctest are a bit different so we can't use the test
        from TestUndefinedNames
        """
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> def a():
                ...     x = 1
                ...     def b():
                ...         x = 2 # line 4 in a doctest
                ...         def c():
                ...             x
                ...             x = 3

            """
        ''', m.UndefinedLocal).messages[0]
        self.assertEqual(exc.message_args, ('x', 4))

    def test_futureImport(self):
        """XXX This test can't work in a doctest"""

    def test_importBeforeDoctest(self):
        super(Test, self).flakes("""
        import foo

        def doctest_stuff():
            '''
                >>> foo
            '''
        """)

    def test_importBeforeAndInDoctest(self):
        super(Test, self).flakes('''
        import foo

        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        foo
        ''', m.RedefinedWhileUnused)

    def test_importInDoctestAndAfter(self):
        super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> import foo
                >>> foo
            """

        import foo
        foo()
        ''')

    def test_lineNumbersInDoctests(self):
        exc = super(Test, self).flakes('''

        def doctest_stuff():
            """
                >>> x # line 5
            """

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 5)

    def test_lineNumbersAfterDoctests(self):
        exc = super(Test, self).flakes('''

        def doctest_stuff():
            """
                >>> x = 5
            """

        x

        ''', m.UndefinedName).messages[0]
        self.assertEqual(exc.lineno, 8)

    def test_syntaxErrorInDoctest(self):
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> from # line 4
            """
        ''', m.DoctestSyntaxError).messages[0]
        self.assertEqual(exc.lineno, 4)

    def test_indentationErrorInDoctest(self):
        exc = super(Test, self).flakes('''
        def doctest_stuff():
            """
                >>> if True:
                ... pass
            """
        ''', m.DoctestSyntaxError).messages[0]
        self.assertEqual(exc.lineno, 5)
