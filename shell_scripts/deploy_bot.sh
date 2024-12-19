#!/bin/sh

NEW_REV=$1
TEMP_DIR=$(mktemp -d)
SYSTEM_USER_NAME=$(whoami)
REPO_NAME=$(basename "$PWD")
BOT_NAME=${REPO_NAME%.git}

# Check if BOTMAN_URL is set
if [ -z "$BOTMAN_URL" ]; then
    echo "Error: BOTMAN_URL is not set" >&2
    exit 1
fi

git --work-tree="$TEMP_DIR" --git-dir="$(pwd)" checkout "$NEW_REV" -- . 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to checkout files" >&2
    exit 1
fi
cd "$TEMP_DIR" || exit 1
# Create a tarball of the repo files
tar -czf "$TEMP_DIR/src.tar.gz" * 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to create tarball" >&2
    exit 1
fi
# send repo files via webhook
status_http_code=$(curl -s -o /tmp/curl_output -w "%{http_code}" -X POST "$BOTMAN_URL/build/$SYSTEM_USER_NAME/$BOT_NAME" \
    -F file=@"$TEMP_DIR/src.tar.gz")
if [ "$status_http_code" -ne 200 ]; then
    echo "Docker build failed. Reverting changes..." >&2
    exit 1
fi
container_id=$(cat /tmp/curl_output)

# Clean up
rm -rf "$TEMP_DIR"
echo "$container_id"
exit 0
