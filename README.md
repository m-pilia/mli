# mli - Shell interface for MATLAB
[![Actions Status](https://github.com/m-pilia/mli/workflows/Build%20and%20test/badge.svg)](https://github.com/m-pilia/mli/actions?query=workflow%3A"Build+and+test")
[![Codecov](https://codecov.io/gh/m-pilia/mli/branch/master/graph/badge.svg)](https://codecov.io/gh/m-pilia/mli/branch/master)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/m-pilia/mli/blob/master/LICENSE)

This package implements a cross-platform shell interface for MATLAB.

# Motivation

While on Linux it is possible to run MATLAB as a headless REPL (with `matlab
-nodesktop`), this is [not possible on
Windows](https://blogs.mathworks.com/community/2010/02/22/launching-matlab-without-the-desktop/),
where the `-nodesktop` option launches a GUI application implementing a
graphical terminal. This makes it impossible to open a MATLAB shell inside a
terminal multiplexer or within another program (e.g. Vim, Emacs).

This package leverages the [MATLAB Engine API for
Python](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html)
to implement a shell interface, using a client-server model, allowing to attach
multiple shells to a running MATLAB session.

# Requirements

This package requires a working MATLAB installation and the
[MATLAB Engine API for Python](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

# Usage

This package provides three commands:
```sh
python -m mli --help

# Run a MATLAB command or start a REPL locally (whitout network)
python -m mli local --help

# Start a server, allowing to attach client shells
python -m mli server --help

# Attach a client to a running server
python -m mli client --help
```

When running the shell (either locally or as a client), it is possible to start
a REPL (`--repl`) or to run a single MATLAB command (providing the command as a
positional argument).

When running a single command, the result is returned in form of a JSON
message, with keys `ret` (for the return value), `out` (stdout from the
command), and `err` (stderr from the command). The number of desired return
values can be specified in the call with the `--nargout` parameter (for the
details, please refer to the [upstream
documentation](https://mathworks.com/help/matlab/apiref/matlab.engine.matlabengine-class.html)).

It is possible to attach multiple shells (local or clients connected to a
server) to the same MATLAB engine session, sharing the same workspace. To do
so, use the `--session-name` parameter and specify the same session name for
the servers and for local shells.

# Example

```bash
# Start a server
python -m mli server --session-name mysession --host '127.0.0.1' --port 5000 --log-level INFO

# On a separate shell, attach a client
python -m mli mysession client --host '127.0.0.1' --port 5000 --repl
```

# Limitations

In its current implementation, this shell does not handle interactive
execution, e.g. commands requiring user input, `keyboard` commands,
breakpoints, and such. These commands make the shell hang.

It is however possible to use breakpoints in command line debugging by
launching a script in one shell, and then attaching a second shell to the same
session to access the workspace, inspect variables, and issue `dbcont` commands
to resume execution.

# LICENSE

MIT
