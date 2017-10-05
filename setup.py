from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='rayr',
    version='0.0.2',
    description='Replicate all your repositories',
    long_description=readme(),
    url='http://github.com/berenm/rayr',
    author='Beren Minor',
    author_email='beren.minor+github@example.com',
    license='UNLICENSE',
    packages=['rayr'],
    entry_points={
        'rayr': ['rayr=rayr.__main__:main'],
    },
    install_requires=[
        'requests',
        'requests-oauthlib',
    ],
)
