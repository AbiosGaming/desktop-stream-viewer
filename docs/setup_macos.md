## Initial Requirements

First off you should really install Homebrew if you haven't already. It's really nice for handling packages and software on MacOS. See [here](https://brew.sh/index_se.html) for more information about how to install Homebrew.

Also make sure to install the latest VLC build [here](https://nightlies.videolan.org/build/macosx-intel/vlc-3.0.0-20170307-0240-git.dmg)

### Installing packages with Homebrew

Begin with installing Python3 using Homebrew.

```bash
brew install python3
```

If you get a Warning saying that a version of Python3 is already installed, don't worry! This won't cause you any problems.

After having done the above, please run

```bash
brew install pygobject3 --with-python3
```

That `--with-python3` flag at the end is **important**. It makes sure that the package is installed using Python3 instead of Python2 (that 3 at the end of pygobject3 has nothing to do with Python versions).

You should be all set with installing packages using Homebrew now!

### Setting up a virtual environment

virtualenv is this really nice Python tool which helps you create isolated Python environments on your system. What this means for you is that you can keep packages isolated to certain projects, hence not cluttering your system with junk or causing dependency problems (amongst other things)! Awesome, right?

From within the root of the project, run

```bash
virtualenv venv -p python3 --system-site-packages
```

This creates an isolated virtual environment for Python3 with access to GTK libraries.

Now run:

```bash
source venv/bin/activate
```

You're now hooked into your virtual environment. Now the fun begins!

If you want to deactivate your virtual environment and get back to real life, just run:

```bash
deactivate
```

You can always activate your previously configured virtualenv by running the above `source` command again.

### Installing required modules for the project
While activated in your virtual environment (which we named venv), run:

```bash
pip3 install -r requirements.txt --no-binary :all:
```

Now run this command:

```bash
export LD_LIBRARY_PATH="/Applications/VLC.app/Contents/MacOS/lib/"
```

So that the VLC image can be found. You might want to put this in your Terminal config file for the future so you don't need to export it every session.

That's it!

### Run the application
Now for example you can run (from within the root folder of the project):

```bash
python3 main.py https://www.twitch.tv/esl_csgo worst https://www.twitch.tv/esl_csgo worst
```

And you're done! Phew, you can finally breathe out. Happy coding!
