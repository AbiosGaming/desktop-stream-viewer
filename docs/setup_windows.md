## Requirements
The application requires `Python3`, `VLC` as well as `GTK+3` to be installed on
the system. So before we continue, lets go ahead and install these.

#### Installing Python
GTK+3 currently requires `Python 3.4.4` to work properly. Go ahead and install
this using the .msi installer from
[here](https://www.python.org/ftp/python/3.4.4/python-3.4.4.amd64.msi). **Be sure
to check the box `make path to the python.exe`, to make it easy to run Python
directly from the command prompt.**

#### Installing VLC
Since this project uses the latest libVLC API, we need to install VLC 3.0 from
[here](https://nightlies.videolan.org/build/win64/vlc-3.0.0-20170220-0448/).

#### Installing GTK+3
* Download the `pygobject` installer from
[here](https://sourceforge.net/projects/pygobjectwin32/).
* Run the installer and check the box GTK+ 3.xx.
**NOTE:** If your going to be involved with GUI development, go ahead and check
Glade 3.xx as well.

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
python.exe main.py https://www.twitch.tv/esl_csgo low https://www.twitch.tv/esl_csgo low
```

Which if everything is working correctly should bring up a application window
with the two streams side by side. If no application window appear, be sure to
check that the stream `https://www.twitch.tv/esl_csgo` is currently
broadcasting. If not, go ahead and change the urls to the streams you wish to
view.
