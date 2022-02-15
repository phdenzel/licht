"""
licht.__main__

@author: phdenzel
"""
import licht
from licht.rest import LichtClient
from licht.app import LichtApplet


def main(verbose=False):
    bridge_ip = licht.bridge_ip
    licht_client = LichtClient(bridge_ip)
    licht_applet = LichtApplet(client=licht_client)
    licht_applet.run()


if __name__ == "__main__":
    main()
