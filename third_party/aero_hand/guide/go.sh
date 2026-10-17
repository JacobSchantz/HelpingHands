#!/bin/bash
# go.sh next|last|<n> : show a guide page in the Pebbles Browser
D=$(dirname "$0"); c=$(cat "$D/current"); n=50
case "$1" in next) p=$((c+1));; last|back|prev) p=$((c-1));; *) p=$1;; esac
[ $p -lt 1 ] && p=1; [ $p -gt $n ] && p=$n; echo $p > "$D/current"
:
echo "page $p"
