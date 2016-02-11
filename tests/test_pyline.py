#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
test_pyline
----------------------------------

Tests for `pyline` module.
"""
import collections
import difflib
# import json
import logging
import os
import pprint
import sys
import tempfile
import unittest

from itertools import izip_longest

try:
    import StringIO as io   # Python 2
except ImportError:
    import io               # Python 3

from pyline import pyline

TEST_INPUT = """
Lines
=======
Of a file
---------
With Text

And Without

http://localhost/path/to/file?query#fragment

"""


TEST_INPUT_A0 = """a 5 320
b 4 310
c 3 200
d 2 100
e 1 500
f 0 300
"""

TEST_OUTPUT_A0_SORT_ASC_0 = TEST_INPUT_A0
TEST_OUTPUT_A0_SORT_DESC_0 = """f 0 300
e 1 500
d 2 100
c 3 200
b 4 310
a 5 320
"""
TEST_OUTPUT_A0_SORT_ASC_1 = TEST_OUTPUT_A0_SORT_DESC_0

TEST_OUTPUT_A0_SORT_ASC_2 = """d 2 100
c 3 200
f 0 300
b 4 310
a 5 320
e 1 500
"""

TEST_OUTPUT_A0_SORT_DESC_2 = '\n'.join(
    l for l in TEST_OUTPUT_A0_SORT_ASC_2.splitlines()[::-1]
)

_IO = collections.namedtuple('IO', ['args', 'kwargs', 'expectedoutput'])


def splitwords(s):
    return [x.split() for x in s.splitlines()]

class IO(_IO):

    def __repr__(self):
        # return json.dumps(self._asdict(), indent=2)
        return unicode(
            "IO(\n"
            "  args={}\n"
            "  kwargs={}\n"
            "  expected=\n"
            "{}\n"
            ")").format(
                repr(self.args),
                repr(self.kwargs),
                pprint.pformat(self.expectedoutput))


class TestPyline(unittest.TestCase):

    def setUp(self, *args):
        self.setup_logging()
        (self._test_file_fd, self.TEST_FILE) = tempfile.mkstemp(text=True)
        fd = self._test_file_fd
        os.write(fd, TEST_INPUT)
        os.write(fd, self.TEST_FILE)
        self.log.info("setup: %r", repr(self.TEST_FILE))

    def setup_logging(self):
        self.log = logging.getLogger() # self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)

    def tearDown(self):
        os.close(self._test_file_fd)
        os.remove(self.TEST_FILE)

    def test_10_pyline_pyline(self):
        PYLINE_TESTS = (
            {"cmd": "line"},
            {"cmd": "words"},
            {"cmd": "sorted(words)"},
            {"cmd": "w[:3]"},
            {"regex": r"(.*)"},
            {"regex": r"(.*)", "cmd": "rgx and rgx.groups()"},
            {"regex": r"(.*)", "cmd": "rgx and rgx.groups() or '#'"},
        )
        _test_output = sys.stdout
        _test_input = io.StringIO(TEST_INPUT)
        for test in PYLINE_TESTS:
            for line in pyline.pyline(_test_input, **test):
                print(line, file=_test_output)

    def test_15_pyline_sort__0__line_asc0(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "line", "sort_asc": "0"},
                TEST_OUTPUT_A0_SORT_ASC_0.splitlines(True))
        self.assertTestIO(io)

    def test_15_pyline_sort__1__words_asc0(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "words", "sort_asc": "0"},
                splitwords(TEST_OUTPUT_A0_SORT_ASC_0))
        self.assertTestIO(io)

    def test_15_pyline_sort__2__words_asc1(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "words", "sort_asc": "1"},
                splitwords(TEST_OUTPUT_A0_SORT_ASC_1))
        self.assertTestIO(io)

    def test_15_pyline_sort__3__words_asc2(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "words", "sort_asc": "2"},   # words[2]
                splitwords(TEST_OUTPUT_A0_SORT_ASC_2))
        self.assertTestIO(io)

    def test_15_pyline_sort__4__line_asc1(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "line", "sort_asc": "1"},    # line[2] == ' ' # XXX
                TEST_INPUT_A0.splitlines(True))
        self.assertTestIO(io)

    def test_15_pyline_sort__5__words_desc2(self):
        io = IO(TEST_INPUT_A0,
                {"cmd": "words", "sort_desc": "2"},  # words[2]
                splitwords(TEST_OUTPUT_A0_SORT_DESC_2))
        self.assertTestIO(io)

    # def test_15_pyline_sort__6(self):
    #     # TODO: AssertRaises ? output w/ cmd "line" undef.
    #     pass

    # def test_15_pyline_sort__7(self):
    #     io = ({"cmd": "line", "sort_desc": "0"},
    #           TEST_OUTPUT_A0_SORT_DESC_0)
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__8(self):
    #     io = ({"cmd": "words", "sort_desc": "0"},
    #           splitwords(TEST_OUTPUT_A0_SORT_DESC_0))
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__9(self):
    #     io = ({"cmd": "words"},
    #           TODO)
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__10(self):
    #     io = ({"cmd": "w[:3]"},
    #           TODO)
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__11(self):
    #     io = ({"regex": r"(.*)"},
    #           TODO)
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__12(self):
    #     io = ({"regex": r"(.*)", "cmd": "rgx and rgx.groups()"},
    #           TODO)
    #     self.assertTestIO(io)

    # def test_15_pyline_sort__13(self):
    #     io = ({"regex": r"(.*)", "cmd": "rgx and rgx.groups() or '#'"},
    #           TODO)
    #     self.assertTestIO(io)

    @staticmethod
    def sequence_sidebyside(
            seq1,
            seq2,
            header1=None,
            header2=None,
            colwidth=None,
            colsplitstr=' | ',
            DEFAULT_COLWIDTH=36):
        """print seq1 and seq2  adjacently

        Args:
            seq1 (list[object.__repr__)): list of objects
            seq2 (list[object.__repr__]): list of objects
        Kwargs:
            header1 (None, str): header for col1
            header2 (None, str): header for col2
            colwidth (None):
        Returns:
            list: list of strings without newlines
                (of length ((2 * colwidth) + len(colsplitstr)))
        """
        header1 = header1 if header1 is not None else 'thing1'
        header2 = header2 if header2 is not None else 'thing2'
        obj1_repr_maxwidth = None
        # obj2_repr_maxwidth = None
        seq1_and_seq2 = []
        for obj1, obj2 in izip_longest(seq1, seq2):
            obj1_repr, obj2_repr = repr(obj1), repr(obj2)
            seq1_and_seq2.append((obj1_repr, obj2_repr,))
            obj1_repr_len = len(obj1_repr)
            if obj1_repr_len > obj1_repr_maxwidth:
                obj1_repr_maxwidth = obj1_repr_len
        if colwidth is None:
            if obj1_repr_maxwidth:
                colwidth = obj1_repr_maxwidth
            else:
                colwidth = DEFAULT_COLWIDTH

        def strfunc(str1, str2, colwidth=colwidth, colsplitstr=colsplitstr):
            return colsplitstr.join((
                str1.ljust(colwidth, ' '),
                str2.ljust(colwidth, ' ')))

        def draw_table():
            yield strfunc(header1, header2)
            yield strfunc('='*colwidth, '='*colwidth)
            for seqs in seq1_and_seq2:
                yield strfunc(*seqs)
            yield strfunc('_' * colwidth, '_' * colwidth)
        tblstr = list(draw_table())
        # for line in tblstr:
        #     print(line)
        return tblstr, colwidth

    @staticmethod
    def sequence_updown(seq1, seq2, maxwidth=None):
        yield str(seq1)[:maxwidth]
        yield str(seq2)[:maxwidth]

    def assertSequenceEqualSidebyside(self,
            seq1, seq2, seq_type=None, msg=None,
            header1=None, header2=None, colwidth=None):
        """print seq1 and seq2  adjacently

        Args:
            seq1 (list[object)): list of objects with ``__repr__`` methods
            seq2 (list[object]): list of objects with ``__repr__`` methods
        Kwargs:
            header1 (None, str): header for col1
            header2 (None, str): header for col2
            colwidth (None):
        Raises:
            list: list of strings without newlines
                (of length ((2 * colwidth) + len(colsplitstr)))
        """
        seq1_str = pprint.pformat(seq1) #.splitlines() # [repr(x) for x in seq1])
        seq2_str = pprint.pformat(seq2) #.splitlines() # [repr(x) for x in seq2))
        #import pdb; pdb.set_trace()  # XXX BREAKPOINT

        header1 = 'expected'
        header2 = 'output'
        try:
            self.assertSequenceEqual(
                seq1, seq2,
                seq_type=seq_type,
                msg=msg)
            self.assertMultiLineEqual(
                seq1_str,
                seq2_str,
                msg=msg)
        except AssertionError as e:
            sidebysidestr, colwidth = self.sequence_sidebyside(
                seq1, seq2,
                header1=header1,
                header2=header2)
            updownstr = self.sequence_updown(seq1, seq2, maxwidth=79)
            diffstr_unified = difflib.unified_diff(
                seq1_str.splitlines(),
                seq2_str.splitlines(),
                fromfile=header1,
                tofile=header2,
            )
            # diffstr_ndiff = list(difflib.ndiff(seq1_str, seq2_str))
            errmsg = unicode('\n').join((
                e.message,
                '\n',
                unicode('\n').join(sidebysidestr),
                '\n',
                unicode('\n').join(diffstr_unified),
                '\n',
                # unicode('\n').join(diffstr_ndiff),
                unicode('\n').join(updownstr),
            ))
            e.message = errmsg
            print(errmsg)
            raise

    def assertTestIO(self, testio, msg=None):
        """
        Args:
            testio (test_pyline.IO):
        Kwargs:
            msg (None, str): Assertion kwargs
        """
        # print(testio)
        args, kwargs, expectedoutput = testio

        if isinstance(args, basestring):
            args = args.splitlines(True)
        iterable = args

        if hasattr(expectedoutput, 'readlines'):
            expectedoutputlist = expectedoutput.readlines()
        elif hasattr(expectedoutput, 'splitlines'): # isinstance(basestring)
            expectedoutputlist = expectedoutput.splitlines(True)
        else:
            expectedoutputlist = expectedoutput

        # output = list(pyline.pyline(args, **kwargs)) # TODO: port sort?

        output = []
        pyline.main(iterable=iterable, results=output, opts=kwargs)

        outputresults = [x.result for x in output]
        self.assertSequenceEqualSidebyside(
                expectedoutputlist,
                outputresults,
                seq_type=list, # (list, io.StringIO),
                header1='seq1',
                header2='seq2',
                msg=msg)

    def test_20_pyline_main(self):
        CMDLINE_TESTS = (
            tuple(),
            ("line",),
            ("l",),
            ("l", "-n"),
            ("l and l[:5]",),
            ("words",),
            ("w",),
            ("w", "-n"),
            ("w", "--shlex"),
            ("w", '-O', 'csv'),
            ("w", '-O', 'csv', '-n'),

            ("w", '-O', 'csv', '-s', '0'),
            ("w", '-O', 'csv', '-s', '1'),
            ("w", '-O', 'csv', '-s', '1,2'),
            ("w", '-O', 'csv', '-S', '1'),
            ("w", '-O', 'csv', '-S', '1', '-n'),

            ("w", '-O', 'json'),
            ("w", '-O', 'json', '-n'),

            ("w", '-O', 'tsv'),

            ("w", '-O', 'html'),

            ("w", '-O', 'checkbox'),
            ("w", '-O', 'chk'),

            ("len(words) > 2 and words",),

            ('-r', '(.*with.*)'),
            ('-r', '(.*with.*)',            '-R', 'i'),
            ('-r', '(?P<line>.*with.*)'),
            ('-r', '(?P<line>.*with.*)',    '-O', 'json'),
            ('-r', '(?P<line>.*with.*)',    '-O', 'checkbox'),
            ('-r', '(.*with.*)', 'rgx and {"n":i, "match": rgx.groups()[0]}',
             '-O', 'json'),
            ("-r", '(.*with.*)', '_rgx.findall(line)',
             '-O', 'json'),

            ('-m',
             'os',
             'os.path.isfile(line) and (os.stat(line).st_size, line)'),
            #
            ("-p", "p and p.isfile() and (p.size, p, p.stat())")
        )

        TEST_ARGS = ('-f', self.TEST_FILE)

        for argset in CMDLINE_TESTS:
            _args = TEST_ARGS + argset
            self.log.debug("main%s" % str(_args))
            try:
                output = pyline.main(_args)
                for n in output and output or []:
                    self.log.debug(n)
            except Exception as e:
                self.log.error("cmd: %s" % repr(_args))
                self.log.exception(e)
                raise

    def test_30_pyline_codefunc(self):
        codefunc = lambda x: x['line'][::-1]
        iterable = ["one", "two"]
        outrable = ["eno", "owt"]
        output = pyline.pyline(iterable, codefunc=codefunc)
        self.assertTrue(hasattr(output, 'next'))
        output_list = [result.result for result in output]
        self.assertEqual(output_list, outrable)  # ...


import types

class TestCaseColspec(unittest.TestCase):

    colspecstr_inputs = """
    0
    0,1,2'
    2, 1, 0
    2:int
    0:str, 1:int, 2:int
    0:int, 1:int, 2:int  # raises
    0, 1, 2:int
    2::int, 2::xsd:integer  #
    #0:"xsd:string", 2:xsd:integer #
    attr:"xsd:string", attr2:"xsd:integer" #
    """
    def test_parse_colspecstr(self):
        for x in map(str.lstrip, self.colspecstr_inputs.splitlines()):
            def _fut(x):  # "function under test"
                return pyline.parse_colspecstr(x)
            output = _fut(x)
            self.assertTrue(output)
            self.assertIsInstance(output, types.GeneratorType)
            #TODO

class TestSortfunc(unittest.TestCase):
    def test_sort_by_001(self):
        iterable = splitwords("a 5 10\nb 6 20\n")
        resiterable = [pyline.PylineResult(
            n=0,
            result=iterable,
            uri=None,
            meta=None)]
        output = pyline.sort_by(resiterable, sortstr='1', reverse=True)
        self.assertIsInstance(output, list)
        self.assertTrue(output)
        self.assertEqual(output[0].result[0][0], "b")
        raise Exception(output)


if __name__ == '__main__':
    sys.exit(unittest.main())
