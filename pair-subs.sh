#!/usr/bin/env bash

THRES=20000

MOVIE_DIRS=(
  /mnt/media/torrents
)

SUBS_DIRS=(
  /mnt/media/tmp.*
)


# takes a movie file name and returns best possible subtittle with score
function pair_file {
  local movie="$1"
  local subs="$2"

  local mdir="$(basename "$(dirname "$movie")")"
  local mfile="$(basename "$movie")"

  local dist1="$(tre-agrep -isB "$mdir/$mfile" "$subs")"
  local dist2="$(tre-agrep -isB "$mfile" "$subs")"

  if [ ${dist1%%:*} -lt ${dist2%%:*} ]; then
    [ ${dist1%%:*} -lt $THRES ] && echo $dist1
  else
    [ ${dist2%%:*} -lt $THRES ] && echo $dist2
  fi
}

function pair_all {
  local subs="$(mktemp)"
  local subfiles="$(mktemp)"

  [ -z "${SUBS_DIRS[@]}" ] && return 1

  find ${SUBS_DIRS[@]} -iname '*.srt' \
    > "$subfiles"
  cat "$subfiles" |
    xargs -r -L 1 -d '\n' basename \
    > "$subs"

  if [ "$(cat "$subfiles" | wc -l)" -gt 0 ]; then
    find ${MOVIE_DIRS[@]} -iname '*.avi' -o -iname '*.mkv' |
    while read mfile; do
      subfile="$(pair_file "$mfile" "$subs")"
      if [ "$subfile" ]; then
        subfile="$(grep "${subfile#*:}" "$subfiles")"
        echo "
mv '$subfile' \\
   '$(echo $mfile | sed 's/\.avi$\|\.mkv$//').srt'"
      fi
    done
  fi

  rm -f "$subs" "$subfiles"
}

scriptfile="$(mktemp)"
pair_all > "$scriptfile" || exit 1
if [ "$(cat "$scriptfile" | wc -l)" -gt 0 ]; then
  vim "$scriptfile"
  echo -n "Apply pairing ? "; read applyreq
  [ $applyreq = yes ] && bash "$scriptfile"
fi
rm -f "$scriptfile"
