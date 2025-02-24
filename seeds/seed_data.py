from app import create_app, db
from models.core import (
    Idea, 
    EvolutionCycle, 
    Phase, 
    Requirement, 
    RequirementType, 
    RequirementPriority, 
    Status, 
    TechStack, 
    Technology
)

def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    with app.app_context():
        # Create statuses
        statuses = [
            Status(name="not initiated"),
            Status(name="in progress"),
            Status(name="completed"),
            Status(name="delayed"),
            Status(name="cancelled")
        ]
        db.session.add_all(statuses)
        
        # Create requirement types
        req_types = [
            RequirementType(name="functional"),
            RequirementType(name="non-functional"),
            RequirementType(name="technical"),
            RequirementType(name="business")
        ]
        db.session.add_all(req_types)
        
        # Create requirement priorities
        priorities = [
            RequirementPriority(name="must-have"),
            RequirementPriority(name="should-have"),
            RequirementPriority(name="nice-to-have"),
            RequirementPriority(name="won't-have")
        ]
        db.session.add_all(priorities)
        
        # Create technologies
        technologies = [
            Technology(name="Python", description="Programming language"),
            Technology(name="Flask", description="Web framework"),
            Technology(name="SQLite", description="Database"),
            Technology(name="SQLAlchemy", description="ORM"),
            Technology(name="TailwindCSS", description="CSS framework"),
            Technology(name="JavaScript", description="Programming language"),
            Technology(name="HTML", description="Markup language"),
            Technology(name="CSS", description="Styling language")
        ]
        db.session.add_all(technologies)
        
        # Create tech stack
        tech_stack = TechStack(
            name="Flask Web App",
            description="A web application built with Flask, SQLAlchemy, and TailwindCSS"
        )
        tech_stack.technologies.extend([t for t in technologies])
        db.session.add(tech_stack)
        
        # Commit changes to get IDs
        db.session.commit()
        
        # Get references to created objects
        in_progress_status = Status.query.filter_by(name="in progress").first()
        not_initiated_status = Status.query.filter_by(name="not initiated").first()
        must_have_priority = RequirementPriority.query.filter_by(name="must-have").first()
        nice_to_have_priority = RequirementPriority.query.filter_by(name="nice-to-have").first()
        functional_type = RequirementType.query.filter_by(name="functional").first()
        non_functional_type = RequirementType.query.filter_by(name="non-functional").first()
        
        # Create idea
        idea = Idea(
            name="Idea Management",
            description="Manage your ideas in one place",
            slug="idea-management",
            status=in_progress_status
        )
        idea.tech_stacks.append(tech_stack)
        db.session.add(idea)
        db.session.commit()
        
        # Create evolution cycles
        sdlc_evolution = EvolutionCycle(name="SDLC Evolutions", idea=idea)
        env_evolution = EvolutionCycle(name="Environments", idea=idea)
        db.session.add_all([sdlc_evolution, env_evolution])
        db.session.commit()
        
        # Create phases for SDLC evolution
        sdlc_phases = [
            Phase(name="Proof of Concept", description="Test the idea", order=1, status=in_progress_status, evolution_cycle=sdlc_evolution),
            Phase(name="Minimum Viable Product", description="Build the first version", order=2, status=not_initiated_status, evolution_cycle=sdlc_evolution),
            Phase(name="Launch", description="Release the product", order=3, status=not_initiated_status, evolution_cycle=sdlc_evolution),
            Phase(name="Growth", description="Scale the product", order=4, status=not_initiated_status, evolution_cycle=sdlc_evolution),
            Phase(name="Maintenance", description="Keep the product running", order=5, status=not_initiated_status, evolution_cycle=sdlc_evolution)
        ]
        db.session.add_all(sdlc_phases)
        
        # Create phases for Environments evolution
        env_phases = [
            Phase(name="Development", description="Test the idea", order=1, status=not_initiated_status, evolution_cycle=env_evolution),
            Phase(name="Staging", description="Build the first version", order=2, status=not_initiated_status, evolution_cycle=env_evolution),
            Phase(name="Test", description="Release the product", order=3, status=not_initiated_status, evolution_cycle=env_evolution),
            Phase(name="Production", description="Scale the product", order=4, status=not_initiated_status, evolution_cycle=env_evolution)
        ]
        db.session.add_all(env_phases)
        db.session.commit()
        
        # Create requirements
        requirements = [
            Requirement(
                name="Seed Database",
                description="Seed the database with initial data for 'EvolutionsCycle', 'Phases', 'Requirements', 'RequirementTypes', 'RequirementPriorities', 'Statuses', 'TechStacks', and 'Technologies'.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="FLASK App",
                description="Develop the Flask backend application.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Sqlite Database",
                description="Set up the SQLite database.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="UI/UX Design",
                description="Implement UI/UX using TailwindCSS.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Models & Relationships",
                description="""Entities:

Idea
EvolutionCycle
Phase
Requirement
RequirementType
RequirementPriority
Status
TechStack
Technologies

Relationships:

An Idea has many EvolutionCycles.
An Idea has one active Status.
An EvolutionCycle comprises many Phases.
A Phase encompasses many Requirements.
A Requirement can belong to multiple RequirementTypes.
Each Requirement carries a defined priority and status.
Combined, an Idea, its EvolutionCycle, and its Phase map to one or more TechStacks.
A TechStack includes many Technologies.

This model and its relationships are critical and will be validated during the Proof of Concept (POC) phase.""",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Documentation",
                description="Document the system using markdown.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Export",
                description="Implement feature to export data to CSV.",
                status=not_initiated_status,
                priority=nice_to_have_priority
            ),
            Requirement(
                name="User will be able to create new EvolutionCycle",
                description="Allow users to create and manage new evolution cycles.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="User will be able to create new Phase",
                description="Allow users to create and manage new phases.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="User will be able to create new TechStack and Technologies",
                description="Allow users to create and manage new TechStacks and associated Technologies.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Modern Web App UI/UX",
                description="Ensure responsive design and modern UI/UX guidelines.",
                status=not_initiated_status,
                priority=must_have_priority
            ),
            Requirement(
                name="Mandatory Files and Structure",
                description="""Define and enforce the project file structure, including mandatory files:
README
.gitignore
app.py
/models/core.py""",
                status=not_initiated_status,
                priority=must_have_priority
            )
        ]
        
        # Add types to requirements
        for req in requirements:
            if req.name in ["Export", "User will be able to create new EvolutionCycle", 
                           "User will be able to create new Phase", 
                           "User will be able to create new TechStack and Technologies"]:
                req.types.append(functional_type)
            else:
                req.types.append(non_functional_type)
        
        db.session.add_all(requirements)
        
        # Link requirements to phases
        poc_phase = Phase.query.filter_by(name="Proof of Concept").first()
        models_req = Requirement.query.filter_by(name="Models & Relationships").first()
        poc_phase.requirements.append(models_req)
        
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
