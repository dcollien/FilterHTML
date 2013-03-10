from setuptools import setup, find_packages

setup(name='FilterHTML',
   version='0.0.1',
   py_modules=['FilterHTML'],
   author='David Collien',
   author_email='david@openlearning.com',
   url='https://github.com/dcollien/FilterHTML/',
   license='MIT',
   description='FilterHTML: A whitelisting HTML filter',
   long_description='FilterHTML: A whitelisting HTML filter. Allows only a well-defined subset of HTML to pass through, with Regex and URL filtering.',
   platforms=['any'],
)
