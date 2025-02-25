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

        # Create technology versions
        versions_data = {
            'Python': [
                ('3.11', datetime(2022, 10, 24), datetime(2027, 10, 24), True),
                ('3.12', datetime(2023, 10, 2), datetime(2028, 10, 2), False)
            ],
            'React': [
                ('18.2.0', datetime(2022, 6, 14), None, True),
                ('18.3.0', datetime(2024, 5, 1), None, False)
            ],
            'TensorFlow': [
                ('2.15.0', datetime(2023, 11, 1), None, True),
                ('3.0.0', datetime(2024, 6, 1), None, False)
            ],
            'Material UI': [
                ('5.15.0', datetime(2023, 12, 1), None, True),
                ('6.0.0', datetime(2024, 3, 1), None, False)
            ],
            'JavaScript': [
                ('ES2022', datetime(2022, 6, 1), None, True),
                ('ES2023', datetime(2023, 6, 1), None, False)
            ]
        }

        tech_versions = []
        version_aggregates = []

        for tech_name, versions in versions_data.items():
            tech = Technology.query.filter_by(name=tech_name).first()
            if tech:
                for version_info in versions:
                    version = TechnologyVersion(
                        technology_id=tech.id,
                        version=version_info[0],
                        release_date=version_info[1].date(),
                        end_of_life_date=version_info[2].date() if version_info[2] else None,
                        is_default=version_info[3]
                    )
                    tech_versions.append(version)

        db.session.add_all(tech_versions)
        db.session.commit()

        # Create version aggregates for default versions
        for version in tech_versions:
            if version.is_default:
                aggregate = TechnologyVersionAggregate(
                    technology_id=version.technology_id,
                    version_id=version.id
                )
                version_aggregates.append(aggregate)

        db.session.add_all(version_aggregates)
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

        # Create tech stacks for different components
        frontend_stack = TechStack(
            name="React Frontend",
            description="Modern frontend with React and Material UI",
            type_id=framework_type.id
        )
        db.session.add(frontend_stack)
        db.session.commit()
        
        frontend_stack.technologies.extend([react, javascript, material_ui])
        
        # Add default version aggregates to frontend stack
        frontend_versions = [agg for agg in version_aggregates 
                           if agg.technology in [react, javascript, material_ui]]
        frontend_stack.technology_versions.extend(frontend_versions)
        
        backend_stack = TechStack(
            name="Python Backend",
            description="AI-powered backend with Python and TensorFlow",
            type_id=framework_type.id
        )
        db.session.add(backend_stack)
        db.session.commit()
        
        backend_stack.technologies.extend([python, tensorflow])
        
        # Add default version aggregates to backend stack
        backend_versions = [agg for agg in version_aggregates 
                          if agg.technology in [python, tensorflow]]
        backend_stack.technology_versions.extend(backend_versions)
        
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

        # Create phases for AI Chat App
        phases_data = [
            {
                "name": "Frontend Development",
                "description": "Implement the user interface and chat components",
                "order": 1,
                "status": in_progress_status,
                "tech_stacks": [frontend_stack]
            },
            {
                "name": "Backend Development",
                "description": "Implement the AI chat engine and API",
                "order": 2,
                "status": new_status,
                "tech_stacks": [backend_stack]
            },
            {
                "name": "Integration",
                "description": "Connect frontend and backend components",
                "order": 3,
                "status": new_status,
                "tech_stacks": [frontend_stack, backend_stack]
            }
        ]
        
        # Create phases and associate tech stacks
        for phase_data in phases_data:
            phase = Phase(
                name=phase_data["name"],
                description=phase_data["description"],
                order=phase_data["order"],
                evolution_cycle_id=development_cycle.id
            )
            db.session.add(phase)
            db.session.commit()
            
            idea_phase = IdeaEvolutionPhase(
                idea_evolution_cycle_id=idea_dev.id,
                phase_id=phase.id,
                status_id=phase_data["status"].id,
                order=phase_data["order"]
            )
            idea_phase.tech_stacks.extend(phase_data["tech_stacks"])
            db.session.add(idea_phase)
        
        db.session.commit()

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
