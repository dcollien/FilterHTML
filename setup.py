from setuptools import setup

setup(
   name='FilterHTML',
   version='0.2.1',
   py_modules=['FilterHTML'],
   author='David Collien',
   author_email='me@dcollien.com',
   url='http://dcollien.github.com/FilterHTML/',
   license='MIT',
   description='FilterHTML: A whitelisting HTML filter',
   long_description='FilterHTML: A whitelisting HTML filter. Allows only a well-defined subset of HTML to pass through, with style parsing and options for Regex and URL filtering.',
   platforms=['any'],
)
