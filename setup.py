from setuptools import setup

setup(
    name='ncrt',
    version='0.1',
    packages=['ncrt'],
    url='https://github.com/Depau/ncrt',
    license='GNU GPLv3.0',
    author='Davide Depau',
    author_email='davide@depau.eu',
    description='Replace SecureCRT with an ncurses client',
    install_requires=['urwid', 'confuse'],
    include_package_data=True
)
