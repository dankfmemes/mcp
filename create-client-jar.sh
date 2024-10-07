#!/bin/bash

# Define the source directory and output JAR file
SOURCE_DIR="bin/minecraft"
OUTPUT_JAR="recompiled/client.jar"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Source directory $SOURCE_DIR does not exist."
    exit 1
fi

# Create the JAR file from the compiled classes
jar cf "$OUTPUT_JAR" -C "$SOURCE_DIR" .

# Check if the JAR creation was successful
if [ $? -eq 0 ]; then
    echo "JAR file created successfully: $OUTPUT_JAR"
else
    echo "Failed to create JAR file."
    exit 1
fi
