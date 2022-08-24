from importlib.metadata import entry_points
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# The text of the README file
REQUIRE = (HERE / "requirements.txt").read_text()

setup(
    name = 'wtrobot',
    version = '1.0.0-rc.3',
    description = 'WTRobot is keyword driven web testing framework',
    long_description = README,
    long_description_content_type="text/markdown",
    url = 'https://github.com/wtrobot/wtrobot',
    author = 'Vishal Vijayraghavan',
    author_email = 'vishalvvr@fedoraproject.org',
    license = 'MIT',
    classifiers = [
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    packages=["wtrobot"],
    include_package_data=True,
    entry_points={
        "console_scripts":[
            "wtrobot=wtrobot.__main__:main",
        ]
    },
    install_requires = REQUIRE
)