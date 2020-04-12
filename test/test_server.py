import argparse
import json
import logging
import socket
import unittest
import unittest.mock as mock

import mli.mlsession
import mli.server


class TestServer(unittest.TestCase):

    @mock.patch('matlab.engine')
    def test_json_encoder(self, engine_mock):
        class FutureResult:
            pass
        engine_mock.FutureResult = FutureResult
        encoder = mli.server._ML_JSON_Encoder()
        obj = FutureResult()
        self.assertEqual(encoder.default(obj), 'FutureResult')

    def test_serve_client(self):
        parms = {
            'action': 'my_action',
            'args': ['arg1'],
            'kwargs': {'k1': 'v1'},
        }

        connection_mock = mock.MagicMock(spec=socket.socket)
        connection_mock.__enter__ = mock.Mock()
        connection_mock.recv.return_value = json.dumps(parms).encode()

        ml_mock = mock.Mock(spec=mli.mlsession.MLSession)
        ml_mock.do.return_value = {'Success': True}

        expected_response = json.dumps(ml_mock.do.return_value).encode()

        mli.server._serve_client(connection_mock, ml_mock)

        connection_mock.__enter__.assert_called_once()
        ml_mock.do.assert_called_once_with(parms['action'], *parms['args'], **parms['kwargs'])
        connection_mock.sendall.assert_called_once_with(expected_response)

    @mock.patch('mli.server.logger', spec=logging.Logger)
    def test_serve_client_decode_error(self, _):
        connection_mock = mock.MagicMock(spec=socket.socket)
        connection_mock.__enter__ = mock.Mock()
        connection_mock.recv.return_value = '{invalid JSON'.encode()
        ml_mock = mock.Mock(spec=mli.mlsession.MLSession)

        mli.server._serve_client(connection_mock, ml_mock)

        connection_mock.__enter__.assert_called_once()
        ml_mock.do.assert_not_called()
        connection_mock.sendall.assert_called_once()

    @mock.patch('mli.server.logger', spec=logging.Logger)
    def test_serve_client_connection_aborted_error(self, _):
        connection_mock = mock.MagicMock(spec=socket.socket)
        connection_mock.__enter__ = mock.Mock()
        connection_mock.recv.side_effect = ConnectionAbortedError
        ml_mock = mock.Mock(spec=mli.mlsession.MLSession)

        mli.server._serve_client(connection_mock, ml_mock)

        connection_mock.__enter__.assert_called_once()
        ml_mock.do.assert_not_called()
        connection_mock.sendall.assert_not_called()

    @mock.patch('mli.server.MLSession', autospec=True)
    @mock.patch('socket.socket', autospec=True)
    @mock.patch('threading.Thread', autospec=True)
    @mock.patch('mli.server.logger', spec=logging.Logger)
    def test_main(self, logger_mock, thread_mock, socket_mock, ml_mock):
        thread_mock.return_value.start.side_effect = InterruptedError
        connection_mock = socket_mock.return_value.__enter__.return_value
        connection_mock.recv.return_value = '{"success": true}'.encode()
        connection_mock.accept.return_value = ('my_conn', 'my_addr')
        args = {
            'host': 'myhost',
            'port': 12345,
            'log_level': logging.INFO,
            'session_name': 'mysession',
        }
        parsed_args = argparse.Namespace(**args)

        try:
            mli.server.main(parsed_args)
        except InterruptedError:
            pass

        connection_mock.settimeout.assert_called_once_with(3.0)
        connection_mock.bind.assert_called_once_with((args['host'], args['port']))
        connection_mock.listen.assert_called_once()
        connection_mock.accept.assert_called_once()
        thread_mock.assert_called_once()
        thread_mock.return_value.start.assert_called_once()
        thread_mock.call_args.target = mli.server._serve_client
        self.assertEqual(thread_mock.call_args[1]['args'][0], 'my_conn')
