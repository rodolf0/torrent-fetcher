#!/usr/bin/env bash

VERBOSE=false
PATH=$PATH:/usr/local/bin
SUBPATH=/mnt/media/torrents

wdir="$(dirname $0)"
[ -f $wdir/processed.log ] || touch $wdir/processed.log

$wdir/torrent-fetcher.py |
while read torrent; do
  name=$(echo $torrent | reorder -d ^ -f 1)
  url=$(echo $torrent | reorder -d ^ -f 2)
  if ! fgrep -q "$url" $wdir/processed.log; then
    transmission-remote --add "$url" >/dev/null &&
    echo "$url" >> $wdir/processed.log &&
    echo $name # info for cron to mail
  else
    $VERBOSE && echo "Ignoring: $torrent"
  fi
done
