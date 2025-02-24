from app import create_app, db, TechnologyType

app = create_app()

with app.app_context():
    tech_types = TechnologyType.query.all()
    print(f"Found {len(tech_types)} technology types")
    
    if not tech_types:
        # Seed some default technology types
        default_types = [
            ("Programming Language", "Programming Language"),
            ("Framework", "Framework"),
            ("Database", "Database"),
            ("Cloud Service", "Cloud Service"),
            ("Operating System", "Operating System"),
            ("Protocol", "Protocol"),
            ("Other", "Other"),
            ("AI", "AI"),
            ("Machine Learning", "Machine Learning"),
            ("Deep Learning", "Deep Learning"),
            ("Natural Language Processing", "Natural Language Processing"),
            ("Package Manager", "Package Manager"),
            ("Design Pattern", "Design Pattern"),
            ("Package", "Package"),
        ]
        
        for name, desc in default_types:
            tech_type = TechnologyType(name=name, description=desc)
            db.session.add(tech_type)
        
        db.session.commit()
        print("Added default technology types")
        tech_types = TechnologyType.query.all()
    
    for tech_type in tech_types:
        print(f"- {tech_type.name}: {tech_type.description}")
