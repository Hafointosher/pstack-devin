#!/bin/sh
# Optional POSIX wrapper; canonical entry is log.mjs via Node.
exec node "$(dirname "$0")/log.mjs" "$@"
