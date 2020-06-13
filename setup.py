from setuptools import setup, find_packages

setup(
    name="easybox",
    version="0.0.3",
    keywords=["easybox", "Detection", 'Python', 'Deep-learning', 'TKinter'],
    description="A simple but powerful bounding box annotation tool by Python",
    long_description="A simple but powerful bounding box annotation tool by Python",
    license="MIT Licence",

    url="https://github.com/vra/easybox",
    author="Yunfeng Wang",
    author_email="wyf.brz@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['pillow', 'tk'],

    scripts=[],
    entry_points={
        'console_scripts': [
            'easybox=easybox.main:main'
        ]
    }
)
