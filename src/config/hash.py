import bcrypt

class PasswordManager:
    """Password hashing and verification utility using bcrypt"""
    
    def __init__(self, rounds: int = 12):
        """
        Initialize with bcrypt rounds (default: 12)
        Higher rounds = more secure but slower
        """
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

# Global instance
password_manager = PasswordManager()

# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return password_manager.hash_password(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password"""
    return password_manager.verify_password(password, hashed)