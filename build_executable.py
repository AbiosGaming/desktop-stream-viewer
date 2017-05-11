from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages=['streamlink'],
    excludes=[],
    includes=[],
    include_files=['ui/']
)

base = 'Win32GUI' if sys.platform == 'win32' else None


executables = [
    Executable('main.py', base=base, targetName='desktop_stream_viewer' + ('.exe' if sys.platform == 'win32' else ''))
]

setup(
    name='Desktop Stream Viewer',
    version='0.5',
    description='Watch multiple streams at the same time.',
    options=dict(build_exe=buildOptions),
    executables=executables
)
