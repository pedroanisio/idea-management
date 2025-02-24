from app import app
from extensions import db
from models.core import Status, RequirementType, RequirementPriority

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create initial data
        # Status
        statuses = [
            Status(name='New'),
            Status(name='In Progress'),
            Status(name='Completed'),
            Status(name='On Hold')
        ]
        db.session.add_all(statuses)
        
        # Requirement Types
        types = [
            RequirementType(name='Functional'),
            RequirementType(name='Non-Functional'),
            RequirementType(name='Technical'),
            RequirementType(name='Business')
        ]
        db.session.add_all(types)
        
        # Requirement Priorities
        priorities = [
            RequirementPriority(name='Must Have'),
            RequirementPriority(name='Should Have'),
            RequirementPriority(name='Could Have'),
            RequirementPriority(name="Won't Have")
        ]
        db.session.add_all(priorities)
        
        # Commit changes
        db.session.commit()

if __name__ == '__main__':
    init_db()
