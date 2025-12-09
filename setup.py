"""
Setup script for Dark Triad Experiment
使项目可以作为Python包安装
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dark-triad-experiment",
    version="2.0.0",
    author="Dark Triad Research Team",
    description="面向对象的LLM Dark Triad实验框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dark-triad-experiment",

    # 包配置
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,

    # 依赖
    install_requires=requirements,

    # Python版本要求
    python_requires=">=3.8",

    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    # 命令行脚本
    entry_points={
        'console_scripts': [
            'dark-triad-run=scripts.run_experiment:main',
            'dark-triad-analyze=scripts.analyze:main',
        ],
    },

    # 额外文件
    package_data={
        '': ['*.yaml', '*.yml', '*.txt', '*.md'],
    },
)
