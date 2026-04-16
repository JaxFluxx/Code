#!/bin/zsh
set -euo pipefail

duration_seconds="${1:-120}"
interval_seconds="${2:-5}"

if (( duration_seconds <= 0 || interval_seconds <= 0 )); then
  echo "用法: $0 [总时长秒数] [采样间隔秒数]" >&2
  exit 1
fi

samples=$(( duration_seconds / interval_seconds ))
if (( samples < 1 )); then
  samples=1
fi

echo "Apple GPU 监控"
echo "总时长: ${duration_seconds}s"
echo "采样间隔: ${interval_seconds}s"
echo
printf "%-19s %-8s %-10s %-10s %-8s %-8s\n" "timestamp" "device%" "renderer%" "tiler%" "busy" "queue"

for ((i = 1; i <= samples; i++)); do
  ts="$(date '+%F %T')"
  raw="$(ioreg -r -d 1 -w 0 -c IOAccelerator 2>/dev/null)"

  device="$(printf '%s\n' "$raw" | sed -n 's/.*"Device Utilization %"=\([0-9]\+\).*/\1/p' | head -n1)"
  renderer="$(printf '%s\n' "$raw" | sed -n 's/.*"Renderer Utilization %"=\([0-9]\+\).*/\1/p' | head -n1)"
  tiler="$(printf '%s\n' "$raw" | sed -n 's/.*"Tiler Utilization %"=\([0-9]\+\).*/\1/p' | head -n1)"
  busy="$(printf '%s\n' "$raw" | sed -n 's/.*"fBusyCount"=\([0-9]\+\).*/\1/p' | head -n1)"
  queue="$(printf '%s\n' "$raw" | sed -n 's/.*"state"="\([^"]*\)".*/\1/p' | head -n1)"

  device="${device:-NA}"
  renderer="${renderer:-NA}"
  tiler="${tiler:-NA}"
  busy="${busy:-NA}"
  queue="${queue:-NA}"

  printf "%-19s %-8s %-10s %-10s %-8s %-8s\n" "$ts" "$device" "$renderer" "$tiler" "$busy" "$queue"

  if (( i < samples )); then
    sleep "$interval_seconds"
  fi
done
