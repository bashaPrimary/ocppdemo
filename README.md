OCPP Demo
=========

Overview
--------
A simple package adhering to the [OCPP 2.0.1](https://www.openchargealliance.org/protocols/ocpp-201/) protocol and demonstrates using the [ocpp](https://github.com/mobilityhouse/ocpp) library on both the server side and the client side.

Setup
-----
* Run `make install` to build the world

How to:
-------
* `make lint`: cleans up using ([black](https://pypi.org/project/black/), [flake8](https://pypi.org/project/flake8/), [mypy](https://pypi.org/project/mypy/))
* `make tests`: runs the unit tests
* `make run`: runs the server in the background and spins up the client
    - :warning: PORT 9000 will be consumed by the server process, and process will need to be killed if the script is terminated.



Development Requirements
------------------------

* [Python 3.10.0 or higher](https://www.python.org/downloads/release/python-3100/) Just for compatibility reasons make sure you have the right version of python installed, or use [pyenv](https://github.com/pyenv/pyenv)
to emulate the right python version

Troubleshooting
---------------

* If you get an error like this after installing pyenv and pointing to the right python version:
```bash
make: *** [lint] Error 1
(base) basha@Ahmeds-iMac ocppdemo % ./bin/run-black.sh

Current Python version (3.9.12) is not allowed by the project (^3.10).
Please change python executable via the "env use" command.
```
Then try running these commands in the root:
```bash
$ rm -rf .venv
$ poetry env use 3.10.0
$ poetry install
```
This forces poetry to look at the pyenv version instead
