#!/bin/sh
set -e # Exit early if any commands fail
exec python -m app.main "$@"
