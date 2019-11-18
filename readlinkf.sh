#!/bin/sh

# Below is an implementation of readlink -f
# Taken from https://stackoverflow.com/a/1116890/1709587, authored by
# Keith Smith, and CC-licensed.
# This is used in DeepSimulator to support readlink -f behaviour on macOS,
# since the default readlink implementation on macOS doesn't accept the -f
# flag.

TARGET_FILE=$1

cd `dirname $TARGET_FILE`
TARGET_FILE=`basename $TARGET_FILE`

# Iterate down a (possible) chain of symlinks
while [ -L "$TARGET_FILE" ]
do
    TARGET_FILE=`readlink $TARGET_FILE`
    cd `dirname $TARGET_FILE`
    TARGET_FILE=`basename $TARGET_FILE`
done

# Compute the canonicalized name by finding the physical path 
# for the directory we're in and appending the target file.
PHYS_DIR=`pwd -P`
RESULT=$PHYS_DIR/$TARGET_FILE
echo $RESULT
