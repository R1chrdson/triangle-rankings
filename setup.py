import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': ['PyQt5', 'pandas'],
    'excludes': ['scipy', 'matplotlib', 'tkinter'],
    'include_files': ['ui/', 'ui/'],
    'include_msvcr': True
}

bas = None
if sys.platform == 'win32':
    base = 'Win32GUI'

targetName = 'Rankings Generator'
setup(options={'build_exe': build_exe_options},
      executables=[Executable(script='main.py',
                              base=base,
                              targetName=targetName)])
