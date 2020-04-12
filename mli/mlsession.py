import io

import matlab.engine


class MLSession:
    def __init__(self, *, option='-nodesktop', session_name=None):
        self._option = option
        self._session_name = session_name
        self._engine = None

        if self._session_name:
            self._connect()
        else:
            self._start_engine()

    def _connect(self):
        try:
            self._engine = matlab.engine.connect_matlab(name=self._session_name)
        except BaseException:
            self._start_engine()

    def _start_engine(self):
        self._engine = matlab.engine.start_matlab(self._option, background=True)

    def _resolve_engine(self):
        if isinstance(self._engine, matlab.engine.FutureResult):
            self._engine = self._engine.result()
            if self._session_name and self._session_name not in matlab.engine.find_matlab():
                self._engine.eval(f'matlab.engine.shareEngine("{self._session_name}")', nargout=0)

    def do(self, action, *args, **kwargs):
        self._resolve_engine()
        if 'nargout' not in kwargs:
            kwargs['nargout'] = 0
        with io.StringIO() as sout, io.StringIO() as serr:
            ret = None
            try:
                ret = getattr(self._engine, action)(*args, stdout=sout, stderr=serr, **kwargs)
            except matlab.engine.RejectedExecutionError:
                self._connect()
                return self.do(action, *args, **kwargs)
            except BaseException:
                pass
            return {
                'ret': ret,
                'out': sout.getvalue(),
                'err': serr.getvalue(),
            }
