import argparse
import io
import json
import unittest
import unittest.mock as mock

import mli.local


class TestLocal(unittest.TestCase):

    @mock.patch('mli.local.MLSession', autospec=True)
    @mock.patch('mli.local.repl')
    def test_main_repl(self, repl_mock, ml_mock):
        args = {
            'session_name': 'mysession',
            'repl': True,
            'args': ['arg1'],
            'nargout': 10,
        }
        parsed_args = argparse.Namespace(**args)

        mli.local.main(parsed_args)

        repl_mock.assert_called_once()
        ml_mock.assert_called_once()

    @mock.patch('mli.local.MLSession', autospec=True)
    def test_main_command(self, ml_mock):
        ml_do_mock = ml_mock.return_value.do
        ml_do_mock.return_value = '{"Success": true}'
        args = {
            'session_name': 'mysession',
            'repl': False,
            'args': ['arg1'],
            'nargout': 10,
        }
        parsed_args = argparse.Namespace(**args)

        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:

            mli.local.main(parsed_args)

            self.assertEqual(stdout.getvalue(), f'{json.dumps(ml_do_mock.return_value)}\n')

        ml_mock.assert_called_once()
        ml_do_mock.assert_called_once_with(*args['args'], nargout=args['nargout'])
