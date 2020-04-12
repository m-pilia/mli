import json

from ._repl import repl
from .mlsession import MLSession


def main(args):
    ml = MLSession(session_name=args.session_name)

    def repl_source(expression, background):
        ret = ml.do('eval', expression, background=background)
        return ret['out'] + ret['err']

    if args.repl:
        repl(repl_source)
    else:
        print(json.dumps(ml.do(*args.args, nargout=args.nargout)))
