from nexy.decorators import Injectable

@Injectable()
class DatabaseService:
    def get_connection(self):
        return "DB_CONNECTION_OK"

@Injectable()
class UserService:
    # Injection imbriquée : UserService a besoin de DatabaseService
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_users(self):
        conn = self.db.get_connection()
        return {"users": ["Alice", "Bob"], "db_status": conn}
