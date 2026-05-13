#!/bin/bash

# Prompt for the Git description of work done today
read -p "Enter a description of the work done today: " description

# Check if the description is empty
if [ -z "$description" ]; then
  echo "Please enter a description of the work done today."
  exit 1
fi

# Stop and backup the Neo4j instance (neo4j-wu)
echo "Stopping and backing up neo4j-wu..."
if ! docker stop neo4j-wu; then
  echo "Error stopping neo4j-wu."
  exit 1
fi
if ! docker exec -it neo4j-wu neo4j-admin backup --database-graph db --to /path/to/backup/folder; then
  echo "Error backing up neo4j-wu."
  exit 1
fi

# Cleanly shut down all running processes
echo "Shutting down all running processes..."
if ! pkill -u $USER; then
  echo "Error shutting down running processes."
  exit 1
fi

# Add, commit, and push changes to GitHub
echo "Adding, committing, and pushing changes to GitHub..."
if ! git add .; then
  echo "Error adding changes to Git."
  exit 1
fi
if ! git commit -m "$description"; then
  echo "Error committing changes to Git."
  exit 1
fi
if ! git push origin master; then
  echo "Error pushing changes to GitHub."
  exit 1
fi

# Print a success message
echo "Backup and Git update complete!"
