import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = [
    n.strip() for n in read('requirements.txt').split('\n') if n.strip()
]

setup(
    name = "jiraedit",
    version = "0.0.1",
    author = "Rory Geoghegan",
    author_email = "r.geoghegan@gmail.com",
    description = "Edit your jira cases from the command line."

    packages=['jiraedit', 'tests'],
    install_requires = requirements,
    entry_points={
        'console_scripts': [
            'jiraedit = jiraedit.cmd:run',
        ],
    },
    
    license = "BSD",
    keywords = "jira",
    url = "https://github.com/rgeoghegan/jiraedit",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
