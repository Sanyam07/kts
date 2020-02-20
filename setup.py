import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("kts/__version__.py") as fh:
    version = fh.readlines()[-1].split()[-1].strip("\"'")

extras = {
    'zoo': ['sklearn', 'catboost', 'xgboost', 'lightgbm', 'skorch'],
    'selection': ['eli5'],
    'ray': ["ray[tune]"],
}

all_deps = []
for group_name in extras:
    all_deps += extras[group_name]
extras['all'] = all_deps

setuptools.setup(
    name="kts",
    version=version,
    author="Nikita Konodyuk",
    author_email="konodyuk@gmail.com",
    description="A framework for fast and interactive conducting machine learning experiments on tabular data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konodyuk/kts",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',

        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        "License :: OSI Approved :: MIT License",

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        "Operating System :: OS Independent",
    ],
    keywords=[
        "Machine Learning",
        "Parallel Computing",
        "Feature Engineering",
    ],
    extras_require=extras,
    install_requires=[
        "ray>=0.8.1",
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "dill",
        "feather-format",
        "click",
        "python-forge",
        "xxhash"
    ],
    entry_points={
        "console_scripts": ['kts=kts.cli.scripts:cli']
    },
    include_package_data=True
)
