#!/bin/bash
echo "🚀 Deploying delta_graph using a direct bash execution thread..."
sudo docker run -d \
  --name delta_graph \
  -p 7474:7474 \
  -p 7687:7687 \
  -m 1g \
  -e NEO4J_AUTH=neo4j/r0ckNr0!! \
  -e NEO4J_PLUGINS='["apoc"]' \
  --restart always \
  neo4j:5.20-community
