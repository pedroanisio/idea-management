from models.core import TechnologyType, TechStack, TechnologyVersion
from extensions import db
from datetime import date

def seed_technology_types():
    # Create initial technology types
    types = [
        {
            'name': 'Programming Language',
            'description': 'Programming languages used in software development'
        },
        {
            'name': 'Operating System',
            'description': 'Operating systems and platforms'
        },
        {
            'name': 'Framework',
            'description': 'Software frameworks and libraries'
        },
        {
            'name': 'Database',
            'description': 'Database management systems and storage solutions'
        },
        {
            'name': 'Cloud Service',
            'description': 'Cloud computing and hosting services'
        },
        {
            'name': 'Development Tool',
            'description': 'Development tools, IDEs, and utilities'
        }
    ]

    # Add types if they don't exist
    for type_data in types:
        if not TechnologyType.query.filter_by(name=type_data['name']).first():
            tech_type = TechnologyType(**type_data)
            db.session.add(tech_type)
    
    # Commit the types
    db.session.commit()

    # Add some example technologies with versions
    programming_lang_type = TechnologyType.query.filter_by(name='Programming Language').first()
    if programming_lang_type:
        # Python with versions
        python = TechStack.query.filter_by(name='Python').first()
        if not python:
            python = TechStack(
                name='Python',
                description='A high-level, general-purpose programming language',
                technology_type=programming_lang_type
            )
            db.session.add(python)
            db.session.commit()

            # Add Python versions
            python_versions = [
                {
                    'version': '3.11',
                    'release_date': date(2022, 10, 24),
                    'end_of_life_date': date(2027, 10, 24),
                    'is_default': True,
                    'tech_stack_id': python.id
                },
                {
                    'version': '3.10',
                    'release_date': date(2021, 10, 4),
                    'end_of_life_date': date(2026, 10, 4),
                    'is_default': False,
                    'tech_stack_id': python.id
                }
            ]
            
            for version_data in python_versions:
                version = TechnologyVersion(**version_data)
                db.session.add(version)
            
            db.session.commit()
