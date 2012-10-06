from distutils.core import setup

from win_unc import __version__

def get_desc():
    try:
        return open('README.rst').read()
    except IOError:
        return ''


setup(
    name='win_unc',
    packages=['win_unc', 'win_unc.internal'],
    version=__version__,
    description='UNC network drive handling and mounting for Windows',
    author='Elliot Cameron',
    author_email='elliot.cameron@covenanteyes.com',
    url='https://github.com/CovenantEyes/py_win_unc',
    download_url='https://github.com/CovenantEyes/py_win_unc/tarball/v' + __version__,
    keywords=['directory', 'folder', 'unc', 'local', 'remote', 'path'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    long_description=get_desc(),
)
