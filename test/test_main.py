import logging
import unittest
import unittest.mock as mock

import mli.__main__


@mock.patch('mli.server.main')
class TestServer(unittest.TestCase):

    def test_no_args(self, mock_server_main):
        mli.__main__._main(['server'])
        mock_server_main.assert_called_once()

    def test_session_name(self, mock_server_main):
        session_name = 'foobar'
        mli.__main__._main(['server', '--session-name', session_name])
        mock_server_main.assert_called_once()
        self.assertEqual(mock_server_main.call_args.args[0].session_name, session_name)

    def test_port(self, mock_server_main):
        port = 12345
        mli.__main__._main(['server', '--port', str(port)])
        mock_server_main.assert_called_once()
        self.assertEqual(mock_server_main.call_args.args[0].port, port)

    def test_host(self, mock_server_main):
        host = 'foobar'
        mli.__main__._main(['server', '--host', host])
        mock_server_main.assert_called_once()
        self.assertEqual(mock_server_main.call_args.args[0].host, host)

    def test_log_level(self, mock_server_main):
        log_level = 'INFO'
        mli.__main__._main(['server', '--log-level', log_level])
        mock_server_main.assert_called_once()
        self.assertEqual(mock_server_main.call_args.args[0].log_level, logging.getLevelName(log_level))


@mock.patch('mli.client.main')
class TestClient(unittest.TestCase):

    def test_no_args(self, mock_client_main):
        mli.__main__._main(['client'])
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].repl, False)
        self.assertEqual(mock_client_main.call_args.args[0].nargout, 0)

    def test_port(self, mock_client_main):
        port = 12345
        mli.__main__._main(['client', '--port', str(port)])
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].port, port)

    def test_host(self, mock_client_main):
        host = 'foobar'
        mli.__main__._main(['client', '--host', host])
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].host, host)

    def test_repl(self, mock_client_main):
        mli.__main__._main(['client', '--repl'])
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].repl, True)

    def test_nargout(self, mock_client_main):
        nargout = 10
        mli.__main__._main(['client', '--nargout', str(nargout)])
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].nargout, nargout)

    def test_args(self, mock_client_main):
        args = ['foo', 'bar']
        mli.__main__._main(['client'] + args)
        mock_client_main.assert_called_once()
        self.assertEqual(mock_client_main.call_args.args[0].args, args)


@mock.patch('mli.local.main')
class TestLocal(unittest.TestCase):

    def test_no_args(self, mock_local_main):
        mli.__main__._main(['local'])
        mock_local_main.assert_called_once()
        self.assertEqual(mock_local_main.call_args.args[0].repl, False)
        self.assertEqual(mock_local_main.call_args.args[0].nargout, 0)

    def test_session_name(self, mock_local_main):
        session_name = 'foobar'
        mli.__main__._main(['local', '--session-name', session_name])
        mock_local_main.assert_called_once()
        self.assertEqual(mock_local_main.call_args.args[0].session_name, session_name)

    def test_repl(self, mock_local_main):
        mli.__main__._main(['local', '--repl'])
        mock_local_main.assert_called_once()
        self.assertEqual(mock_local_main.call_args.args[0].repl, True)

    def test_nargout(self, mock_local_main):
        nargout = 10
        mli.__main__._main(['local', '--nargout', str(nargout)])
        mock_local_main.assert_called_once()
        self.assertEqual(mock_local_main.call_args.args[0].nargout, nargout)

    def test_args(self, mock_local_main):
        args = ['foo', 'bar']
        mli.__main__._main(['local'] + args)
        mock_local_main.assert_called_once()
        self.assertEqual(mock_local_main.call_args.args[0].args, args)
