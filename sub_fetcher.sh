#!/usr/bin/env bash

VERBOSE=false
PATH=$PATH:/usr/local/bin
SUBPATH=/mnt/media/subtitles

wdir="$(dirname $0)"
[ -f $wdir/processed.log ] || touch $wdir/processed.log
[ -f $wdir/subdivx.log ] || touch $wdir/subdivx.log

tail -10 $wdir/processed.log |
while read url; do
  if ! fgrep -q "$url" $wdir/subdivx.log; then
    # best effort subtitle download
    suburl=$($wdir/subdivx-fetcher.py "$(basename "$url")")
    if [ "$suburl" ]; then
      wget -P "$SUBPATH" -q --content-disposition "$suburl" &&
        echo "$url" >> $wdir/subdivx.log
    fi
  fi
done

pushd "$SUBPATH" &>/dev/null
for f in *rar; do
  [ -f "$f" ] &&
  unrar x "$f" &>/dev/null && rm -f "$f"
done
for f in *zip; do
  [ -f "$f" ] &&
  unzip "$f" &>/dev/null && rm -f "$f"
done

# vim: set sw=2 sts=2 : #
