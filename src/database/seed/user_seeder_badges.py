from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import random

from ...models.user_badge import user_badge_association
from ...models.user import User, UserRole
from ...models.badges import Badge
from ..seeder import BaseSeeder

class UserSeederBadges(BaseSeeder):
    """Seeder untuk memberikan badges kepada users berdasarkan ID"""
    
    def run(self):
        """Run the user badge seeder"""
        try:
            print("🏆 Seeding user badges...")
            self.seed_user_badges()
            print("✅ User badges seeding completed.")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"User badges seeding failed: {e}")

    def seed_user_badges(self):
        """Seed user badges berdasarkan ID mapping"""
        users = self.db.query(User).all()
        badges = self.db.query(Badge).all()
        
        if not users:
            print("  ⚠️ No users found. Please run UserSeeder first.")
            return
            
        if not badges:
            print("  ⚠️ No badges found. Please run BadgeSeeder first.")
            return
        
        # Mapping user dengan badge IDs yang mau dikasih
        user_badge_mapping = {
            # Admin gets all badges (ID 1,2,3,4)
            "admin": [1, 2, 3, 4],
            
            # Moderator gets most badges (ID 1,2,3)
            "moderator": [1, 2, 3],
            
            # Regular users get starter badges
            "johndoe": [1],  # Only "First Steps"
            "janedoe": [1, 2],  # "First Steps" and "Alphabet Master"
        }
        
        assigned_count = 0
        for user in users:
            username = str(user.username)
            if username in user_badge_mapping:
                badge_ids = user_badge_mapping[username]
                user_assigned = self.assign_badges_by_id(user, badge_ids)
                assigned_count += user_assigned
                
                # Update user's total_badges count - ensure we have proper user_id
                if user_assigned > 0:
                    user_id = int(user.id) if user.id is not None else None # type: ignore
                    if user_id is not None:
                        setattr(user, "total_badges", self._get_user_badge_count(user_id))
                    
        self.db.commit()
        print(f"  ✅ Assigned {assigned_count} badges to users.")
    def assign_badges_by_id(self, user: User, badge_ids: List[int]) -> int:
        """Assign specific badge IDs to user"""
        assigned_count = 0
        
        # Get user_id value
        user_id = user.id if user.id is not None else None
        if user_id is None:
            print(f"    ❌ Invalid user ID for {user.username}")
            return 0
        
        for badge_id in badge_ids:
            # Check if user already has this badge
            if not self._user_has_badge(user_id, badge_id):
                # Get badge name for logging
                badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
                if badge:
                    self._award_badge(user_id, badge_id) # type: ignore
                    assigned_count += 1
                    print(f"    ✅ {user.username} earned '{badge.nama}' (ID: {badge_id})")
                else:
                    print(f"    ❌ Badge ID {badge_id} not found")
            else:
                badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
                badge_name = badge.nama if badge else f"ID {badge_id}"
                print(f"    ⚠️ {user.username} already has '{badge_name}'")
        
        return assigned_count
    def _user_has_badge(self, user_id, badge_id) -> bool:
        """Check if user already has this badge"""
        result = self.db.execute(
            text("SELECT 1 FROM user_badges WHERE user_id = :user_id AND badge_id = :badge_id"),
            {"user_id": user_id, "badge_id": badge_id}
        ).first()
        return result is not None

    def _award_badge(self, user_id: int, badge_id: int, earned_date: datetime = None):
        """Award a badge to user"""
        if earned_date is None:
            earned_date = datetime.utcnow()
            
        insert_stmt = user_badge_association.insert().values(
            user_id=user_id,
            badge_id=badge_id,
            earned_at=earned_date
        )
        self.db.execute(insert_stmt)

    def _get_user_badge_count(self, user_id: int) -> int:
        """Get count of badges for a user"""
        result = self.db.execute(
            text("SELECT COUNT(*) as count FROM user_badges WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        return result[0] if result else 0

    # Utility methods untuk manual assignment
    def assign_badge_to_user(self, user_id: int, badge_id: int) -> bool:
        """Manually assign badge ID to user ID"""
        try:
            if self._user_has_badge(user_id, badge_id):
                print(f"❌ User ID {user_id} already has badge ID {badge_id}")
                return False
                
            self._award_badge(user_id, badge_id)
            
            # Update user's total_badges
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                setattr(user, "total_badges", self._get_user_badge_count(user_id))
                
            self.db.commit()
            print(f"✅ Badge ID {badge_id} awarded to user ID {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error: {e}")
            return False
            
    def assign_multiple_badges(self, assignments: Dict[int, List[int]]):
        """
        Assign multiple badges to multiple users
        Format: {user_id: [badge_id1, badge_id2, ...]}
        
        Example:
        assignments = {
            1: [1, 2, 3, 4],  # User ID 1 gets badge IDs 1,2,3,4
            2: [1, 2, 3],     # User ID 2 gets badge IDs 1,2,3
            3: [1],           # User ID 3 gets badge ID 1
        }
        """
        try:
            total_assigned = 0
            
            for user_id, badge_ids in assignments.items():
                user = self.db.query(User).filter(User.id == user_id).first()
                if not user:
                    print(f"❌ User ID {user_id} not found")
                    continue
                    
                assigned_count = self.assign_badges_by_id(user, badge_ids)
                total_assigned += assigned_count
                
                # Update user's total_badges
                if assigned_count > 0:
                    setattr(user, "total_badges", self._get_user_badge_count(user_id))
            
            self.db.commit()
            print(f"✅ Total {total_assigned} badges assigned")
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error in bulk assignment: {e}")

# Contoh penggunaan untuk manual assignment
def quick_assign_badges():
    """Quick function untuk assign badges by ID"""
    seeder = UserSeederBadges()
    
    # Contoh assignment by ID
    assignments = {
        1: [1, 2, 3, 4],  # Admin (user ID 1) gets all badges
        2: [1, 2, 3],     # Moderator (user ID 2) gets 3 badges  
        3: [1],           # User (user ID 3) gets 1 badge
        4: [1, 2],        # User (user ID 4) gets 2 badges
    }
    
    seeder.assign_multiple_badges(assignments)
    seeder.close()

# Standalone functions
def assign_badge(user_id: int, badge_id: int):
    """Assign single badge to user"""
    seeder = UserSeederBadges()
    result = seeder.assign_badge_to_user(user_id, badge_id)
    seeder.close()
    return result