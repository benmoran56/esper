#!/usr/bin/env python

import os
import sys
import shlex
import shutil

from subprocess import call


HERE = os.path.dirname(os.path.abspath(__file__))


def clean():
    """Clean up all build & test artifacts."""
    dirs = [os.path.join(HERE, 'dist'),
            os.path.join(HERE, 'build'),
            os.path.join(HERE, '_build'),
            os.path.join(HERE, 'esper.egg-info'),
            os.path.join(HERE, '.pytest_cache'),
            os.path.join(HERE, '.mypy_cache')]

    for d in dirs:
        print(f'   --> Deleting: {d}')
        shutil.rmtree(d, ignore_errors=True)


def dist():
    """Create sdist and wheels, then upload to PyPi."""
    sdist_cmd = "python setup.py sdist --formats=zip" 
    wheel_cmd = "python setup.py bdist_wheel" 
    twine_cmd = "twine upload dist/esper*"
    call(shlex.split(sdist_cmd))
    call(shlex.split(wheel_cmd))
    call(shlex.split(twine_cmd))


if __name__ == '__main__':

    def _print_usage():
        print('Usage: make.py <command>')
        print('  where commands are:', ', '.join(avail_cmds))
        print()
        for name, cmd in avail_cmds.items():
            print(name, '\t', cmd.__doc__)

    avail_cmds = dict(clean=clean, dist=dist)

    try:
        command = avail_cmds[sys.argv[1]]
    except IndexError:
        _print_usage()

    except KeyError:
        print('Unknown command:', sys.argv[1])
        print()
        _print_usage()
    else:
        command()
