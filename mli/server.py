import json
import logging
import socket
import sys
import threading

import matlab.engine

from .mlsession import MLSession

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class _ML_JSON_Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, matlab.engine.FutureResult):
            return 'FutureResult'
        return super(_ML_JSON_Encoder, self).default(o)


def _serve_client(connection, matlab_session):
    try:
        with connection:
            data = bytes.decode(connection.recv(4096))
            logger.info('Serving request: %s', data)
            try:
                data = json.loads(data)
                ret = matlab_session.do(data['action'], *data['args'], **data['kwargs'])
                connection.sendall(json.dumps(ret, cls=_ML_JSON_Encoder).encode())
            except json.decoder.JSONDecodeError:
                msg = sys.exc_info()
                logger.error(msg)
                connection.sendall(json.dumps({'ret': None, 'out': str(msg)}).encode())
    except ConnectionAbortedError:
        return


def main(args):
    logger.setLevel(args.log_level)

    ml = MLSession(session_name=args.session_name)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3.0)
        s.bind((args.host, args.port))
        s.listen()
        logger.info('Waiting for incoming connections...')
        while True:
            try:
                conn, _ = s.accept()
                threading.Thread(target=_serve_client, args=(conn, ml)).start()
            except socket.timeout:
                continue
