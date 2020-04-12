import unittest
import unittest.mock as mock

from mli.mlsession import MLSession


class FutureResult:
    def result(self):
        return mock.Mock()


class TestMLSession(unittest.TestCase):
    def setUp(self):
        with mock.patch.object(MLSession, '_connect'), mock.patch.object(MLSession, '_start_engine'):
            self.ml = MLSession()

    @mock.patch.object(MLSession, '_connect')
    @mock.patch.object(MLSession, '_start_engine')
    def test_init_without_session_name(self, mock_start_engine, mock_connect):
        MLSession()

        mock_start_engine.assert_called_once()
        mock_connect.assert_not_called()

    @mock.patch.object(MLSession, '_connect')
    @mock.patch.object(MLSession, '_start_engine')
    def test_init_with_session_name(self, mock_start_engine, mock_connect):
        session_name = 'my_session'

        ml = MLSession(session_name=session_name)

        mock_start_engine.assert_not_called()
        mock_connect.assert_called_once()
        self.assertEqual(ml._session_name, session_name)

    @mock.patch.object(MLSession, '_start_engine')
    @mock.patch('matlab.engine')
    def test_connect_successful(self, mock_engine, mock_start_engine):
        self.ml._session_name = 'my_session'

        self.ml._connect()

        mock_engine.connect_matlab.assert_called_once_with(name=self.ml._session_name)
        mock_start_engine.assert_not_called()

    @mock.patch.object(MLSession, '_start_engine')
    @mock.patch('matlab.engine')
    def test_connect_failure(self, mock_engine, mock_start_engine):
        mock_engine.connect_matlab.side_effect = BaseException
        self.ml._session_name = 'my_session'

        self.ml._connect()

        mock_engine.connect_matlab.assert_called_once_with(name=self.ml._session_name)
        mock_start_engine.assert_called_once()

    @mock.patch('matlab.engine')
    def test_start_engine(self, mock_engine):
        mock_engine.start_matlab.return_value = 'my_engine'
        self.ml._start_engine()

        mock_engine.start_matlab.assert_called_once_with(self.ml._option, background=True)
        self.assertEqual(mock_engine.start_matlab.return_value, self.ml._engine)

    @mock.patch('matlab.engine')
    def test_resolve_engine_without_session_name(self, mock_engine):
        mock_engine.FutureResult = FutureResult
        self.ml._engine = FutureResult()

        self.ml._resolve_engine()

        self.assertTrue(isinstance(self.ml._engine, mock.Mock))
        self.ml._engine.eval.assert_not_called()

    @mock.patch('matlab.engine')
    def test_resolve_engine_with_session_name(self, mock_engine):
        mock_engine.FutureResult = FutureResult
        self.ml._engine = FutureResult()
        self.ml._session_name = 'my_session'

        self.ml._resolve_engine()

        self.assertTrue(isinstance(self.ml._engine, mock.Mock))
        self.ml._engine.eval.assert_called_once_with(f'matlab.engine.shareEngine("{self.ml._session_name}")', nargout=0)

    @mock.patch('matlab.engine')
    def test_resolve_engine_already_resolved(self, mock_engine):
        mock_engine.FutureResult = FutureResult
        self.ml._engine = mock.Mock()

        self.ml._resolve_engine()

        self.ml._engine.result.assert_not_called()

    @mock.patch('mli.mlsession.io', autospec=True)
    @mock.patch.object(MLSession, '_resolve_engine')
    @mock.patch.object(MLSession, '_connect')
    def test_do(self, mock_connect, mock_resolve_engine, mock_io):
        mock_io.StringIO.return_value.__enter__.return_value.getvalue.return_value = 'myoutput'
        self.ml._engine = mock.Mock()
        self.ml._engine.myaction.return_value = 'myret'

        action = 'myaction'
        args = ['arg1']
        kwargs = {'k1': 'v1'}

        out = self.ml.do(action, *args, **kwargs)

        mock_resolve_engine.assert_called_once()
        mock_connect.assert_not_called()
        self.ml._engine.myaction.assert_called_once()
        self.assertEqual(out['ret'], 'myret')
        self.assertEqual(out['out'], 'myoutput')
        self.assertEqual(out['err'], 'myoutput')

    @mock.patch('mli.mlsession.io', autospec=True)
    @mock.patch('matlab.engine')
    @mock.patch.object(MLSession, '_resolve_engine')
    @mock.patch.object(MLSession, '_connect')
    def test_do_with_connection_and_exception(self, mock_connect, mock_resolve_engine, mock_engine, mock_io):
        """ First call to action fails with RejectedExecutionError, second call fails with BaseException. """
        class RejectedExecutionError(Exception):
            pass

        def secondCallFails():
            self.ml._engine.myaction.side_effect = BaseException

        mock_io.StringIO.return_value.__enter__.return_value.getvalue.return_value = 'myoutput'
        mock_engine.RejectedExecutionError = RejectedExecutionError
        self.ml._engine = mock.Mock()
        self.ml._engine.myaction.side_effect = RejectedExecutionError
        mock_connect.side_effect = secondCallFails

        out = self.ml.do('myaction')

        mock_connect.assert_called_once()
        self.assertEqual(mock_resolve_engine.call_count, 2)
        self.assertEqual(out['ret'], None)
        self.assertEqual(out['out'], 'myoutput')
        self.assertEqual(out['err'], 'myoutput')
