"""
Hip-Hop Noir 데이터베이스 시드 스크립트
90년대 힙합 씬의 인물, 갱단, 사건 관계도를 구축합니다.
"""
import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph

load_dotenv()

# 그래프 연결
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)


def seed_database():
    """Neo4j 데이터베이스에 힙합 느와르 데이터를 주입합니다."""
    print("🧹 기존 데이터 삭제 중...")
    try:
        graph.query("MATCH (n) DETACH DELETE n")
        print("✅ 기존 데이터 삭제 완료")
    except Exception as e:
        print(f"⚠️ 데이터 삭제 중 오류 (무시 가능): {e}")

    print("\n🔫 힙합 느와르 데이터 주입 중...")
    
    # 1. 인물 및 조직 생성
    print("  → 인물 및 조직 생성 중...")
    create_nodes = """
    // 서부 (West Coast) - Death Row Records
    CREATE (pac:Rapper {name: "Tupac Shakur", aka: "2Pac", status: "Deceased", birth_year: 1971, death_year: 1996})
    CREATE (suge:Producer {name: "Suge Knight", aka: "Sugar Bear", status: "Alive", birth_year: 1965})
    CREATE (deathrow:Label {name: "Death Row Records", location: "Los Angeles", founded: 1991})
    CREATE (mob:Gang {name: "Mob Piru Bloods", territory: "Compton, LA"})
    
    // 동부 (East Coast) - Bad Boy Records
    CREATE (biggie:Rapper {name: "Notorious B.I.G.", aka: "Biggie Smalls", status: "Deceased", birth_year: 1972, death_year: 1997})
    CREATE (diddy:Producer {name: "P. Diddy", aka: "Puff Daddy", status: "Alive", birth_year: 1969})
    CREATE (badboy:Label {name: "Bad Boy Records", location: "New York", founded: 1993})
    CREATE (crips:Gang {name: "Southside Crips", territory: "Compton, LA"})
    
    // 추가 인물들
    CREATE (drdre:Producer {name: "Dr. Dre", status: "Alive", birth_year: 1965})
    CREATE (snoop:Rapper {name: "Snoop Dogg", status: "Alive", birth_year: 1971})
    CREATE (orlando:Person {name: "Orlando Anderson", aka: "Baby Lane", status: "Deceased", birth_year: 1974, death_year: 1998})
    CREATE (keefe:Person {name: "Keefe D", aka: "Duane Keith Davis", status: "Alive", birth_year: 1965})
    CREATE (dexter:Person {name: "Dexter Isaac", status: "Alive"})
    
    // 추가 조직
    CREATE (ywk:Gang {name: "Young Wanna-be Killers", territory: "Brooklyn, NY"})
    CREATE (luther:Person {name: "Luther Campbell", status: "Alive"})
    """
    
    # 2. 계약 및 소속 관계
    print("  → 계약 및 소속 관계 생성 중...")
    create_contracts = """
    MATCH (pac:Rapper {name: "Tupac Shakur"}), (deathrow:Label {name: "Death Row Records"})
    MATCH (suge:Producer {name: "Suge Knight"}), (mob:Gang {name: "Mob Piru Bloods"})
    MATCH (biggie:Rapper {name: "Notorious B.I.G."}), (badboy:Label {name: "Bad Boy Records"})
    MATCH (diddy:Producer {name: "P. Diddy"})
    MATCH (snoop:Rapper {name: "Snoop Dogg"}), (drdre:Producer {name: "Dr. Dre"})
    MATCH (orlando:Person {name: "Orlando Anderson"}), (crips:Gang {name: "Southside Crips"})
    MATCH (keefe:Person {name: "Keefe D"}), (dexter:Person {name: "Dexter Isaac"})
    MATCH (ywk:Gang {name: "Young Wanna-be Killers"})
    
    // 레이블 계약
    MERGE (pac)-[:SIGNED_TO {year: 1995, duration: "until death"}]->(deathrow)
    MERGE (biggie)-[:SIGNED_TO {year: 1993}]->(badboy)
    MERGE (snoop)-[:SIGNED_TO {year: 1992}]->(deathrow)
    MERGE (drdre)-[:CO_FOUNDED {year: 1991}]->(deathrow)
    
    // 레이블 창립/경영
    MERGE (suge)-[:FOUNDED {year: 1991}]->(deathrow)
    MERGE (diddy)-[:FOUNDED {year: 1993}]->(badboy)
    
    // 갱단 소속
    MERGE (suge)-[:AFFILIATED_WITH {since: 1990}]->(mob)
    MERGE (pac)-[:AFFILIATED_WITH {since: 1995}]->(mob)
    MERGE (orlando)-[:MEMBER_OF {since: 1992}]->(crips)
    MERGE (keefe)-[:MEMBER_OF {since: 1990}]->(crips)
    MERGE (dexter)-[:AFFILIATED_WITH]->(ywk)
    """
    
    # 3. 갈등 및 사건 (Events & Conflicts)
    print("  → 갈등 및 사건 생성 중...")
    create_relations = """
    MATCH (pac:Rapper {name: "Tupac Shakur"}), (biggie:Rapper {name: "Notorious B.I.G."})
    MATCH (mob:Gang {name: "Mob Piru Bloods"}), (crips:Gang {name: "Southside Crips"})
    MATCH (orlando:Person {name: "Orlando Anderson"}), (keefe:Person {name: "Keefe D"})
    MATCH (suge:Producer {name: "Suge Knight"}), (diddy:Producer {name: "P. Diddy"})
    MATCH (dexter:Person {name: "Dexter Isaac"})
    MATCH (deathrow:Label {name: "Death Row Records"}), (badboy:Label {name: "Bad Boy Records"})
    
    // 갱단 간 전쟁
    MERGE (mob)-[:AT_WAR_WITH {since: 1980, reason: "Territory dispute"}]->(crips)
    
    // 레이블 간 경쟁
    MERGE (deathrow)-[:RIVALRY_WITH]->(badboy)
    MERGE (suge)-[:BEEF_WITH {reason: "Business competition and personal animosity"}]->(diddy)
    
    // 래퍼 간 개인적 원한 (Beef)
    MERGE (pac)-[:BEEF_WITH {reason: "Hit 'Em Up Diss Track", year: 1996, severity: "extreme"}]->(biggie)
    MERGE (pac)-[:BEEF_WITH {reason: "Thinks Biggie knew about 1994 shooting", year: 1994}]->(biggie)
    MERGE (pac)-[:SUSPECTED {reason: "1994 shooting in Quad Studios", year: 1994}]->(biggie)
    
    // 결정적 사건 (The Trigger Event - 투팍 사망 당일)
    // 투팍이 죽기 몇 시간 전, MGM Grand 로비에서 올랜도를 폭행함
    MERGE (pac)-[:ATTACKED {location: "MGM Grand Lobby", date: "1996-09-07", time: "Evening", method: "Physical assault", witnesses: "Multiple"}]->(orlando)
    
    // 올랜도와 동행자들 (Vegas 당일)
    MERGE (orlando)-[:WAS_IN_VEGAS {date: "1996-09-07", purpose: "Boxing match attendance"}]->(pac)
    MERGE (keefe)-[:WAS_IN_VEGAS {date: "1996-09-07"}]->(pac)
    MERGE (keefe)-[:RELATED_TO {relation: "Uncle"}]->(orlando)
    
    // 실제 살해 사건 (Event Node로 명시)
    CREATE (pacmurder:Event {type: "Homicide", victim: "Tupac Shakur", date: "1996-09-07", location: "Las Vegas, Flamingo Road", weapon: "Firearm", status: "Unsolved"})
    CREATE (biggiemurder:Event {type: "Homicide", victim: "Notorious B.I.G.", date: "1997-03-09", location: "Los Angeles, Wilshire Blvd", weapon: "Firearm", status: "Unsolved"})
    
    // 사건과 인물 연결
    MATCH (pac:Rapper {name: "Tupac Shakur"}), (pacmurder:Event {victim: "Tupac Shakur"})
    MATCH (biggie:Rapper {name: "Notorious B.I.G."}), (biggiemurder:Event {victim: "Notorious B.I.G."})
    MERGE (pac)-[:DIED_IN]->(pacmurder)
    MERGE (biggie)-[:DIED_IN]->(biggiemurder)
    
    // 용의자 연결 (명시적이지 않은, 추론용 관계)
    MATCH (orlando:Person {name: "Orlando Anderson"}), (pacmurder:Event {victim: "Tupac Shakur"})
    MERGE (orlando)-[:PRESENT_AT {circumstantial: true}]->(pacmurder)
    MERGE (keefe)-[:PRESENT_AT {circumstantial: true}]->(pacmurder)
    MERGE (orlando)-[:MOTIVE {reason: "Retaliation for MGM Grand assault", strength: "high"}]->(pacmurder)
    
    // 1994년 사건 (추가 배경 정보)
    CREATE (quadshooting:Event {type: "Shooting", victim: "Tupac Shakur", date: "1994-11-30", location: "New York, Quad Studios", perpetrator: "Unknown"})
    MATCH (pac:Rapper {name: "Tupac Shakur"}), (quadshooting:Event {victim: "Tupac Shakur"})
    MERGE (pac)-[:SHOT_AT]->(quadshooting)
    MERGE (dexter)-[:SUSPECTED_OF {crime: "Quad Studios shooting", year: 1994}]->(quadshooting)
    """

    # 실행
    try:
        graph.query(create_nodes)
        graph.query(create_contracts)
        graph.query(create_relations)
        print("\n✅ 데이터 구축 완료!")
        print("\n📊 데이터베이스 통계:")
        
        # 통계 조회
        stats = graph.query("""
            MATCH (n)
            RETURN labels(n)[0] as label, count(*) as count
            ORDER BY count DESC
        """)
        
        for record in stats:
            print(f"  - {record['label']}: {record['count']}개")
        
        relation_stats = graph.query("""
            MATCH ()-[r]->()
            RETURN type(r) as relation, count(*) as count
            ORDER BY count DESC
        """)
        
        print("\n관계 통계:")
        for record in relation_stats:
            print(f"  - {record['relation']}: {record['count']}개")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        raise


if __name__ == "__main__":
    seed_database()

