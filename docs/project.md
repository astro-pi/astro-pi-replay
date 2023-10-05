# Using the project

This executor is designed to support the [Calculate the speed of the ISS](https://projects.raspberrypi.org/en/projects/astropi-iss-speed/0) project.

That project requires that `opencv-python` is installed.

## Install `opencv-python`

Install with:

    pip install --only-binary opencv-python

If this fails, then you probably have an old version of python or pip.
Depending on your OS and how you installed python, try and upgrade python.
If you installed Python manually from [https://www.python.org/downloads/](https://www.python.org/downloads/) you will have to repeat the process again to update python.
Otherwise, if you installed python using a package manager, then you can execute
a command on the command-line to update python. The table below shows the common package managers used in various operating systems,

| Operating System        | Package Manager       | Update Command                                |
|-------------------------|-----------------------|----------------------------------------------|
| Debian/Ubuntu           | apt                   | `sudo apt update && sudo apt upgrade python`  |
| Arch Linux              | pacman                | `sudo pacman -Syu python`                    |
| Fedora                  | dnf                   | `sudo dnf upgrade python`                    |
| Fedora (older)          | yum                   | `sudo yum update python`                     |
| CentOS/RHEL             | yum                   | `sudo yum update python`                     |
| openSUSE                | zypper                | `sudo zypper update python`                  |
| Gentoo                  | emerge                | `sudo emerge --sync && sudo emerge -auvDN @world` |
| FreeBSD                 | pkg                   | `sudo pkg update && sudo pkg upgrade python` |
| macOS                   | Homebrew (brew)       | `brew update && brew upgrade python`        |
| Windows                 | Chocolatey (choco)    | `choco upgrade python`                       |
| Windows (Miniconda)     | Miniconda/conda       | `conda update python`                        |
| Windows (Python.org)    | Python Installer      | Download and run the latest Python installer from [python.org](https://www.python.org/downloads/) |
| Windows (Scoop)         | Scoop                 | `scoop update python`                        |
| NixOS / Nixpkgs         | Nix                   | `nix-channel --update && nix-env -u python`  |


# Installing python

The best way to install Python for a beginner largely depends on the individual's operating system and their specific goals. Here are some common recommendations:

1. **Windows**:
   - For Windows users, the easiest way to install Python is by downloading the official Python installer from the [Python website](https://www.python.org/downloads/windows/). This installer includes Python and pip (Python package manager) out of the box, making it beginner-friendly.

2. **macOS**:
   - macOS often comes with a pre-installed version of Python. However, it's recommended to use Homebrew for installing and managing Python. You can install Homebrew first, and then use it to install Python:
     - Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
     - Install Python: `brew install python`

3. **Linux** (Ubuntu/Debian):
   - Many Linux distributions come with Python pre-installed. To ensure you have the latest version and access to pip, you can use `apt` (for Ubuntu/Debian):
     - `sudo apt update`
     - `sudo apt install python3`

4. **Linux** (Fedora):
   - For Fedora users, you can use `dnf` to install Python:
     - `sudo dnf install python3`

5. **Linux** (Arch Linux):
   - Arch Linux users can use `pacman` to install Python:
     - `sudo pacman -S python`

6. **Linux** (NixOS/Nixpkgs):
   - NixOS users can install Python using Nix:
     - `nix-env -i python`

7. **Linux** (Other Distributions):
   - For other Linux distributions, consult your distribution's documentation or package manager (e.g., `zypper` for openSUSE, `emerge` for Gentoo) to install Python.

8. **Alternative Methods (Advanced Users)**:
   - More advanced users or those with specific needs might consider tools like Anaconda or Miniconda, which provide Python environments for data science and scientific computing.

In general, for beginners, it's recommended to install the latest stable version of Python 3 (e.g., Python 3.9 or 3.10 at the time of my knowledge cutoff in September 2021) as Python 2 is no longer supported. The official Python installer or package manager commands mentioned above are usually the easiest and safest methods for beginners to get started with Python.


# Usage

On Linux or MacOS:

    Astro-Pi-Replay download
    Astro-Pi-Replay run main.py

On Windows:

    Astro-Pi-Replay.exe download
    Astro-Pi-Replay.exe run main.py
