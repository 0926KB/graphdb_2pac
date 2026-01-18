# -*- coding: utf-8 -*-
"""
Neo4j AuraDB Connection Test Script - Direct test
"""
import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("Neo4j AuraDB Connection Test")
print("=" * 60)

# 환경 변수 확인
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

print(f"\n[ENV] NEO4J_URI: {neo4j_uri}")
print(f"[ENV] NEO4J_USERNAME: {neo4j_user}")
print(f"[ENV] NEO4J_PASSWORD: {'*' * len(neo4j_pass) if neo4j_pass else 'NOT SET'}")

# 직접 연결 테스트
print(f"\n[TEST] Connecting to {neo4j_uri}...")

from neo4j import GraphDatabase

try:
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_user, neo4j_pass)
    )
    driver.verify_connectivity()
    
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        record = result.single()
        print(f"  [OK] Query test: {record['test']}")
    
    driver.close()
    print("\n[SUCCESS] Neo4j connection successful!")
    
except Exception as e:
    print(f"  [FAILED] {e}")
