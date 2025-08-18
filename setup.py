
from setuptools import setup
from setuptools import find_packages

import pathlib

from umldiagrammer import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

APP = ['umldiagrammer/UmlDiagrammer.py']
DATA_FILES = [('umldiagrammer/resources', ['pyut/resources/loggingConfiguration.json']),
              ('umldiagrammer/resources/img', ['pyut/resources/img/pyut.ico']),
              ]
OPTIONS = {}

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name='umldiagrammer',
    version=__version__,
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(include=['pyut.*']),
    include_package_data=True,
    zip_safe=False,

    url='https://github.com/hasii2011/umldiagrammer',
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='A Next Generation Python UML Tool',
    long_description='A Second Generation UML Diagrammer.',
    options=dict(py2app=dict(
        plist=dict(
            NSRequiresAquaSystemAppearance='False',
            CFBundleGetInfoString='Edits Diagrammer UML Files',
            CFBundleIdentifier='umldiagrammer',
            CFBundleShortVersionString=__version__,
            CFBundleDocumentTypes=[
                {'CFBundleTypeName': 'umldiagrammer'},
                {'CFBundleTypeRole': 'Editor'},
                {'CFBundleTypeExtensions':  ['udt', 'xml']}
            ],
            LSMinimumSystemVersion='12',
            LSEnvironment=dict(
                APP_MODE='True',
                PYTHONOPTIMIZE='1',
            ),
            LSMultipleInstancesProhibited='True',
        )
    ),
    ),
    setup_requires=['py2app'],
    install_requires=[
        'codeallybasic>=1.15.0',
        'codeallyadvanced>=1.4.3',
        'pyutmodelv2>=2.2.6',
        'umlshapes>=0.9.50',
        'umlio>=0.4.2',
        'wxPython==4.2.3',
    ]
)
