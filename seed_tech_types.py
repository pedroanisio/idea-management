from app import create_app
from extensions import db
from seeds.technology_types import seed_technology_types

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_technology_types()
        print("Technology types seeded successfully!")
