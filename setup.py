from setuptools import setup, find_packages

setup(
    name='latex-progress',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'latex-progress=latex_progress.cli:cli',
        ],
    },
    author='chreisinger',
    description='LaTeX Writing Progress Tracker CLI',
    include_package_data=True,
    python_requires='>=3.7',
)
