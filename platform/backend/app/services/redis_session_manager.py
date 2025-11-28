import redis
import json

class RedisSessionManager:
    def __init__(self):
        self.client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    def get_session(self, session_id):
        data = self.client.get(session_id)
        return json.loads(data) if data else {}

    def update_session(self, session_id, state):
        self.client.set(session_id, json.dumps(state))

    def create_session(self):
        import uuid
        session = str(uuid.uuid4())
        self.client.set(session, json.dumps({}))
        return session


session_manager = RedisSessionManager()