## Requirements
The application requires `Python3`, `VLC` as well as `GTK+3` installed on the
system. So before we continue, lets go ahead and install these.

On Ubuntu the steps would be:
```
sudo apt update
sudo apt-get install vlc
```

GTK+ and Python3 should already be installed by default, so all we need to do is
install the `gobject-introspection` for Python3.
```
sudo apt-install python3-gi
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
folder named `venv`. The `--system-site-packages` argument is required to access
the shared GTK+ libraries (`gi`).

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
./main.py https://www.twitch.tv/esl_csgo low https://www.twitch.tv/esl_csgo low
```

Which if everything is working correctly should bring up a application window
with the two streams side by side. If no application window appear, be sure to
check that the stream `https://www.twitch.tv/esl_csgo` is currently
broadcasting. If not, go ahead and change the urls the to streams you wish to view.
