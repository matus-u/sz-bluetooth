def formatNumber(value):
    if value < 10:
        return "0" + str(value)
    else:
        return str(value)

def isBluetooth(name):
    return name == "Bluetooth"

def formatDuration(duration, name=""):

    if isBluetooth(name):
        return "--:--"
    else:
        return formatNumber(int(int(duration)/60)) + ":" + formatNumber(int(duration)%60)

def formatNameWithStartTime(name, startTime=None):
    if startTime is not None:
        return formatSongName(name) + " - " + str(startTime.time().strftime("%H:%M"))
    return formatSongName(name)

def formatSongName(name):
    return name
