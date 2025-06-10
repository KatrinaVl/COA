import clickhouse_connect
import uuid
from datetime import datetime
from typing import List, Dict

client = clickhouse_connect.get_client(
    host='clickhouse',
    port=8123,
    username='admin',
    password='admin123'
)

# docker exec -it clickhouse clickhouse-client

def init_clickhouse():
    try:
        query = """
        CREATE TABLE IF NOT EXISTS poststat (
            id String,
            update DateTime,
            post_id String,
            number_likes Int32,
            number_see Int32,
            number_comments Int32
        ) ENGINE = MergeTree()
        ORDER BY (id, post_id)
        """
        client.command(query)
        
        query = """
        CREATE TABLE IF NOT EXISTS activestat (
            id String,
            type String,
            post_id String,
            user_id String,
            date DateTime
        ) ENGINE = MergeTree()
        ORDER BY (id, post_id, user_id)
        """
        client.command(query)
    except Exception as e:
        print(f"Error initializing ClickHouse: {e}")

def post_liked(data):
    try:
        id_t = str(uuid.uuid4())
        post_id = data.get("post_id")
        user_id = data.get("user_id")
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Inserting to ClickHouse: id={id_t}, post_id={post_id}, user_id={user_id}", flush=True)

        if not all([post_id, user_id]):
            print("Missing fields in post_liked event:", data)
            return

        query = f"""
        INSERT INTO activestat (id, type, post_id, user_id, date) VALUES
        ('{id_t}', 'like', '{post_id}', '{user_id}', toDateTime('{now}'))
        """
        
        client.command(query)

        print(f"Inserted like event into activestat: {data}", flush=True)
    except Exception as e:
        print(f"Failed to insert like event into activestat: {e}", flush=True)


def post_seen(data):
    try:
        id_t = str(uuid.uuid4())
        post_id = data.get("post_id")
        user_id = data.get("user_id")
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Inserting to ClickHouse: id={id_t}, post_id={post_id}, user_id={user_id}", flush=True)

        if not all([post_id, user_id]):
            print("Missing fields in post_seen event:", data)
            return

        query = f"""
        INSERT INTO activestat (id, type, post_id, user_id, date) VALUES
        ('{id_t}', 'see', '{post_id}', '{user_id}', toDateTime('{now}'))
        """

        client.command(query)

        print(f"Inserted see event into activestat: {data}", flush=True)
    except Exception as e:
        print(f"Failed to insert see event into activestat: {e}", flush=True)


def post_commented(data):
    try:
        id_t = str(uuid.uuid4())
        post_id = data["comment"]["post_id"]
        user_id = data["comment"]["user_id"]
        comment_text = data["comment"]["text"]
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        print(f"Inserting to ClickHouse: id={id_t}, post_id={post_id}, user_id={user_id}, comment={comment_text}", flush=True)

        if not all([post_id, user_id]):
            print("Missing fields in post_commented event:", data)
            return

        query = f"""
        INSERT INTO activestat (id, type, post_id, user_id, date) VALUES
        ('{id_t}', 'comment', '{post_id}', '{user_id}', toDateTime('{now}'))
        """

        client.command(query)

        print(f"Inserted comment event into activestat: {data}", flush=True)
    except Exception as e:
        print(f"Failed to insert comment event into activestat: {e}", flush=True)

        

def get_see(post_id):
    query = f"""
    SELECT count() FROM activestat WHERE post_id = '{post_id}' AND type = 'see'
    """
    result = client.command(query)
    return int(result) if result else 0

def get_likes(post_id):
    query = f"""
    SELECT count() FROM activestat WHERE post_id = '{post_id}' AND type = 'like'
    """
    result = client.command(query)
    return int(result) if result else 0

def get_comments(post_id):
    query = f"""
    SELECT count() FROM activestat WHERE post_id = '{post_id}' AND type = 'comment'
    """
    result = client.command(query)
    return int(result) if result else 0

def get_see_dynamics(post_id: str) -> List[Dict]:
    query = f"""
    SELECT toDate(date) AS day, count(*) AS views
    FROM activestat
    WHERE post_id = '{post_id}' AND type = 'see'
    GROUP BY day
    ORDER BY day
    """
    result = client.query(query)
    return [{'day': row[0], 'views': row[1]} for row in result.result_rows]

def get_likes_dynamics(post_id: str) -> List[Dict]:
    query = f"""
    SELECT toDate(date) AS day, count(*) AS likes
    FROM activestat
    WHERE post_id = '{post_id}' AND type = 'like'
    GROUP BY day
    ORDER BY day
    """
    result = client.query(query)
    return [{'day': row[0], 'likes': row[1]} for row in result.result_rows]

def get_comments_dynamics(post_id: str) -> List[Dict]:
    query = f"""
    SELECT toDate(date) AS day, count(*) AS comments
    FROM activestat
    WHERE post_id = '{post_id}' AND type = 'comment'
    GROUP BY day
    ORDER BY day
    """
    result = client.query(query)
    return [{'day': row[0], 'comments': row[1]} for row in result.result_rows]

def get_top_posts(stat_type: str) -> List[Dict]:
    if stat_type not in ['like', 'comment', 'see']:
        raise ValueError("stat_type must be one of 'like', 'comment', 'see'")
    query = f"""
    SELECT post_id, count(*) AS cnt
    FROM activestat
    WHERE type = '{stat_type}'
    GROUP BY post_id
    ORDER BY cnt DESC
    LIMIT 10
    """
    result = client.query(query)
    return [{'post_id': row[0], 'count': row[1]} for row in result.result_rows]

def get_top_users(stat_type: str) -> List[Dict]:
    if stat_type not in ['like', 'comment', 'see']:
        raise ValueError("stat_type must be one of 'like', 'comment', 'see'")
    query = f"""
    SELECT user_id, count(*) AS cnt
    FROM activestat
    WHERE type = '{stat_type}'
    GROUP BY user_id
    ORDER BY cnt DESC
    LIMIT 10
    """
    result = client.query(query)
    return [{'user_id': row[0], 'count': row[1]} for row in result.result_rows]



# docker exec -it library-database-1 psql -U KV -d library_db
