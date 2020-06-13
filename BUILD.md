# How to publish package to pypi
```bash
pip3 install --user twine
rm -rf dist
python3 setup.py sdist
twine upload dist/*
```
