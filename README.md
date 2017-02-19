## Description
This is a **proof of concept example** GTK+3 application for playing live video streams using Streamlink and libVLC callbacks. It provides complete access to the stream data provided by Streamlink and full coverage of the libVLC API.

**Since I'm lazy I've only added X11 support for the VLC playback. If you feel the urge to run non X11 systems, go ahead and add support for this by setting the player by window handle instead of xid.**

## Requirements
The application requires `Python3`, `VLC` as well as `GTK+3` installed on the system. So before we go ahead and continue, let install these.

On Ubuntu the steps would be (correct me if I'm wrong):
```
sudo apt update
sudo apt-get install vlc
```

GTK+ should already be installed by default, all we need to do is install the `gobject-introspection` for Python3.
```
sudo apt-install python3-gi
```

I'm not aware of the steps for other systems than \*nix derivatives. If you find the steps, go ahead and add these! \<3

## Getting up to speed
Before starting, clone the repo to your local computer.

### Virtualenv
To aviod clashing with your system installed packages, we'll create a virtual environment with `virtualenv`.

Install `virtualenv` in your preferred way using either a **package manager** or:
```
pip install virtualenv
```

Create your virtualenvironment using: 
```
virtualenv venv --system-site-packages
```
where `venv` is the name of your virtual environment. This will create a new folder named `venv`. The `--system-site-packages` argument is required to access the shared GTK+ libraries (`gi`).

Start the virtual environment by using:
```
source venv/bin/activate
```

### Dependencies
Install the `pip` dependencies by issuing the following command inside your virtual environment.
```
pip install -r requirements.txt
```

### Ready for takeof (hopefully)
Go ahead and test this ghetto application by running the command:
```
./main.py https://www.twitch.tv/esl_csgo low https://www.twitch.tv/esl_csgo low
```

Which if everything is working correctly should bring up a application window with the two streams side by side. 

## Setup environment on Windows! (Ninja cat time!)

#### 1. Python 3.4.4
> install python 3.4.4 x64, 
on install check the box: make path to the python.exe
#### 2. Get VLC!
>https://nightlies.videolan.org/build/win64/ 
run an .exe version for 3.0.0

#### 3. GTK+ 3
> Download pygobject installer: https://sourceforge.net/projects/pygobjectwin32/
Run the installer!
Check GTK+ 3.xx.y
Press next.
Press next.
Check Glade 3.yy (If you wish to have the gui designer)
Press next.
Press yes. 
DONE!

#### 4. Clone the repo:
 ```
 git clone https://github.com/kaszim/desktop-stream-viewer.git
 ```
 
#### 5. Install required modules using pip installer
> cd into the repo
First make sure pip and setuptools is on the latest version:
```
python -m pip install -U pip setuptools
```
Then install streamlink globally: 
```
pip install streamlink
```
 
#### 6. Run this ghetto application, yes you will be part of making it into a real application!
  ```
  python.exe "<pathToRepo>\main.py" https://www.twitch.tv/esl_csgo low https://www.twitch.tv/esl_csgo low
  ```
