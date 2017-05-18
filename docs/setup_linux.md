## Requirements
The application requires `Python3`, `VLC3` as well as `Qt5` installed on the 
system. So before we continue, lets go ahead and install these.

First install the nightly build of VLC:
```
sudo add-apt-repository ppa:videolan/master-daily
sudo apt update
sudo apt-get install vlc
```

If Qt5 is not installed by default, go ahead and install that.
```
sudo apt-get install qt5-default
```
## Getting up to speed
Before continuing, clone the repo to your local computer.
```
git clone https://github.com/kaszim/desktop-stream-viewer.git
```
### Virtualenv
To aviod clashing with your system installed packages, we'll create a virtual
environment with `virtualenv`.

Install `virtualenv` in your preferred way using either a **package manager**
or:
```
pip install virtualenv
```

Create your virtualenvironment using:
```
virtualenv venv --system-site-packages
```
where `venv` is the name of your virtual environment. This will create a new
folder named `venv`. The `--system-site-packages` will allow your to access 
shared libraries from your virtual environment.

Start the virtual environment by using:
```
source venv/bin/activate
```

### Dependencies
Install the project dependencies by issuing the following command inside your
virtual environment.
```
pip install -r requirements.txt
```

### Run the application
Go ahead and test the application by running the following command (inside the
repository folder):
```
./main.py
```

Which if everything is working correctly should bring up a application window
with the stream. If no application window appear, be sure to check that the 
stream `https://www.twitch.tv/esl_csgo` is currently broadcasting. If not, 
go ahead and change the urls the to streams you wish to view.
