#!/bin/bash

# Specify the repository URL
repo_url="https://github.com/NetManAIOps/OmniAnomaly"

# Get the repository name from the URL
repo_name=$(basename $repo_url .git)

# Clone the repository
git clone $repo_url

# Specify the path to the SMD dataset in the repository
smd_dataset_path="$repo_name/ServerMachineDataset"

# Copy the SMD dataset to the current directory
mkdir -p ../../data/
cp -r $smd_dataset_path ../../data/

# Remove the cloned repository
rm -rf $repo_name
