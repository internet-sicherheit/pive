from setuptools import setup, find_packages

setup(
    name='pive',
    packages=['pive', 'pive/visualization'],
    use_2to3=True,
    include_package_data=True,
    version='0.3.202104061100',
    url='https://github.com/daboth/pive',
    download_url='https://github.com/daboth/pive/tarball/0.3.4',
    license='BSD',
    description='Interactive visualization tool',
    long_description=open('README.txt').read(),
    author='David Bothe',
    author_email='davbothe@googlemail.com',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=['jinja2','py-dateutil', 'pyveplot',  'networkx', 'requests'],
    test_suite = 'testcases'

)
