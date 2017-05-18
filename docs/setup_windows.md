## Requirements
The application requires `Python3` and `VLC3+` to be pre-installed on
the system. So before we continue, lets go ahead and install these.

#### Installing Python
PyQT5 currently requires `Python 3.5` or higher to work properly. You could try
to compile from source if you want to, but I would suggest just upping your
Python version to any version that is supported by SIP (which PyQT5 relies on) on 
[PYPI](https://pypi.python.org/pypi/SIP/4.19).
You can grab python from [here](https://www.python.org/downloads/release/python-361/).
Currently the latest version is _3.6.1_ so we will grab that.

**Be sure to check the box `make path to the python.exe`, to make it easy to run Python
directly from the command prompt.**

#### Installing VLC
Since this project uses the latest libVLC API, we need to install VLC 3.0 from
[here](https://nightlies.videolan.org/build/win64/vlc-3.0.0-20170220-0448/).

## Getting up to speed
Before continuing, clone the repo to your local computer.
```
git clone https://github.com/kaszim/desktop-stream-viewer.git
```

### Dependencies
Before we go ahead and install the dependencies, update the tool `pip` by
issuing the following command:
```
python -m pip install -U pip setuptools
```

Change into the repository folder and install the project specific dependencies
by using:
```
pip install -r requirements.txt
```

### Run the application
Go ahead and test the application by running the following command (inside the
repository folder):
```
py main.py
```

Which if everything is working correctly should bring up a application window
with the two streams side by side. If no application window appear, be sure to
check that the stream `https://www.twitch.tv/esl_csgo` is currently
broadcasting. If not, go ahead and change the urls to the streams you wish to
view.
