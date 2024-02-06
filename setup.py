from setuptools import setup, find_packages

# Read requirements.txt and use its contents for the install_requires option
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='PSSimPy',
    version='0.1.0',
    author='Kenneth See',
    author_email='see.k@u.nus.edu',
    packages=find_packages(),
    description='A simulator for Large Value Payment Systems',
    long_description=open('README.md').read(),
    install_requires=requirements,
)
