import pkgutil
import logging
from cifsdk.constants import LOG_FORMAT, RUNTIME_PATH, LOGLEVEL, VERSION
from argparse import ArgumentParser
import signal
from . import color

import yaml
import os


def read_config(args):
    options = {}
    if os.path.isfile(args.config):
        f = file(args.config)
        config = yaml.load(f)
        if config.get('client'):
            config = config['client']
        f.close()
        if not config:
            print("Unable to read {} config file".format(args.config))
            raise SystemExit
        for k in config:
            if not options.get(k):
                options[k] = config[k]
    else:
        print("Unable to read {} config file".format(args.config))
        raise SystemExit

    return options


def get_argument_parser():
    BasicArgs = ArgumentParser(add_help=False)
    BasicArgs.add_argument('-v', '--verbose', dest='verbose', action="store_true", help="logging level: INFO")
    BasicArgs.add_argument('-d', '--debug', dest='debug', action="store_true", help="logging level: DEBUG")
    BasicArgs.add_argument('-V', '--version', action='version', version=VERSION)
    BasicArgs.add_argument(
        "--runtime-path", help="specify the runtime path [default %(default)s]", default=RUNTIME_PATH
    )
    return ArgumentParser(parents=[BasicArgs], add_help=False)


def load_plugin(path, plugin):
    p = None
    for loader, modname, is_pkg in pkgutil.iter_modules([path]):
        if modname == plugin:
            p = loader.find_module(modname).load_module(modname)
            p = p.Plugin

    return p


def setup_logging(args):
    loglevel = logging.getLevelName(LOGLEVEL)

    if args.verbose:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG

    console = logging.StreamHandler()
    logging.getLogger('').setLevel(loglevel)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(console)


def setup_signals(name):
    logger = logging.getLogger(__name__)

    def sigterm_handler(_signo, _stack_frame):
        logger.info('SIGTERM Caught for {}, shutting down...'.format(name))
        raise SystemExit

    signal.signal(signal.SIGTERM, sigterm_handler)


def setup_runtime_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)
