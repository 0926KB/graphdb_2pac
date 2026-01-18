"""
Neo4j 그래프 데이터베이스와 LangChain 연동 예제

중요: 
1. Neo4j는 관계형 DB가 아닌 그래프 DB입니다
2. 라이브러리 설치만으로 자동 연결되지 않습니다
3. 연결 정보(URL, 사용자명, 비밀번호)를 명시적으로 제공해야 합니다
"""

from langchain_community.graphs import Neo4jGraph

# Neo4j 연결 설정
# Neo4j Desktop 또는 Neo4j Aura에서 연결 정보를 확인하세요
graph = Neo4jGraph(
    url="bolt://localhost:7687",  # Neo4j 서버 URL
    username="neo4j",              # 사용자명
    password="your_password"       # 비밀번호 (실제 비밀번호로 변경 필요)
)

# Cypher 쿼리 실행 예제
# 예: 노드 생성
create_query = """
CREATE (p1:Person {name: 'Alice', age: 30})
CREATE (p2:Person {name: 'Bob', age: 25})
CREATE (p1)-[:KNOWS]->(p2)
"""

# 쿼리 실행
result = graph.query(create_query)
print("노드 및 관계 생성 완료")

# 데이터 조회 예제
read_query = """
MATCH (p:Person)
RETURN p.name as name, p.age as age
"""
results = graph.query(read_query)
print("\n조회 결과:")
for record in results:
    print(f"이름: {record['name']}, 나이: {record['age']}")

