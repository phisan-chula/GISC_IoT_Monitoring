#!/bin/bash
# clear_cache.sh

CACHE_DIR="./CACHE"

# Check if CACHE exists
if [ ! -d "$CACHE_DIR" ]; then
    echo "Directory $CACHE_DIR does not exist."
    exit 1
fi

echo "The following files and directories will be removed from $CACHE_DIR:"
find "$CACHE_DIR" -mindepth 1

read -p "Are you sure you want to delete ALL contents of $CACHE_DIR? (yes/no) " confirm
if [ "$confirm" == "yes" ]; then
    rm -rf "$CACHE_DIR"/*
    rm -rf "$CACHE_DIR"/.[!.]*
    echo "All contents inside $CACHE_DIR have been deleted."
else
    echo "Aborted."
fi

