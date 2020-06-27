import os

def AppBasePath():
    if os.getenv('RUN_FROM_DOCKER', False) == False:
        return "/media/usbstick/blue-app/"
    else:
        return "/src/blue-app/"
