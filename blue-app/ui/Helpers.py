def formatNumber(value):
    if value < 10:
        return "0" + str(value)
    else:
        return str(value)

def formatDuration(duration):
    return formatNumber(int(int(duration)/60)) + ":" + formatNumber(int(duration)%60)

