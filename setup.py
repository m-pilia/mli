import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mli',
    version='0.0.1',
    author='Martino Pilia',
    author_email='martino.pilia@gmail.com',
    description='Cross platform shell interface for MATLAB',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/m-pilia/mli',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
