from app import create_app, db
from datetime import datetime
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
    TechnologyType,
    TechnologyVersion,
    TechnologyVersionAggregate
)

def seed_sample_data():
    """Seed a complete sample idea with all features."""
    app = create_app()
    with app.app_context():
        # Check if sample data already exists
        if Idea.query.filter_by(title="AI Chat Application").first():
            print("Sample data already exists, skipping...")
            return

        # Get existing data
        new_status = Status.query.filter_by(name="New").first()
        in_progress_status = Status.query.filter_by(name="In Progress").first()
        completed_status = Status.query.filter_by(name="Completed").first()
        
        must_have = RequirementPriority.query.filter_by(name="Must Have").first()
        should_have = RequirementPriority.query.filter_by(name="Should Have").first()
        nice_to_have = RequirementPriority.query.filter_by(name="Nice to Have").first()
        
        functional = RequirementType.query.filter_by(name="Functional").first()
        non_functional = RequirementType.query.filter_by(name="Non-Functional").first()
        technical = RequirementType.query.filter_by(name="Technical").first()
        business = RequirementType.query.filter_by(name="Business").first()

        # Get technology types
        prog_lang_type = TechnologyType.query.filter_by(name="Programming Language").first()
        framework_type = TechnologyType.query.filter_by(name="Framework").first()
        frontend_type = TechnologyType.query.filter_by(name="Frontend").first()

        # Get existing technologies
        python = Technology.query.filter_by(name="Python").first()
        javascript = Technology.query.filter_by(name="JavaScript").first()
        tailwindcss = Technology.query.filter_by(name="TailwindCSS").first()
        html = Technology.query.filter_by(name="HTML").first()

        # Create new technologies only if they don't exist
        ai_technologies = []
        
        react = Technology.query.filter_by(name="React").first()
        if not react:
            react = Technology(
                name="React",
                description="Frontend framework",
                type_id=framework_type.id
            )
            ai_technologies.append(react)

        tensorflow = Technology.query.filter_by(name="TensorFlow").first()
        if not tensorflow:
            tensorflow = Technology(
                name="TensorFlow",
                description="Machine learning framework",
                type_id=framework_type.id
            )
            ai_technologies.append(tensorflow)

        material_ui = Technology.query.filter_by(name="Material UI").first()
        if not material_ui:
            material_ui = Technology(
                name="Material UI",
                description="UI component library",
                type_id=frontend_type.id
            )
            ai_technologies.append(material_ui)

        if ai_technologies:
            db.session.add_all(ai_technologies)
            db.session.commit()

        # Create AI Chat App Idea
        ai_chat_idea = Idea(
            title="AI Chat Application",
            description="""An innovative AI-powered chat application that provides intelligent responses, 
            learns from conversations, and offers personalized experiences. The application will use 
            advanced natural language processing and machine learning techniques to understand context, 
            emotion, and user preferences.""",
            status_id=in_progress_status.id
        )
        db.session.add(ai_chat_idea)
        db.session.commit()

        # Create Tech Stack for AI Chat
        ai_technologies = [
            python,
            react,
            tensorflow,
            material_ui
        ]
        db.session.add_all(ai_technologies)
        db.session.commit()

        # Create technology versions
        python_versions = [
            TechnologyVersion(
                technology_id=python.id,  # Python
                version="3.11",
                release_date=datetime(2022, 10, 24).date(),
                end_of_life_date=datetime(2027, 10, 24).date(),
                is_default=True
            ),
            TechnologyVersion(
                technology_id=python.id,  # Python
                version="3.12",
                release_date=datetime(2023, 10, 2).date(),
                end_of_life_date=datetime(2028, 10, 2).date(),
                is_default=False
            )
        ]

        react_versions = [
            TechnologyVersion(
                technology_id=react.id,  # React
                version="18.2.0",
                release_date=datetime(2022, 6, 14).date(),
                end_of_life_date=None,
                is_default=True
            ),
            TechnologyVersion(
                technology_id=react.id,  # React
                version="18.3.0",
                release_date=datetime(2024, 5, 1).date(),
                end_of_life_date=None,
                is_default=False
            )
        ]

        tensorflow_versions = [
            TechnologyVersion(
                technology_id=tensorflow.id,  # TensorFlow
                version="2.15.0",
                release_date=datetime(2023, 11, 1).date(),
                end_of_life_date=None,
                is_default=True
            ),
            TechnologyVersion(
                technology_id=tensorflow.id,  # TensorFlow
                version="3.0.0",
                release_date=datetime(2024, 6, 1).date(),
                end_of_life_date=None,
                is_default=False
            )
        ]

        mui_versions = [
            TechnologyVersion(
                technology_id=material_ui.id,  # Material UI
                version="5.15.0",
                release_date=datetime(2023, 12, 1).date(),
                end_of_life_date=None,
                is_default=True
            ),
            TechnologyVersion(
                technology_id=material_ui.id,  # Material UI
                version="6.0.0",
                release_date=datetime(2024, 3, 1).date(),
                end_of_life_date=None,
                is_default=False
            )
        ]

        all_versions = python_versions + react_versions + tensorflow_versions + mui_versions
        db.session.add_all(all_versions)
        db.session.commit()

        # Create version aggregates
        version_aggregates = []
        for version in all_versions:
            if version.is_default:  # Only add default versions to the tech stack
                aggregate = TechnologyVersionAggregate(
                    technology_id=version.technology_id,
                    version_id=version.id
                )
                version_aggregates.append(aggregate)
        db.session.add_all(version_aggregates)
        db.session.commit()

        # Create AI tech stack
        ai_tech_stack = TechStack(
            name="AI Chat Tech Stack",
            description="Modern tech stack for AI-powered chat application",
            type_id=framework_type.id
        )
        
        # Add technologies and their default versions to the stack
        for tech in ai_technologies:
            ai_tech_stack.technologies.append(tech)
        
        for aggregate in version_aggregates:
            ai_tech_stack.technology_versions.append(aggregate)
            
        db.session.add(ai_tech_stack)
        db.session.commit()

        # Create Evolution Cycles
        development_cycle = EvolutionCycle(
            name="Development Phases",
            description="Main development phases of the AI Chat App",
            status_id=in_progress_status.id
        )
        feature_cycle = EvolutionCycle(
            name="Feature Releases",
            description="Feature release cycles",
            status_id=new_status.id
        )
        db.session.add_all([development_cycle, feature_cycle])
        db.session.commit()

        # Create IdeaEvolutionCycles
        idea_dev = IdeaEvolutionCycle(
            idea_id=ai_chat_idea.id,
            evolution_cycle_id=development_cycle.id,
            status_id=in_progress_status.id
        )
        idea_feature = IdeaEvolutionCycle(
            idea_id=ai_chat_idea.id,
            evolution_cycle_id=feature_cycle.id,
            status_id=new_status.id
        )
        db.session.add_all([idea_dev, idea_feature])
        db.session.commit()

        # Add tech stack to idea evolution cycles
        idea_dev.tech_stacks.append(ai_tech_stack)
        idea_feature.tech_stacks.append(ai_tech_stack)

        # Create Development Phases
        dev_phases = [
            Phase(
                name="Research & Planning",
                description="Research AI technologies and plan architecture",
                order=1,
                status_id=completed_status.id,
                evolution_cycle_id=development_cycle.id
            ),
            Phase(
                name="Core Development",
                description="Develop core AI chat functionality",
                order=2,
                status_id=in_progress_status.id,
                evolution_cycle_id=development_cycle.id
            ),
            Phase(
                name="Advanced Features",
                description="Implement advanced AI features",
                order=3,
                status_id=new_status.id,
                evolution_cycle_id=development_cycle.id
            ),
            Phase(
                name="Testing & Optimization",
                description="Testing and performance optimization",
                order=4,
                status_id=new_status.id,
                evolution_cycle_id=development_cycle.id
            )
        ]
        db.session.add_all(dev_phases)

        # Create Feature Phases
        feature_phases = [
            Phase(
                name="Basic Chat",
                description="Basic chat functionality with AI responses",
                order=1,
                status_id=in_progress_status.id,
                evolution_cycle_id=feature_cycle.id
            ),
            Phase(
                name="Context Awareness",
                description="Add context awareness to chat",
                order=2,
                status_id=new_status.id,
                evolution_cycle_id=feature_cycle.id
            ),
            Phase(
                name="Personalization",
                description="Add user personalization features",
                order=3,
                status_id=new_status.id,
                evolution_cycle_id=feature_cycle.id
            )
        ]
        db.session.add_all(feature_phases)
        db.session.commit()

        # Create IdeaEvolutionPhases for Development
        for phase in dev_phases:
            idea_phase = IdeaEvolutionPhase(
                idea_evolution_cycle_id=idea_dev.id,
                phase_id=phase.id,
                status_id=phase.status_id,
                order=phase.order
            )
            db.session.add(idea_phase)

        # Create IdeaEvolutionPhases for Features
        for phase in feature_phases:
            idea_phase = IdeaEvolutionPhase(
                idea_evolution_cycle_id=idea_feature.id,
                phase_id=phase.id,
                status_id=phase.status_id,
                order=phase.order
            )
            db.session.add(idea_phase)
        
        db.session.commit()

        # Get phases for requirements
        research_phase = IdeaEvolutionPhase.query.join(Phase).filter(Phase.name == "Research & Planning").first()
        core_dev_phase = IdeaEvolutionPhase.query.join(Phase).filter(Phase.name == "Core Development").first()
        basic_chat_phase = IdeaEvolutionPhase.query.join(Phase).filter(Phase.name == "Basic Chat").first()

        # Create Requirements for Research Phase
        research_requirements = [
            Requirement(
                name="AI Technology Selection",
                description="Research and select appropriate AI/ML technologies for chat functionality",
                status_id=completed_status.id,
                priority_id=must_have.id,
                type_id=technical.id,
                idea_evolution_phase_id=research_phase.id
            ),
            Requirement(
                name="Architecture Design",
                description="Design scalable system architecture for AI chat application",
                status_id=completed_status.id,
                priority_id=must_have.id,
                type_id=technical.id,
                idea_evolution_phase_id=research_phase.id
            ),
            Requirement(
                name="Market Research",
                description="Research competitor features and market demands",
                status_id=completed_status.id,
                priority_id=should_have.id,
                type_id=business.id,
                idea_evolution_phase_id=research_phase.id
            )
        ]
        db.session.add_all(research_requirements)

        # Create Requirements for Core Development Phase
        core_requirements = [
            Requirement(
                name="Chat Interface",
                description="Implement responsive chat interface with message history",
                status_id=in_progress_status.id,
                priority_id=must_have.id,
                type_id=functional.id,
                idea_evolution_phase_id=core_dev_phase.id
            ),
            Requirement(
                name="AI Integration",
                description="Integrate AI model for processing chat messages",
                status_id=new_status.id,
                priority_id=must_have.id,
                type_id=technical.id,
                idea_evolution_phase_id=core_dev_phase.id
            ),
            Requirement(
                name="Real-time Updates",
                description="Implement real-time message updates and notifications",
                status_id=new_status.id,
                priority_id=should_have.id,
                type_id=functional.id,
                idea_evolution_phase_id=core_dev_phase.id
            )
        ]
        db.session.add_all(core_requirements)

        # Create Requirements for Basic Chat Phase
        basic_chat_requirements = [
            Requirement(
                name="Message Sending",
                description="Allow users to send and receive messages",
                status_id=in_progress_status.id,
                priority_id=must_have.id,
                type_id=functional.id,
                idea_evolution_phase_id=basic_chat_phase.id
            ),
            Requirement(
                name="Response Generation",
                description="Generate appropriate AI responses to user messages",
                status_id=new_status.id,
                priority_id=must_have.id,
                type_id=functional.id,
                idea_evolution_phase_id=basic_chat_phase.id
            ),
            Requirement(
                name="Error Handling",
                description="Implement robust error handling for chat functionality",
                status_id=new_status.id,
                priority_id=should_have.id,
                type_id=non_functional.id,
                idea_evolution_phase_id=basic_chat_phase.id
            )
        ]
        db.session.add_all(basic_chat_requirements)
        db.session.commit()

if __name__ == "__main__":
    seed_sample_data()
