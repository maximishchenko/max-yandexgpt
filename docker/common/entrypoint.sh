#!/bin/sh
# Docker secrets support.
#
# For every environment variable named <NAME>_FILE that holds a path to a file,
# export <NAME> with the content of that file, then run the given command.
#
#   MAX_TOKEN_FILE=/run/secrets/max_api_token  ->  MAX_TOKEN=<file content>
set -eu

for file_var in $(env | sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*_FILE\)=.*/\1/p'); do
    var="${file_var%_FILE}"
    [ -n "$var" ] || continue

    path="$(printenv "$file_var")"
    [ -n "$path" ] || continue

    if printenv "$var" > /dev/null; then
        echo "entrypoint: both $var and $file_var are set" >&2
        exit 1
    fi

    if [ ! -r "$path" ]; then
        echo "entrypoint: $file_var points to an unreadable file: $path" >&2
        exit 1
    fi

    export "$var=$(cat "$path")"
done

exec "$@"
