from .neo4j_driver import db
import uuid

def start_session(user_id):
    """Creates a session node and returns the UUID."""
    query = """
    MERGE (u:User {id: $user_id})
    CREATE (s:Session {
        uuid: $uuid,
        start_time: datetime(),
        status: 'active'
    })
    CREATE (u)-[:STARTED_SESSION]->(s)
    RETURN s.uuid AS session_id
    """
    result = db.query(query, {"user_id": user_id, "uuid": str(uuid.uuid4())})
    # db.query returns a list of records; we want the first one
    return result[0]['session_id']

def end_session(session_id):
    """Closes the session and calculates duration."""
    query = """
    MATCH (s:Session {uuid: $session_id})
    SET s.end_time = datetime(),
        s.status = 'completed',
        s.duration_seconds = duration.between(s.start_time, datetime()).seconds
    RETURN s.duration_seconds AS duration
    """
    result = db.query(query, {"session_id": session_id})
    return result[0]['duration'] if result else 0

def log_manual_time(user_id, hours, description):
    query = """
    MERGE (u:User {id: $user_id})
    CREATE (s:Session {
        uuid: $uuid,
        start_time: datetime(),
        end_time: datetime(),
        duration_seconds: $seconds,
        status: 'manual_entry',
        note: $description
    })
    CREATE (u)-[:STARTED_SESSION]->(s)
    RETURN s.duration_seconds
    """
    db.query(query, {
        "user_id": user_id, 
        "uuid": str(uuid.uuid4()),
        "seconds": float(hours) * 3600,
        "description": description
    })
