#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import textwrap

# Qt imports
from PyQt5 import QtWidgets

from application import ApplicationWindow


def main():
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if str(e) == "no function 'libvlc_new'":
            sys.exit(textwrap.dedent(
                """
                Crap! Could not call some of the VLC functions...
                Be a darling and check that you've installed libVLC 3.0 correctly <3
                """
            ))

        sys.exit(textwrap.dedent(
            """
            Crap! You've encountered the following error: {error}
            Post an issue about it in the GitHub repo and someone will help you asap! <3
            """.format(error=str(e))
        ))
