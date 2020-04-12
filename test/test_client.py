import argparse
import io
import json
import unittest
import unittest.mock as mock

import mli.client


class TestClient(unittest.TestCase):

    @mock.patch('socket.socket', autospec=True)
    def test_request(self, socket_mock):
        connection_mock = socket_mock.return_value.__enter__.return_value
        connection_mock.recv.return_value = '{"success": true}'.encode()
        host = 'myhost'
        port = 10000
        action = 'some_action'
        args = ['arg1']
        kwargs = {'k1': 'v1'}
        expected_req = json.dumps({
            'action': action,
            'args': args,
            'kwargs': kwargs,
        }).encode()

        ret = mli.client._request(host, port, action, *args, **kwargs)

        self.assertEqual(ret, {'success': True})
        connection_mock.connect.assert_called_once_with((host, port))
        connection_mock.sendall.assert_called_once_with(expected_req)
        connection_mock.recv.assert_called_once()

    @mock.patch('mli.client.repl')
    def test_main_repl(self, repl_mock):
        args = argparse.Namespace(host='myhost', port=12345, repl=True)

        mli.client.main(args)

        repl_mock.assert_called_once()

    @mock.patch('mli.client._request')
    def test_main_command(self, request_mock):
        request_mock.return_value = {'Success': True}
        args = {
            'host': 'myhost',
            'port': 12345,
            'repl': False,
            'args': ['arg1'],
            'kwargs': {'k1': 'v1'},
            'nargout': 10,
        }
        parsed_args = argparse.Namespace(**args)

        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:

            mli.client.main(parsed_args)

            self.assertEqual(stdout.getvalue(), f'{json.dumps(request_mock.return_value)}\n')

        request_mock.assert_called_once_with(args['host'], args['port'], *args['args'], nargout=args['nargout'])
