#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 12:02:38 2026

@author: delta
"""

from neo4j import GraphDatabase
import os

class Neo4jManager:
    def __init__(self):
        # Update with your local credentials
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Global instance for easy import
db = Neo4jManager()
