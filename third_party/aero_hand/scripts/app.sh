#!/bin/sh
# Press a button in the Helping Hands Mac app, so the app (not Terminal) owns camera, mic and USB.
#   app.sh perform [song]   app.sh routine   app.sh pose peace   app.sh count
#   app.sh teleop           app.sh rps       app.sh home         app.sh stop    app.sh fast on|off
# Same as opening helpinghands://aero/<command>[/<arg>].
[ $# -ge 1 ] || { sed -n '2,5p' "$0"; exit 2; }
cmd=$1; shift
url="helpinghands://aero/$cmd"
if [ $# -gt 0 ]; then
    arg=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(" ".join(sys.argv[1:]), safe=""))' "$@")
    url="$url/$arg"
fi
exec open -g "$url"
