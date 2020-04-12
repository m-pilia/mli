import json
import socket

from ._repl import repl


def _request(host, port, action, *pargs, **kwargs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            req = {
                'action': action,
                'args': pargs,
                'kwargs': kwargs,
            }
            s.sendall(json.dumps(req).encode())
            ret = json.loads(s.recv(4096).decode())
        except BaseException:
            s.shutdown(socket.SHUT_RDWR)
            raise
    return ret


def main(args):
    def repl_source(expression, background):
        ret = _request(args.host, args.port, 'eval', expression, background=background)
        return ret['out'] + ret['err']

    if args.repl:
        repl(repl_source)
    else:
        print(json.dumps(_request(args.host, args.port, *args.args, nargout=args.nargout)))
