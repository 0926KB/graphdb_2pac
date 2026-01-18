# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

print("=" * 60)
print("Database Status Check")
print("=" * 60)

# 노드 수 확인
nodes = graph.query('MATCH (n) RETURN count(n) as count')
print(f"\nTotal nodes: {nodes[0]['count']}")

# 관계 수 확인
rels = graph.query('MATCH ()-[r]->() RETURN count(r) as count')
print(f"Total relationships: {rels[0]['count']}")

# 주요 노드 확인
print("\n[NODES] Key nodes:")
key_nodes = graph.query('MATCH (n) WHERE n.id IS NOT NULL RETURN n.id as id, labels(n)[0] as label LIMIT 15')
for n in key_nodes:
    print(f"  - {n['label']}: {n['id']}")

# 투팍 관련 관계 확인
print("\n[RELATIONS] Relationships pointing to Tupac:")
tupac_rels = graph.query('''
    MATCH (a)-[r]->(t)
    WHERE t.id CONTAINS "Tupac" OR t.id CONTAINS "tupac"
    RETURN a.id as from_node, type(r) as rel, t.id as to_node
    LIMIT 15
''')
if tupac_rels:
    for r in tupac_rels:
        print(f"  {r['from_node']} -[:{r['rel']}]-> {r['to_node']}")
else:
    print("  (No relationships found)")

# Puff Daddy 관련 확인
print("\n[RELATIONS] Puff Daddy's relationships:")
puffy_rels = graph.query('''
    MATCH (p)-[r]->(t)
    WHERE p.id CONTAINS "Puff" OR p.id CONTAINS "Diddy"
    RETURN p.id as from_node, type(r) as rel, t.id as to_node
    LIMIT 10
''')
if puffy_rels:
    for r in puffy_rels:
        print(f"  {r['from_node']} -[:{r['rel']}]-> {r['to_node']}")
else:
    print("  (No relationships found)")

print("\n" + "=" * 60)

