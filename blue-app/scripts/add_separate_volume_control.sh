#!/bin/bash
cat > ~/.asoundrc << EOL
pcm.softvolsound {
    type            softvol
    slave.pcm       "default"
    control.name    "SoftSoundMaster"
    control.card    0
}

pcm.softvolbluetooth {
    type            softvol
    slave.pcm       "default"
    control.name    "SoftBlueMaster"
    control.card    0
}
EOL

cp ~/.asoundrc /root/.asoundrc

speaker-test -Dsoftvolsound -c 1 -l1 -twav
speaker-test -Dsoftvolbluetooth -c 1 -l1 -twav

amixer set 'SoftSoundMaster' 100%
amixer set 'SoftBlueMaster' 100%

