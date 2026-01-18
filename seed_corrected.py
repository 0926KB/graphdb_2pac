# -*- coding: utf-8 -*-
"""
Hip-Hop Noir - 수정된 데이터 모델로 그래프 재구축
팩트 체크 및 논리적 관계 교정 완료
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

def run_query(query, description=""):
    """개별 쿼리 실행 헬퍼"""
    try:
        graph.query(query)
        if description:
            print(f"  -> {description}")
    except Exception as e:
        print(f"  [ERROR] {description}: {e}")

def seed_corrected_data():
    print("=" * 60)
    print("Hip-Hop Noir - Corrected Data Model")
    print("=" * 60)
    
    # 1. 기존 데이터 삭제
    print("\n[CLEAN] Deleting all existing data...")
    graph.query("MATCH (n) DETACH DELETE n")
    print("  -> Done")
    
    # 2. 노드 생성
    print("\n[CREATE] Creating nodes...")
    
    # 인물 노드
    run_query('MERGE (n:Rapper {id: "Tupac Shakur", status: "Deceased", death_date: "1996-09-13"})', "Tupac")
    run_query('MERGE (n:Producer {id: "Suge Knight", status: "Alive"})', "Suge Knight")
    run_query('MERGE (n:Person {id: "Orlando Anderson", status: "Deceased", death_date: "1998-05-29"})', "Orlando Anderson")
    run_query('MERGE (n:Person {id: "Keffe D", aka: "Duane Keith Davis", status: "Arrested", arrest_date: "2024"})', "Keffe D")
    run_query('MERGE (n:Producer {id: "Puff Daddy", aka: "P. Diddy", status: "Alive"})', "Puff Daddy")
    run_query('MERGE (n:Rapper {id: "Notorious B.I.G.", aka: "Biggie Smalls", status: "Deceased", death_date: "1997-03-09"})', "Biggie")
    
    # 조직 노드
    run_query('MERGE (n:Label {id: "Death Row Records", location: "Los Angeles"})', "Death Row")
    run_query('MERGE (n:Label {id: "Bad Boy Records", location: "New York"})', "Bad Boy")
    run_query('MERGE (n:Gang {id: "Southside Crips", territory: "Compton"})', "Crips")
    run_query('MERGE (n:Gang {id: "Mob Piru Bloods", territory: "Compton"})', "Bloods")
    
    # 장소 노드
    run_query('MERGE (n:Location {id: "MGM Grand Hotel", city: "Las Vegas"})', "MGM")
    run_query('MERGE (n:Location {id: "Lakewood Mall", city: "Los Angeles"})', "Lakewood Mall")
    run_query('MERGE (n:Location {id: "Las Vegas"})', "Las Vegas")
    
    # 도구 노드
    run_query('MERGE (n:Vehicle {id: "White Cadillac"})', "White Cadillac")
    run_query('MERGE (n:Weapon {id: "Glock 22", caliber: ".40 S&W"})', "Glock 22")
    
    # 사건 노드
    run_query('MERGE (n:Event {id: "Mike Tyson Fight", date: "1996-09-07"})', "Tyson Fight")
    run_query('MERGE (n:Event {id: "Tupac Shooting", date: "1996-09-07", location: "Las Vegas"})', "Tupac Shooting")
    run_query('MERGE (n:Event {id: "MGM Lobby Assault", date: "1996-09-07"})', "MGM Assault")
    run_query('MERGE (n:Event {id: "Quad Studios Shooting", date: "1994-11-30", location: "New York"})', "Quad Shooting")
    run_query('MERGE (n:Event {id: "Biggie Murder", date: "1997-03-09", location: "Los Angeles", status: "Unsolved"})', "Biggie Murder")
    
    # 3. 관계 생성
    print("\n[CREATE] Creating relationships...")
    
    # 소속 관계
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Label {id: "Death Row Records"})
        MERGE (a)-[:SIGNED_TO {year: 1995}]->(b)
    ''', "Tupac -> Death Row")
    
    run_query('''
        MATCH (a:Producer {id: "Suge Knight"}), (b:Label {id: "Death Row Records"})
        MERGE (a)-[:FOUNDED {year: 1991}]->(b)
    ''', "Suge -> Death Row")
    
    run_query('''
        MATCH (a:Rapper {id: "Notorious B.I.G."}), (b:Label {id: "Bad Boy Records"})
        MERGE (a)-[:SIGNED_TO {year: 1993}]->(b)
    ''', "Biggie -> Bad Boy")
    
    run_query('''
        MATCH (a:Producer {id: "Puff Daddy"}), (b:Label {id: "Bad Boy Records"})
        MERGE (a)-[:FOUNDED {year: 1993}]->(b)
    ''', "Puff Daddy -> Bad Boy")
    
    # 갱단 소속
    run_query('''
        MATCH (a:Person {id: "Orlando Anderson"}), (b:Gang {id: "Southside Crips"})
        MERGE (a)-[:MEMBER_OF]->(b)
    ''', "Orlando -> Crips")
    
    run_query('''
        MATCH (a:Person {id: "Keffe D"}), (b:Gang {id: "Southside Crips"})
        MERGE (a)-[:MEMBER_OF]->(b)
    ''', "Keffe D -> Crips")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Gang {id: "Mob Piru Bloods"})
        MERGE (a)-[:AFFILIATED_WITH]->(b)
    ''', "Tupac -> Bloods")
    
    run_query('''
        MATCH (a:Label {id: "Death Row Records"}), (b:Gang {id: "Mob Piru Bloods"})
        MERGE (a)-[:AFFILIATED_WITH]->(b)
    ''', "Death Row -> Bloods")
    
    # 가족 관계
    run_query('''
        MATCH (a:Person {id: "Keffe D"}), (b:Person {id: "Orlando Anderson"})
        MERGE (a)-[:UNCLE_OF]->(b)
    ''', "Keffe D uncle of Orlando")
    
    # 갱단 간 대립
    run_query('''
        MATCH (a:Gang {id: "Southside Crips"}), (b:Gang {id: "Mob Piru Bloods"})
        MERGE (a)-[:RIVAL_OF]->(b)
    ''', "Crips vs Bloods")
    
    # 레이블 간 경쟁
    run_query('''
        MATCH (a:Label {id: "Death Row Records"}), (b:Label {id: "Bad Boy Records"})
        MERGE (a)-[:RIVALRY_WITH]->(b)
    ''', "Death Row vs Bad Boy")
    
    # 사건의 발단: 쇼핑몰 싸움
    run_query('''
        MATCH (a:Person {id: "Orlando Anderson"}), (b:Label {id: "Death Row Records"})
        MERGE (a)-[:FOUGHT_WITH {location: "Lakewood Mall", reason: "Chain robbery"}]->(b)
    ''', "Orlando fought Death Row crew")
    
    # 사건 당일: 타이슨 경기 관람
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Event {id: "Mike Tyson Fight"})
        MERGE (a)-[:ATTENDED]->(b)
    ''', "Tupac attended fight")
    
    run_query('''
        MATCH (a:Producer {id: "Suge Knight"}), (b:Event {id: "Mike Tyson Fight"})
        MERGE (a)-[:ATTENDED]->(b)
    ''', "Suge attended fight")
    
    # MGM 로비 폭행 (투팍 -> 올랜도)
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Person {id: "Orlando Anderson"})
        MERGE (a)-[:ATTACKED {reason: "Revenge for Lakewood Mall incident", location: "MGM Grand Hotel"}]->(b)
    ''', "Tupac attacked Orlando")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Event {id: "MGM Lobby Assault"})
        MERGE (a)-[:PARTICIPATED_IN]->(b)
    ''', "Tupac in MGM assault")
    
    run_query('''
        MATCH (a:Person {id: "Orlando Anderson"}), (b:Event {id: "MGM Lobby Assault"})
        MERGE (a)-[:VICTIM_OF]->(b)
    ''', "Orlando victim of assault")
    
    # 암살 의뢰 (퍼프 대디 -> 키피 D) - 핵심!
    run_query('''
        MATCH (a:Producer {id: "Puff Daddy"}), (b:Person {id: "Keffe D"})
        MERGE (a)-[:OFFERED_BOUNTY {amount: "1 Million USD", target: "Tupac and Suge"}]->(b)
    ''', "Puff Daddy offered bounty")
    
    run_query('''
        MATCH (a:Producer {id: "Puff Daddy"}), (b:Rapper {id: "Tupac Shakur"})
        MERGE (a)-[:ORDERED_HIT_ON]->(b)
    ''', "Puff Daddy ordered hit on Tupac")
    
    run_query('''
        MATCH (a:Producer {id: "Puff Daddy"}), (b:Producer {id: "Suge Knight"})
        MERGE (a)-[:ORDERED_HIT_ON]->(b)
    ''', "Puff Daddy ordered hit on Suge")
    
    # 총격 사건 실행
    run_query('''
        MATCH (a:Person {id: "Keffe D"}), (b:Vehicle {id: "White Cadillac"})
        MERGE (a)-[:RODE_IN]->(b)
    ''', "Keffe D in Cadillac")
    
    run_query('''
        MATCH (a:Person {id: "Orlando Anderson"}), (b:Vehicle {id: "White Cadillac"})
        MERGE (a)-[:RODE_IN]->(b)
    ''', "Orlando in Cadillac")
    
    run_query('''
        MATCH (a:Vehicle {id: "White Cadillac"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:USED_IN]->(b)
    ''', "Cadillac used in shooting")
    
    run_query('''
        MATCH (a:Weapon {id: "Glock 22"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:USED_IN]->(b)
    ''', "Glock used in shooting")
    
    run_query('''
        MATCH (a:Person {id: "Orlando Anderson"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:SUSPECTED_SHOOTER]->(b)
    ''', "Orlando suspected shooter")
    
    # 투팍 총격 결과
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:VICTIM_OF]->(b)
    ''', "Tupac victim")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:DIED_FROM]->(b)
    ''', "Tupac died")
    
    run_query('''
        MATCH (a:Producer {id: "Suge Knight"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:INJURED_IN {injury: "Head fragment"}]->(b)
    ''', "Suge injured")
    
    run_query('''
        MATCH (a:Producer {id: "Suge Knight"}), (b:Event {id: "Tupac Shooting"})
        MERGE (a)-[:SURVIVED]->(b)
    ''', "Suge survived")
    
    # 투팍 vs 비기 비프
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Rapper {id: "Notorious B.I.G."})
        MERGE (a)-[:FORMER_FRIEND_OF]->(b)
    ''', "Tupac former friend of Biggie")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Rapper {id: "Notorious B.I.G."})
        MERGE (a)-[:BEEF_WITH {reason: "Hit Em Up diss track", year: 1996}]->(b)
    ''', "Tupac beef with Biggie")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Rapper {id: "Notorious B.I.G."})
        MERGE (a)-[:SUSPECTED {reason: "Believed Biggie knew about 1994 shooting"}]->(b)
    ''', "Tupac suspected Biggie")
    
    run_query('''
        MATCH (a:Rapper {id: "Tupac Shakur"}), (b:Event {id: "Quad Studios Shooting"})
        MERGE (a)-[:VICTIM_OF]->(b)
    ''', "Tupac victim of Quad shooting")
    
    # 비기 사망
    run_query('''
        MATCH (a:Rapper {id: "Notorious B.I.G."}), (b:Event {id: "Biggie Murder"})
        MERGE (a)-[:DIED_FROM]->(b)
    ''', "Biggie died")
    
    # 4. 통계 출력
    print("\n[STATS] Database statistics:")
    node_stats = graph.query("""
        MATCH (n)
        RETURN labels(n)[0] as label, count(*) as count
        ORDER BY count DESC
    """)
    for record in node_stats:
        print(f"  - {record['label']}: {record['count']}")
    
    rel_stats = graph.query("""
        MATCH ()-[r]->()
        RETURN type(r) as relation, count(*) as count
        ORDER BY count DESC
        LIMIT 15
    """)
    print("\n  Top relationships:")
    for record in rel_stats:
        print(f"  - {record['relation']}: {record['count']}")
    
    print("\n" + "=" * 60)
    print("[DONE] Corrected data loaded!")
    print("\nTest queries in the detective app:")
    print('  - "퍼프 대디가 투팍을 죽였어?"')
    print('  - "올랜도 앤더슨은 누구야?"')
    print('  - "키피 D와 올랜도의 관계는?"')
    print('  - "투팍이 올랜도에게 무슨 짓을 했어?"')
    print("=" * 60)

if __name__ == "__main__":
    seed_corrected_data()
