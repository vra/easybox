# easybox
A simple but powerful bounding box annotation tool by Python

## Install
### 1. Linux
```bash
pip3 install --user easybox
```
Then run below command in termianl to begin:
```bash
easybox
```

### 2. Windows
Download execute file from release page: <https://github.com/vra/easybox/releases>.
Directly run `*.exe` to begin.


## How to use
### 1. Video Demo
### 2. Shortcuts
|Operate|UI operation|Shortcut|
|--|--|--|
|Open folder | File->Open| Ctrl-o|
|Save annotation | Save Button| Ctrl-s|
|Load previous image | Previous Button|<-, Middle mouse button|
|Load Next image | Next Button|->, Right mouse button|
|Load Next image | Next Button|->, Right mouse button|
|Delete previous bbox | |Ctrl-z|
|Open help window | |Ctrl-h|
|Open about window | |Ctrl-a|
|Exit |File->Exit |Ctrl-q|


## Build from source
### 1. Linux
```bash
git clone https://github.com/vra/easybox
cd easybox
python3 setup.py install --user
```
Then run below command in termianl to begin:
```bash
easybox
```

### 2. Windows
Install Pyinstaller first: `pip3 install --user pyinstaller`.

Then run:
```bash
pyinstaller.exe -F -w  ./easybox/main.py
```
A execute file namede `main.exe` will be created in `dist` folder, you can directly run it.
```bash
./dist/main.exe
```

## Acknowledgement
This project is inspired by [BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool), many thanks to the author.
