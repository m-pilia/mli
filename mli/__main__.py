import argparse
import logging
import sys


def _main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Command')
    subparsers.required = True

    server_parser = subparsers.add_parser('server', help='Start a server')
    server_parser.add_argument('--session-name', type=str, default=None, help='Name for shared session')
    server_parser.add_argument('--host', type=str, default='127.0.0.1', help='Server address')
    server_parser.add_argument('--port', type=int, default=65500, help='Server port')
    server_parser.add_argument('--log-level', type=logging.getLevelName, default=logging.WARNING)

    client_parser = subparsers.add_parser('client', help='Start a client')
    client_parser.add_argument('--host', type=str, default='127.0.0.1', help='Address to connect')
    client_parser.add_argument('--port', type=int, default=65500, help='Port to connect')
    client_parser.add_argument('--repl', action='store_true', help='Start a REPL')
    client_parser.add_argument('--nargout', type=int, default=0, help='Number of desired return values')
    client_parser.add_argument('args', nargs=argparse.REMAINDER, help='Call args')

    local_parser = subparsers.add_parser('local', help='Perform local actions')
    local_parser.add_argument('--session-name', type=str, default=None, help='Name for shared session')
    local_parser.add_argument('--repl', action='store_true', help='Start a REPL')
    local_parser.add_argument('--nargout', type=int, default=0, help='Number of desired return values')
    local_parser.add_argument('args', nargs=argparse.REMAINDER, help='Call arguments')

    args = parser.parse_args(argv)

    if args.command == 'server':
        from .server import main as server_main
        server_main(args)
    elif args.command == 'client':
        from .client import main as client_main
        client_main(args)
    elif args.command == 'local':
        from .local import main as local_main
        local_main(args)
    else:
        raise ValueError(f'Unexpected command {args.command}')


if __name__ == '__main__':
    _main(sys.argv[1:])
