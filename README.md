`licht` is a command-line program (including a GTK applet) which
fetches info from a local Philips Hue bridge in your network and
enables you to apply basic operations, such turning lights on/off,
dimming, color-temperature changing, etc.

I was looking for a lightweight program for Philips Hue, but
unfortunately most don't run (stable) on Arch linux, so I decided to
write it myself.


# Prerequisites

This program mainly uses following python3 modules

-   requests
-   pyyaml
-   pycairo
-   PyGObject

The PyGObject dependencies additionally require some packages to
be installed on your distribution. For a detailed overview see
[https://pygobject.readthedocs.io/en/latest/getting<sub>started.html</sub>](https://pygobject.readthedocs.io/en/latest/getting_started.html).

For Arch linux use:

    sudo pacman -S python cairo pkgconf gobject-introspection gtk3


# Install

    pip install licht

For installing from source, clone the repository, and run

    cd licht
    python setup.py install --user

or create a virtual environment with

    pipenv install
    pipenv install -e .

To activate the virtual environment run

    pipenv shell

or start every command with `pipenv run`.


# Usage

To start a daemon, run `licht --daemon`.

    usage: licht [-h] [-d] [-a] [--lights] [--groups] [--scenes] [-l <light-id>] [-g <group-id>] [-s <scene-id>]
    	     [-p <subpath>] [-o {true,false,1,0,yes,no,y,n}] [-b <bri-value>] [-t <color-temp-value>] [-u <json-string>]
    	     [--register] [-c <path>] [--section <section>] [--dark-icon] [--output <path>] [-v]
    
    options:
      -h, --help            show this help message and exit
      -d, --daemon          Run the Licht applet as a daemon process
      -a, --app, --applet   Run the Licht applet
      --lights, --list-lights
    			List the index of lights in the network
      --groups, --list-groups
    			List the index of groups in the network
      --scenes, --list-scenes
    			List the index of groups in the network
      -l <light-id>, --light <light-id>, --light-id <light-id>
    			Light-id for state change
      -g <group-id>, --group <group-id>, --group-id <group-id>
    			Group-id for state change
      -s <scene-id>, --scene <scene-id>, --scene-id <scene-id>
    			Scene-id for state change
      -p <subpath>, --subpath <subpath>
    			Subpath for state change
      -o {true,false,1,0,yes,no,y,n}, --on {true,false,1,0,yes,no,y,n}
    			Toggle lights on
      -b <bri-value>, --bri <bri-value>
    			Update for the brightness value [0-255]
      -t <color-temp-value>, --ct <color-temp-value>
    			Update for the color temperature value [0-65535]
      -u <json-string>, --update <json-string>
    			Update body for the PUT request
      --register            Authenticate licht and receive a username from bridge
      -c <path>, --config <path>
    			Path to the config file
      --section <section>   Section in the yaml file to be parsed
      --dark-icon           Use a dark icon on systray (for light themes)
      --output <path>       Set the path of the output log-file
      -v, --verbose         Run program in verbose mode


# Configuration

`licht` works with both command-line arguments as well as YAML
configuration files (the first takes precedence over the latter).  To
set your desired defaults, edit the configuration file
`licht_example.yml` and place it in either

-   `~/.config/licht/licht.yml`
-   `~/.config/.licht.yml`
-   `~/.licht/licht.yml`
-   `~/.licht.yml`

