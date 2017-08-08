"""
Enables to launch Python programs with command lines and reusable launcher scheme classes.
This module allows you to forget many of the platform-specific details. 
Automatically inserts "Python" and/or path to Python executable at front of command line.
Some of this module may assume 'python' is on your system path.
Runs program file names through 'normpath()' to change Windows special characters.
You can just import this module and use 'PortableLauncher' to call it as method.
IMPORTANT: this module is only skeleton to build your own cross-platform launch solution.
"""

import os, sys
from abc import ABCMeta, abstractmethod

# Platform specific name of interpreter.
pyfile = (sys.platform[:3] == 'win' and 'python.exe') or 'python'
# Path to Python interpreter.
pypath = sys.executable


def fixWindowsPath(cmdline):
    """
	Converts windows special characters such as slashes to windows specific format if needed.
	:param cmdline: Command to execute.
	:return: Normalized input for Windows system.
	"""
    splitLine = cmdline.lstrip().split(' ')
    fixedPath = os.path.normpath(splitLine[0])
    return ''.join([fixedPath] + splitLine[1:])


class LaunchMode(metaclass=ABCMeta):
    """
	On call to instance, announce label and run command.
	Subclasses specialize behavior.
	"""

    def __init__(self, label, command):
        """
		Initializes label to announce and command to execute.
		:param label: Label is just for informative usage.
		:param command: Command to execute. Command should begin with name of Python script. 
		"""
        self.what = label
        self.where = command

    def __call__(self):
        self.announce(self.what)
        self.run(self.where)

    def announce(self, text):
        print(text)

    @abstractmethod
    def run(self, cmdline):
        pass


class System(LaunchMode):
    """
	System default way to start a script in shell command line.
	May block caller, unless '&' added on Unix.
	"""

    def run(self, cmdline):
        cmdline = fixWindowsPath(cmdline)
        os.system('{} {}'.format(pypath, cmdline))


class Popen(LaunchMode):
    """
	Run shell command line in a new process.
	May block caller, since pipe closed to soon.
	"""

    def run(self, cmdline):
        cmdline = fixWindowsPath(cmdline)
        os.popen(pypath + ' ' + cmdline)


class Fork(LaunchMode):
    """
	Run command in explicitly created new process.
	For Unix-like systems only, including cygwin.
	"""

    def run(self, cmdline):
        assert hasattr(os, 'fork')
        cmdline = cmdline.split()
        if os.fork() == 0:
            os.execvp(pypath, [pyfile] + cmdline)


class Start(LaunchMode):
    """
	Run command independent of caller.
	For Windows system only.
	IMPORTANT: uses filename associations.
	"""

    def run(self, cmdline):
        assert sys.platform[:3] == 'win'
        cmdline = fixWindowsPath(cmdline)
        os.startfile(cmdline)


class StartArgs(LaunchMode):
    """
	For Windows system only.
	Args may require real start.
	Forward slashes are okay here.
	"""

    def run(self, cmdline):
        assert sys.platform[:3] == 'win'
        os.system('start ' + cmdline)


class Spawn(LaunchMode):
    """
	Run Python in new process independent of caller.
	For Windows or Unix systems.
	Use P_NOWAIT for dos box.
	Forward slashes are okay here.
	"""

    def run(self, cmdline):
        os.spawnv(os.P_DETACH, pypath, (pyfile, cmdline))


class TopLevel(LaunchMode):
    """
	Space for another platform-specific development.
	"""

    def run(self, cmdline):
        assert False, 'Mode not yet implemented.'


# Platform-specific logic.
# Picks a "best" launcher for this platform.
# May need to specialize the choice elsewhere.
# Portable launcher will contain correct Class according to platform.
if sys.platform[:3] == 'win':
    PortableLauncher = Spawn
else:
    PortableLauncher = Fork


class QuietPortableLauncher(PortableLauncher):
    def announce(self, text):
        pass


def selfTest():
    """
	Function to self testing of functionality of this module. 
	"""
    fileName = sys.argv[1]

    print('default mode...')
    PortableLauncher(fileName, fileName)()

    print('system mode...')
    System(fileName, fileName)()

    if sys.platform[:3] == 'win':
        print('win mode...')
        StartArgs(fileName, fileName)()


if __name__ == '__main__':
    selfTest()
