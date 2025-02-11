from setuptools import setup, find_packages

setup(
    name="configs_cli",
    version="0.3.0",
    description="CLI tool for setting up a minimal headless development environment with zsh, neovim, and tmux",
    author="Your Name",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'configs-cli=configs_cli.main:main',
        ],
    },
    python_requires=">=3.9",
    install_requires=[
        'rich>=13.0.0',
        'setuptools>=64',
        'wheel',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

