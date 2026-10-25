#!/usr/bin/env bash
# Nur den zufällig markierten Container dieses Jobs entfernen. Kein Prune.
set -euo pipefail
trap '' INT TERM
name="${SQLPERF_SQL_CONTAINER:-}"
owner="${SQLPERF_CI_OWNER:-}"
if [ -z "$name" ] && [ -z "$owner" ]; then
  echo 'CI_CONTAINER_CLEANUP|NOT_CREATED'
  exit 0
fi
[[ "$name" =~ ^sqlperf-[a-zA-Z0-9_-]+$ ]] || exit 1
[[ "$owner" =~ ^[0-9a-f]{32}$ ]] || exit 1
cid="$(docker container ls --all --quiet --no-trunc --filter "name=^/${name}$")"
if [ -z "$cid" ]; then
  # Auch ein verlorener Name darf keinen eigenen Container verdecken.
  remaining="$(docker container ls --all --quiet --filter "label=sqlperf.ci.owner=${owner}")"
  test -z "$remaining"
  echo 'CI_CONTAINER_CLEANUP|PASS|ABSENT'
  exit 0
fi
[[ "$cid" =~ ^[0-9a-f]{64}$ ]] || exit 1
identity="$(docker inspect --format '{{.Id}}|{{.Name}}|{{index .Config.Labels "sqlperf.ci.owner"}}' "$cid")"
test "$identity" = "${cid}|/${name}|${owner}"
owned="$(docker container ls --all --quiet --no-trunc --filter "label=sqlperf.ci.owner=${owner}")"
test "$owned" = "$cid"
docker rm --force --volumes "$cid" >/dev/null
for filter in "id=${cid}" "name=^/${name}$" "label=sqlperf.ci.owner=${owner}"; do
  remaining="$(docker container ls --all --quiet --filter "$filter")"
  test -z "$remaining"
done
echo 'CI_CONTAINER_CLEANUP|PASS|ABSENT'
