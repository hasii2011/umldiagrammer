
import logging
import logging.config

from json import loads as jsonLoads

from importlib.resources import files
from importlib.resources.abc import Traversable

from click import group
from click import pass_context
from click import pass_obj
from click import secho
from click import version_option

from commands.Environment import Environment

RESOURCES_PACKAGE_NAME:       str = 'tests.resources'
JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfiguration.json"

__version__: str = '0.5'

def setUpLogging():
    """
    """
    traversable: Traversable = files(RESOURCES_PACKAGE_NAME) / JSON_LOGGING_CONFIG_FILENAME

    loggingConfigContent:    str  = traversable.read_text(encoding='utf-8')
    configurationDictionary: dict = jsonLoads(loggingConfigContent)

    logging.config.dictConfig(configurationDictionary)
    logging.logProcesses = False
    logging.logThreads = False


@group(name='uitest')
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@pass_context
def uitest(ctx, verbose: bool = False):
    """
    \b

    \b

    \b

    \b
    """
    setUpLogging()

    environment: Environment = Environment(verbose=verbose)

    ctx.obj = environment

@uitest.command(name='inheritance')
@pass_obj
def inheritance(environment: Environment):
    """
    Signs the internal python zipfile;  May optionally remove some bad files in test/zipimport_data
    """
    secho(f'I am here -- {environment=}')


@uitest.command(name='composition')
@pass_obj
def composition(environment: Environment):
    """
    Signs the internal python zipfile;  May optionally remove some bad files in test/zipimport_data
    """
    secho(f'I am here -- {environment=}')


@uitest.command(name='aggregation')
@pass_obj
def aggregation(environment: Environment):
    """
    Signs the internal python zipfile;  May optionally remove some bad files in test/zipimport_data
    """
    secho(f'I am here -- {environment=}')


@uitest.command(name='checkClass')
@pass_obj
def checkClass(environment: Environment):
    """
    Signs the internal python zipfile;  May optionally remove some bad files in test/zipimport_data
    """
    secho(f'I am here -- {environment=}')


if __name__ == '__main__':
    # noinspection SpellCheckingInspection

    uitest(['inheritance'])
