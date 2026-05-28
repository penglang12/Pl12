"""AI Employee - 新媒体运营自动化系统"""
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent

# 读取 requirements.txt
requirements = (HERE / "requirements.txt").read_text(encoding="utf-8").splitlines()
install_requires = [line for line in requirements if line and not line.startswith("#")]

setup(
    name="ai-employee",
    version="0.1.0",
    description="AI Employee - 新媒体运营自动化系统",
    long_description=(
        (HERE / "README.md").read_text(encoding="utf-8")
        if (HERE / "README.md").exists()
        else ""
    ),
    long_description_content_type="text/markdown",
    author="AI Employee Team",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "ai-employee=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
