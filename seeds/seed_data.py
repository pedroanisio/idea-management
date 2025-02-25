from app import create_app, db
from models.core import (
    Idea, 
    EvolutionCycle,
    IdeaEvolutionCycle,
    Phase,
    IdeaEvolutionPhase, 
    Requirement, 
    RequirementType, 
    RequirementPriority, 
    Status, 
    TechStack, 
    Technology,
    TechnologyType
)

def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    with app.app_context():
        # Drop all data first
        db.drop_all()
        db.create_all()

        # Create statuses
        statuses = [
            Status(name="New"),
            Status(name="In Progress"),
            Status(name="Completed"),
            Status(name="Delayed"),
            Status(name="Cancelled")
        ]
        db.session.add_all(statuses)
        
        # Create requirement types
        req_types = [
            RequirementType(name="Functional"),
            RequirementType(name="Non-Functional"),
            RequirementType(name="Technical"),
            RequirementType(name="Business")
        ]
        db.session.add_all(req_types)
        
        # Create requirement priorities
        priorities = [
            RequirementPriority(name="Must Have"),
            RequirementPriority(name="Should Have"),
            RequirementPriority(name="Nice to Have"),
            RequirementPriority(name="Won't Have")
        ]
        db.session.add_all(priorities)

        # Create technology types
        tech_types = [
            TechnologyType(name="Programming Language"),
            TechnologyType(name="Framework"),
            TechnologyType(name="Database"),
            TechnologyType(name="ORM"),
            TechnologyType(name="Frontend"),
        ]
        db.session.add_all(tech_types)
        db.session.commit()
        
        # Get technology types
        prog_lang_type = TechnologyType.query.filter_by(name="Programming Language").first()
        framework_type = TechnologyType.query.filter_by(name="Framework").first()
        database_type = TechnologyType.query.filter_by(name="Database").first()
        orm_type = TechnologyType.query.filter_by(name="ORM").first()
        frontend_type = TechnologyType.query.filter_by(name="Frontend").first()
        
        # Create technologies
        technologies = [
            Technology(name="Python", description="Programming language", type_id=prog_lang_type.id),
            Technology(name="Flask", description="Web framework", type_id=framework_type.id),
            Technology(name="SQLite", description="Database", type_id=database_type.id),
            Technology(name="SQLAlchemy", description="ORM", type_id=orm_type.id),
            Technology(name="TailwindCSS", description="CSS framework", type_id=frontend_type.id),
            Technology(name="JavaScript", description="Programming language", type_id=prog_lang_type.id),
            Technology(name="HTML", description="Markup language", type_id=frontend_type.id),
            Technology(name="CSS", description="Styling language", type_id=frontend_type.id)
        ]
        db.session.add_all(technologies)
        
        # Create tech stack
        tech_stack = TechStack(
            name="Flask Web App",
            description="A web application built with Flask, SQLAlchemy, and TailwindCSS",
            type_id=framework_type.id
        )
        for tech in technologies:
            tech_stack.technologies.append(tech)
        db.session.add(tech_stack)
        
        # Commit changes to get IDs
        db.session.commit()

        # Get references to created objects
        in_progress_status = Status.query.filter_by(name="In Progress").first()
        new_status = Status.query.filter_by(name="New").first()
        must_have_priority = RequirementPriority.query.filter_by(name="Must Have").first()
        nice_to_have_priority = RequirementPriority.query.filter_by(name="Nice to Have").first()
        functional_type = RequirementType.query.filter_by(name="Functional").first()
        technical_type = RequirementType.query.filter_by(name="Technical").first()
        
        # Create idea
        idea = Idea(
            title="Idea Management",
            description="Manage your ideas in one place",
            status_id=in_progress_status.id
        )
        db.session.add(idea)
        db.session.commit()
        
        # Create evolution cycles
        sdlc_evolution = EvolutionCycle(
            name="SDLC Evolutions",
            description="Software Development Life Cycle phases",
            status_id=in_progress_status.id
        )
        env_evolution = EvolutionCycle(
            name="Environments",
            description="Different deployment environments",
            status_id=new_status.id
        )
        db.session.add_all([sdlc_evolution, env_evolution])
        db.session.commit()
        
        # Create IdeaEvolutionCycles
        idea_sdlc = IdeaEvolutionCycle(
            idea_id=idea.id,
            evolution_cycle_id=sdlc_evolution.id,
            status_id=in_progress_status.id
        )
        idea_env = IdeaEvolutionCycle(
            idea_id=idea.id,
            evolution_cycle_id=env_evolution.id,
            status_id=new_status.id
        )
        db.session.add_all([idea_sdlc, idea_env])
        db.session.commit()

        # Create phases for SDLC evolution
        sdlc_phases = [
            Phase(name="Proof of Concept", description="Test the idea", order=1, status_id=in_progress_status.id, evolution_cycle_id=sdlc_evolution.id),
            Phase(name="Minimum Viable Product", description="Build the first version", order=2, status_id=new_status.id, evolution_cycle_id=sdlc_evolution.id),
            Phase(name="Launch", description="Release the product", order=3, status_id=new_status.id, evolution_cycle_id=sdlc_evolution.id),
            Phase(name="Growth", description="Scale the product", order=4, status_id=new_status.id, evolution_cycle_id=sdlc_evolution.id),
            Phase(name="Maintenance", description="Keep the product running", order=5, status_id=new_status.id, evolution_cycle_id=sdlc_evolution.id)
        ]
        db.session.add_all(sdlc_phases)
        
        # Create phases for Environments evolution
        env_phases = [
            Phase(name="Development", description="Development environment", order=1, status_id=new_status.id, evolution_cycle_id=env_evolution.id),
            Phase(name="Staging", description="Staging environment", order=2, status_id=new_status.id, evolution_cycle_id=env_evolution.id),
            Phase(name="Test", description="Testing environment", order=3, status_id=new_status.id, evolution_cycle_id=env_evolution.id),
            Phase(name="Production", description="Production environment", order=4, status_id=new_status.id, evolution_cycle_id=env_evolution.id)
        ]
        db.session.add_all(env_phases)
        db.session.commit()

        # Create IdeaEvolutionPhases for SDLC
        for i, phase in enumerate(sdlc_phases):
            idea_phase = IdeaEvolutionPhase(
                idea_evolution_cycle_id=idea_sdlc.id,
                phase_id=phase.id,
                status_id=phase.status_id,
                order=phase.order
            )
            # Assign tech stack to development phase
            if phase.name == "Minimum Viable Product":
                idea_phase.tech_stacks.append(tech_stack)
            db.session.add(idea_phase)

        # Create IdeaEvolutionPhases for Environments
        for phase in env_phases:
            idea_phase = IdeaEvolutionPhase(
                idea_evolution_cycle_id=idea_env.id,
                phase_id=phase.id,
                status_id=phase.status_id,
                order=phase.order
            )
            db.session.add(idea_phase)
        
        db.session.commit()
        
        # Get first phase for requirements
        poc_phase = IdeaEvolutionPhase.query.join(Phase).filter(Phase.name == "Proof of Concept").first()
        
        # Create requirements
        requirements = [
            Requirement(
                name="Seed Database",
                description="Seed the database with initial data",
                status_id=new_status.id,
                priority_id=must_have_priority.id,
                type_id=technical_type.id,
                idea_evolution_phase_id=poc_phase.id
            ),
            Requirement(
                name="Flask App Setup",
                description="Set up the Flask backend application",
                status_id=new_status.id,
                priority_id=must_have_priority.id,
                type_id=technical_type.id,
                idea_evolution_phase_id=poc_phase.id
            ),
            Requirement(
                name="Database Models",
                description="Set up all database models and relationships",
                status_id=new_status.id,
                priority_id=must_have_priority.id,
                type_id=technical_type.id,
                idea_evolution_phase_id=poc_phase.id
            ),
            Requirement(
                name="UI Implementation",
                description="Implement the UI using TailwindCSS",
                status_id=new_status.id,
                priority_id=must_have_priority.id,
                type_id=functional_type.id,
                idea_evolution_phase_id=poc_phase.id
            )
        ]
        db.session.add_all(requirements)
        db.session.commit()
        print("Base data seeded successfully!")

if __name__ == "__main__":
    seed_database()
    from seeds.sample_data import seed_sample_data
    seed_sample_data()
    print("Database seeded successfully with base and sample data!")
