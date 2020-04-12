import io
import unittest
import unittest.mock as mock

import mli._repl


def mock_input(values):
    def fun(*args, **kwargs):
        if not hasattr(fun, 'count'):
            fun.count = 0
        else:
            fun.count += 1
        return values[fun.count]
    return fun


class TestReadline(unittest.TestCase):
    @mock.patch('builtins.input', side_effect=mock_input(['x']))
    def test_simple_expression(self, _):
        res = mli._repl._readline()
        self.assertEqual(res, 'x')

    @mock.patch('builtins.input', side_effect=mock_input(['x + ...', '1']))
    def test_continued_expression(self, _):
        res = mli._repl._readline()
        self.assertEqual(res, 'x + ...\n1')

    @mock.patch('builtins.input', side_effect=mock_input(['for x = 1:10\\', 'x\\', 'end']))
    def test_continued_statement(self, _):
        res = mli._repl._readline()
        self.assertEqual(res, 'for x = 1:10\nx\nend')


class TestRepl(unittest.TestCase):
    def setUp(self):
        self.source = mock.Mock(side_effect=lambda e, b: f'result {e}')

    @mock.patch('builtins.input', side_effect=mock_input(['x', 'exit']))
    def test_one_statement(self, mi):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            mli._repl.repl(self.source)
            self.assertEqual(stdout.getvalue(), 'result x\n')
        self.source.assert_called_once_with('x', False)

    @mock.patch('builtins.input', side_effect=mock_input(['-async x', 'exit']))
    def test_one_statement_async(self, _):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            mli._repl.repl(self.source)
            self.assertEqual(stdout.getvalue(), 'result x\n')
        self.source.assert_called_once_with('x', True)

    @mock.patch('builtins.input', side_effect=mock_input(['x', 'y', 'exit']))
    def test_two_statements(self, _):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            mli._repl.repl(self.source)
            self.assertEqual(stdout.getvalue(), 'result x\nresult y\n')
        self.source.assert_any_call('x', False)
        self.source.assert_any_call('y', False)
