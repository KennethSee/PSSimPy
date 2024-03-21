from setuptools import setup, find_packages

# Read requirements.txt and use its contents for the install_requires option
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PSSimPy',
    version='0.0.0rc3',
    author='Kenneth See, Hanzholah Shobri',
    author_email='see.k@u.nus.edu, hanzhshobri@gmail.com',
    packages=find_packages(),
    description='A simulator for Large Value Payment Systems',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Specify the content type
    install_requires=requirements,
)
