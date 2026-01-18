# -*- coding: utf-8 -*-
"""
누락된 증거 보강 스크립트
탐정이 무시할 수 없는 강력한 증거 주입
"""
import os
import sys
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

print("=" * 60)
print("Evidence Injection Script")
print("=" * 60)

# 1단계: 노드 확실히 생성
print("\n[STEP 1] Ensuring all key players exist...")
graph.query("""
MERGE (puffy:Producer {id: "Puff Daddy"})
SET puffy.aka = "P. Diddy"
MERGE (tupac:Rapper {id: "Tupac Shakur"})
MERGE (keffe:Person {id: "Keffe D"})
SET keffe.aka = "Duane Keith Davis"
MERGE (orlando:Person {id: "Orlando Anderson"})
""")
print("  -> Nodes ready")

# 2단계: 청부 체인 (Puff Daddy -> Keffe D -> Orlando -> Tupac)
print("\n[STEP 2] Creating hit chain (Puff Daddy -> Keffe D -> Orlando -> Tupac)...")
graph.query("""
MATCH (puffy:Producer {id: "Puff Daddy"}), (keffe:Person {id: "Keffe D"})
MERGE (puffy)-[:HIRED_HITMAN {amount: "1 Million USD", purpose: "Kill Tupac and Suge"}]->(keffe)
""")
print("  -> Puff Daddy -[:HIRED_HITMAN]-> Keffe D")

graph.query("""
MATCH (keffe:Person {id: "Keffe D"}), (orlando:Person {id: "Orlando Anderson"})
MERGE (keffe)-[:ORDERED_HIT {target: "Tupac Shakur"}]->(orlando)
MERGE (keffe)-[:GAVE_WEAPON {type: "Glock 22"}]->(orlando)
""")
print("  -> Keffe D -[:ORDERED_HIT]-> Orlando")

graph.query("""
MATCH (orlando:Person {id: "Orlando Anderson"}), (tupac:Rapper {id: "Tupac Shakur"})
MERGE (orlando)-[:SHOT_AT {date: "1996-09-07", location: "Las Vegas"}]->(tupac)
MERGE (orlando)-[:SUSPECTED_KILLER_OF]->(tupac)
""")
print("  -> Orlando -[:SHOT_AT]-> Tupac")

# 3단계: 직접적인 배후 관계 (Puff Daddy -> Tupac)
print("\n[STEP 3] Creating direct mastermind links...")
graph.query("""
MATCH (puffy:Producer {id: "Puff Daddy"}), (tupac:Rapper {id: "Tupac Shakur"})
MERGE (puffy)-[:BEEF_WITH {reason: "East vs West Coast War"}]->(tupac)
MERGE (puffy)-[:ALLEGEDLY_ORCHESTRATED_MURDER_OF]->(tupac)
""")
print("  -> Puff Daddy -[:ALLEGEDLY_ORCHESTRATED_MURDER_OF]-> Tupac")

# 4단계: 키피 D -> 투팍 연결 (Multi-hop 완성)
print("\n[STEP 4] Completing multi-hop chain...")
graph.query("""
MATCH (keffe:Person {id: "Keffe D"}), (tupac:Rapper {id: "Tupac Shakur"})
MERGE (keffe)-[:ORCHESTRATED_MURDER_OF {role: "Middleman"}]->(tupac)
""")
print("  -> Keffe D -[:ORCHESTRATED_MURDER_OF]-> Tupac")

# 검증
print("\n" + "=" * 60)
print("[CHECK] Verifying new relationships:")
print("=" * 60)

check1 = graph.query("""
    MATCH (p {id: "Puff Daddy"})-[r]->(t {id: "Tupac Shakur"})
    RETURN type(r) as relation
""")
print("\n  Puff Daddy -> Tupac:")
for rec in check1:
    print(f"    - {rec['relation']}")

check2 = graph.query("""
    MATCH path = (p {id: "Puff Daddy"})-[*1..3]->(t {id: "Tupac Shakur"})
    WITH nodes(path) as n, relationships(path) as r
    RETURN [x in n | x.id] as nodes, [x in r | type(x)] as rels
    LIMIT 5
""")
print("\n  Multi-hop paths (Puff Daddy -> ... -> Tupac):")
for rec in check2:
    nodes = rec['nodes']
    rels = rec['rels']
    path_str = ""
    for i, node in enumerate(nodes):
        path_str += str(node)
        if i < len(rels):
            path_str += f" -[:{rels[i]}]-> "
    print(f"    - {path_str}")

print("\n" + "=" * 60)
print("[DONE] Now the detective can find the truth!")
print("=" * 60)
