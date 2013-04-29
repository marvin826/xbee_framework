from distutils.core import setup

setup(
    name='XbeeFramework',
    version='0.1.0',
    author='G. Todd Kaiser',
    author_email='gtkaiser@gmail.com',
    packages=['xbeeframework', 'xbeeframework.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/XbeeFramework/',
    license='LICENSE.txt',
    description='Python module for working with Zigbee-based \
                 XBee wireless modules.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
