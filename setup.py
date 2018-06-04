from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='rayr',
    version='0.0.4',
    description='Replicate all your repositories',
    long_description=readme(),
    url='https://gitlab.com/berenm/rayr',
    author='Beren Minor',
    author_email='beren.minor+git@gmail.com',
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
