
from typing import Any
from typing import Dict

from sys import path

from pathlib import Path

from setuptools import setup, find_packages

# The directory containing this file
HERE = Path(__file__).parent

# Add src to sys.path so we can import umldiagrammer for the version
# without requiring PYTHONPATH to be set externally
path.insert(0, str(HERE / "src"))

# noinspection PyPep8
from umldiagrammer import __version__

APP = ['src/umldiagrammer/UmlDiagrammer.py']
DATA_FILES = [('umldiagrammer/resources', ['src/umldiagrammer/resources/loggingConfiguration.json'])]

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

"""

Put the pyapp options in a separate variable to avoid PyCharm type warnings;
py2app options have a complex nested structure that PyCharm's setuptools stubs
sometimes misinterpret. Using Dict[str, Any] provides the necessary flexibility.

Explicitly include codeallyadvanced (and other related packages) in the packages list of the py2app 
options. This forces py2app to bundle the entire package and all
its subpackages, regardless of whether it detects static imports for them

"""
PY2APP_OPTIONS: Dict[str, Any] = {
    'packages': ['codeallyadvanced', 'codeallybasic', 'umlmodel', 'umlshapes', 'umlio', 'umlextensions'],
    'plist': {
        'NSRequiresAquaSystemAppearance': 'False',
        'CFBundleGetInfoString': 'Edits Diagrammer UML Files',
        'CFBundleIdentifier': 'umldiagrammer',
        'CFBundleShortVersionString': __version__,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'umldiagrammer',
                'CFBundleTypeRole': 'Editor',
                'CFBundleTypeExtensions': ['udt', 'xml']
            }
        ],
        'LSMinimumSystemVersion': '26.5',
        'LSEnvironment': {
            'APP_MODE': 'True',
            'PYTHONOPTIMIZE': '1',
        },
        'LSMultipleInstancesProhibited': 'True',
    }
}

setup(
    name='UmlDiagrammer',
    version=__version__,
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,

    url='https://github.com/hasii2011/umldiagrammer',
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='A Next Generation Python UML Tool',
    long_description='A Second Generation UML Diagrammer.',
    options={
        'py2app': PY2APP_OPTIONS
    },
    setup_requires=['py2app'],
)
