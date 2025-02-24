from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime
import os
from models.core import (
    db, Status, Idea, EvolutionCycle, IdeaEvolutionCycle, Phase,
    IdeaEvolutionPhase, Requirement, RequirementType, RequirementPriority,
    TechnologyType, Technology, TechStack, TechnologyVersion, TechnologyVersionAggregate,
    tech_stack_technology_version
)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Import db and models after creating app
    from extensions import db
    from models.core import Idea, EvolutionCycle, Phase, Requirement, RequirementType, RequirementPriority, Status, TechStack, Technology, IdeaEvolutionCycle, IdeaEvolutionPhase, TechnologyType, TechnologyVersion

    # Initialize SQLAlchemy and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    # Create all database tables
    with app.app_context():
        db.create_all()

    # Add template context processor
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return {'now': datetime.now()}

    # Helper function for counting relationships
    def count_relationship(relationship):
        """Safely count a SQLAlchemy relationship whether it's a query or list."""
        try:
            # Try to use SQLAlchemy query count
            return relationship.count()
        except (AttributeError, TypeError):
            # If it's a list or similar, use len()
            return len(relationship)

    # Register blueprints (to be added later)

    @app.route('/')
    def index():
        # Get counts for dashboard
        ideas_count = Idea.query.count()
        requirements_count = Requirement.query.count()
        evolutions_count = EvolutionCycle.query.count()
        techstacks_count = TechStack.query.count()
        phases_count = Phase.query.count()
        technologies_count = Technology.query.count()

        # Get recent activities (last 5 items of each type)
        recent_ideas = Idea.query.order_by(Idea.created_at.desc()).limit(5).all()
        recent_requirements = Requirement.query.order_by(Requirement.created_at.desc()).limit(5).all()

        # Combine and sort activities
        activities = []

        # Add ideas
        for idea in recent_ideas:
            activities.append({
                'type': 'idea',
                'description': f'New idea created: {idea.name}',
                'created_at': idea.created_at or datetime.utcnow()
            })

        # Add requirements
        for req in recent_requirements:
            activities.append({
                'type': 'requirement',
                'description': f'New requirement added: {req.name}',
                'created_at': req.created_at or datetime.utcnow()
            })

        # Sort activities by creation date
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        activities = activities[:5]  # Get only the 5 most recent activities

        return render_template('index.html',
                             ideas_count=ideas_count,
                             requirements_count=requirements_count,
                             evolutions_count=evolutions_count,
                             techstacks_count=techstacks_count,
                             phases_count=phases_count,
                             technologies_count=technologies_count,
                             activities=activities)

    @app.route('/ideas')
    def ideas():
        ideas = Idea.query.all()
        return render_template('ideas/index.html', ideas=ideas)

    @app.route('/ideas/create', methods=['GET', 'POST'])
    def ideas_create():
        if request.method == 'POST':
            # Get default status (e.g., "New" or "Draft")
            default_status = Status.query.filter_by(name='New').first()
            if not default_status:
                default_status = Status(name='New')
                db.session.add(default_status)
                db.session.commit()

            # Create new idea
            name = request.form.get('name')
            description = request.form.get('description')

            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('ideas_create'))

            idea = Idea(
                name=name,
                description=description,
                status=default_status
            )

            # Handle tech stacks
            tech_stack_ids = request.form.getlist('tech_stack')
            if tech_stack_ids:
                tech_stacks = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all()
                idea.tech_stacks.extend(tech_stacks)

            try:
                db.session.add(idea)
                db.session.commit()
                flash('Idea created successfully!', 'success')
                return redirect(url_for('ideas'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating idea. Please try again.', 'danger')
                return redirect(url_for('ideas_create'))

        # GET request - show create form
        tech_stacks = TechStack.query.all()
        return render_template('ideas/create.html', tech_stacks=tech_stacks)

    @app.route('/ideas/<int:id>')
    def ideas_show(id):
        idea = Idea.query.get_or_404(id)
        return render_template('ideas/show.html', idea=idea)

    @app.route('/ideas/<int:id>/edit', methods=['GET', 'POST'])
    def ideas_edit(id):
        idea = Idea.query.get_or_404(id)
        if request.method == 'POST':
            idea.name = request.form['name']
            idea.description = request.form['description']
            # Update tech stack
            tech_stack_ids = request.form.getlist('tech_stack')
            idea.tech_stack = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all()
            db.session.commit()
            flash('Idea updated successfully!', 'success')
            return redirect(url_for('ideas_show', id=idea.id))
        technologies = TechStack.query.all()
        return render_template('ideas/edit.html', idea=idea, technologies=technologies)

    @app.route('/ideas/<int:id>/delete', methods=['POST'])
    def ideas_delete(id):
        idea = Idea.query.get_or_404(id)
        db.session.delete(idea)
        db.session.commit()
        flash('Idea deleted successfully!', 'success')
        return redirect(url_for('ideas'))

    # Evolution Cycle routes
    @app.route('/evolutions')
    def evolutions():
        cycles = EvolutionCycle.query.all()
        return render_template('evolutions/index.html', cycles=cycles)

    @app.route('/evolutions/create', methods=['GET', 'POST'])
    def evolutions_create():
        if request.method == 'POST':
            # Get default status
            default_status = Status.query.filter_by(name='New').first()
            if not default_status:
                default_status = Status(name='New')
                db.session.add(default_status)
                db.session.commit()

            # Create new evolution cycle
            name = request.form.get('name')
            description = request.form.get('description')
            idea_id = request.form.get('idea_id')

            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('evolutions_create'))

            try:
                # Create evolution cycle
                cycle = EvolutionCycle(
                    name=name,
                    description=description,
                    status=default_status
                )
                db.session.add(cycle)
                db.session.commit()

                # If idea_id is provided, create IdeaEvolutionCycle
                if idea_id:
                    idea = Idea.query.get(idea_id)
                    if not idea:
                        flash('Selected idea not found.', 'danger')
                        return redirect(url_for('evolutions_create'))
                    
                    idea_cycle = IdeaEvolutionCycle(
                        idea=idea,
                        evolution_cycle=cycle,
                        status=default_status
                    )
                    db.session.add(idea_cycle)

                    # Handle phases
                    phase_ids = request.form.getlist('phases')
                    if phase_ids:
                        phases = Phase.query.filter(Phase.id.in_(phase_ids)).all()
                        for order, phase in enumerate(phases, 1):
                            idea_phase = IdeaEvolutionPhase(
                                idea_evolution_cycle=idea_cycle,
                                phase=phase,
                                order=order,
                                status=default_status
                            )
                            db.session.add(idea_phase)

                    db.session.commit()
                    flash('Evolution cycle created and linked to idea successfully!', 'success')
                    return redirect(url_for('ideas_show', id=idea.id))
                
                flash('Evolution cycle template created successfully!', 'success')
                return redirect(url_for('evolutions'))

            except Exception as e:
                db.session.rollback()
                flash('Error creating evolution cycle. Please try again.', 'danger')
                return redirect(url_for('evolutions_create'))

        # GET request - show create form
        idea_id = request.args.get('idea_id')
        selected_idea = None
        if idea_id:
            selected_idea = Idea.query.get(idea_id)

        ideas = Idea.query.all()
        phases = Phase.query.all()
        return render_template('evolutions/create.html',
                             ideas=ideas,
                             phases=phases,
                             selected_idea=selected_idea)

    @app.route('/evolutions/<int:id>')
    def evolutions_show(id):
        cycle = EvolutionCycle.query.get_or_404(id)
        return render_template('evolutions/show.html', cycle=cycle)

    @app.route('/evolutions/link/<int:idea_id>', methods=['GET', 'POST'])
    def evolutions_link(idea_id):
        idea = Idea.query.get_or_404(idea_id)

        if request.method == 'POST':
            evolution_id = request.form.get('evolution_id')
            if not evolution_id:
                flash('Please select an evolution cycle.', 'danger')
                return redirect(url_for('evolutions_link', idea_id=idea.id))

            try:
                evolution = EvolutionCycle.query.get(evolution_id)
                if not evolution:
                    flash('Selected evolution cycle not found.', 'danger')
                    return redirect(url_for('evolutions_link', idea_id=idea.id))

                # Get default status
                default_status = Status.query.filter_by(name='New').first()
                if not default_status:
                    default_status = Status(name='New')
                    db.session.add(default_status)
                    db.session.commit()

                # Create IdeaEvolutionCycle
                idea_cycle = IdeaEvolutionCycle(
                    idea=idea,
                    evolution_cycle=evolution,
                    status=default_status
                )
                db.session.add(idea_cycle)

                # Create IdeaEvolutionPhase entries for each phase
                phase_ids = request.form.getlist('phases')
                if phase_ids:
                    phases = Phase.query.filter(Phase.id.in_(phase_ids)).all()
                    for order, phase in enumerate(phases, 1):
                        idea_phase = IdeaEvolutionPhase(
                            idea_evolution_cycle=idea_cycle,
                            phase=phase,
                            order=order,
                            status=default_status
                        )
                        db.session.add(idea_phase)

                db.session.commit()
                flash('Evolution cycle linked successfully!', 'success')
                return redirect(url_for('ideas_show', id=idea.id))

            except Exception as e:
                db.session.rollback()
                flash('Error linking evolution cycle. Please try again.', 'danger')
                return redirect(url_for('evolutions_link', idea_id=idea.id))

        # GET request - show link form
        # Get all evolution cycles that aren't already linked to this idea
        available_cycles = EvolutionCycle.query.filter(
            ~EvolutionCycle.id.in_(
                db.session.query(IdeaEvolutionCycle.evolution_cycle_id)
                .filter(IdeaEvolutionCycle.idea_id == idea.id)
            )
        ).all()
        phases = Phase.query.all()

        return render_template('evolutions/link.html',
                             idea=idea,
                             available_cycles=available_cycles,
                             phases=phases)

    @app.route('/evolutions/<int:id>/edit', methods=['GET', 'POST'])
    def evolutions_edit(id):
        cycle = EvolutionCycle.query.get_or_404(id)
        
        if request.method == 'POST':
            try:
                cycle.name = request.form.get('name')
                cycle.description = request.form.get('description')
                
                # Update phases for all idea evolution cycles using this template
                idea_cycles = IdeaEvolutionCycle.query.filter_by(evolution_cycle_id=cycle.id).all()
                phase_ids = request.form.getlist('phases')
                phases = Phase.query.filter(Phase.id.in_(phase_ids)).all() if phase_ids else []
                
                # Get default status for new phases
                default_status = Status.query.filter_by(name='New').first()
                if not default_status:
                    default_status = Status(name='New')
                    db.session.add(default_status)
                    db.session.commit()
                
                # Update phases for each idea evolution cycle
                for idea_cycle in idea_cycles:
                    # Delete phases that are no longer selected
                    IdeaEvolutionPhase.query.filter(
                        IdeaEvolutionPhase.idea_evolution_cycle_id == idea_cycle.id,
                        ~IdeaEvolutionPhase.phase_id.in_([p.id for p in phases])
                    ).delete(synchronize_session=False)
                    
                    # Get existing phases to preserve their status
                    existing_phases = {
                        p.phase_id: p.status_id 
                        for p in IdeaEvolutionPhase.query.filter_by(idea_evolution_cycle_id=idea_cycle.id).all()
                    }
                    
                    # Add or update phases in the new order
                    for order, phase in enumerate(phases, 1):
                        idea_phase = IdeaEvolutionPhase.query.filter_by(
                            idea_evolution_cycle_id=idea_cycle.id,
                            phase_id=phase.id
                        ).first()
                        
                        if idea_phase:
                            # Update existing phase order
                            idea_phase.order = order
                        else:
                            # Create new phase with default status
                            idea_phase = IdeaEvolutionPhase(
                                idea_evolution_cycle=idea_cycle,
                                phase=phase,
                                order=order,
                                status_id=existing_phases.get(phase.id, default_status.id)
                            )
                            db.session.add(idea_phase)
                
                db.session.commit()
                flash('Evolution cycle updated successfully!', 'success')
                return redirect(url_for('evolutions_show', id=cycle.id))
                
            except Exception as e:
                db.session.rollback()
                flash('Error updating evolution cycle. Please try again.', 'danger')
                return redirect(url_for('evolutions_edit', id=cycle.id))

        # GET request - show edit form
        phases = Phase.query.all()
        cycle_phase_ids = {p.phase_id for c in cycle.ideas for p in c.phases}
        
        return render_template('evolutions/edit.html',
                             cycle=cycle,
                             phases=phases,
                             cycle_phase_ids=cycle_phase_ids)

    @app.route('/evolutions/<int:id>/delete', methods=['POST'])
    def evolutions_delete(id):
        cycle = EvolutionCycle.query.get_or_404(id)
        
        # Delete all associated IdeaEvolutionPhases and their requirements first
        idea_cycles = IdeaEvolutionCycle.query.filter_by(evolution_cycle_id=cycle.id).all()
        for idea_cycle in idea_cycles:
            idea_phases = IdeaEvolutionPhase.query.filter_by(idea_evolution_cycle_id=idea_cycle.id).all()
            for idea_phase in idea_phases:
                # Delete associated requirements
                Requirement.query.filter_by(idea_evolution_phase_id=idea_phase.id).delete()
                db.session.delete(idea_phase)
            db.session.delete(idea_cycle)
        
        db.session.delete(cycle)
        db.session.commit()
        flash('Evolution cycle and all associated data deleted successfully!', 'success')
        return redirect(url_for('evolutions'))

    @app.route('/evolutions/<int:id>/techstacks/add', methods=['GET', 'POST'])
    def evolutions_add_techstack(id):
        idea_cycle = IdeaEvolutionCycle.query.get_or_404(id)
        
        if request.method == 'POST':
            # Get selected tech stacks
            tech_stack_ids = request.form.getlist('tech_stacks')
            tech_stacks = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all()
            
            # Add tech stacks to the evolution cycle
            for stack in tech_stacks:
                if stack not in idea_cycle.tech_stacks:
                    idea_cycle.tech_stacks.append(stack)
            
            db.session.commit()
            flash('Tech stacks added successfully!', 'success')
            return redirect(url_for('evolutions_show', id=idea_cycle.evolution_cycle.id))
        
        # Get all available tech stacks that aren't already linked
        available_stacks = TechStack.query\
            .filter(~TechStack.id.in_(
                db.session.query(tech_stack_association.c.tech_stack_id)\
                .filter_by(idea_evolution_cycle_id=id)
            ))\
            .all()
        
        return render_template('evolutions/add_techstack.html',
                             idea_cycle=idea_cycle,
                             available_stacks=available_stacks)

    @app.route('/evolutions/<int:id>/techstacks/<int:stack_id>/remove', methods=['POST'])
    def evolutions_remove_techstack(id, stack_id):
        idea_cycle = IdeaEvolutionCycle.query.get_or_404(id)
        tech_stack = TechStack.query.get_or_404(stack_id)
        
        if tech_stack in idea_cycle.tech_stacks:
            idea_cycle.tech_stacks.remove(tech_stack)
            db.session.commit()
            flash('Tech stack removed successfully!', 'success')
        
        return redirect(url_for('evolutions_show', id=idea_cycle.evolution_cycle.id))

    # Requirements routes
    @app.route('/requirements')
    def requirements():
        requirements = Requirement.query.all()
        return render_template('requirements/index.html', requirements=requirements)

    @app.route('/requirements/create', methods=['GET', 'POST'])
    def requirements_create():
        if request.method == 'POST':
            # Get required IDs
            idea_evolution_phase_id = request.form.get('idea_evolution_phase_id')
            type_id = request.form.get('type_id')
            priority_id = request.form.get('priority_id')

            if not idea_evolution_phase_id:
                flash('Please select a phase from an evolution cycle.', 'danger')
                return redirect(url_for('requirements_create'))

            # Get default status
            default_status = Status.query.filter_by(name='New').first()
            if not default_status:
                default_status = Status(name='New')
                db.session.add(default_status)
                db.session.commit()

            # Create new requirement
            requirement = Requirement(
                name=request.form.get('name'),
                description=request.form.get('description'),
                idea_evolution_phase_id=idea_evolution_phase_id,
                status=default_status
            )

            # Set type if provided
            if type_id:
                requirement.type = RequirementType.query.get(type_id)
            
            # Set priority if provided
            if priority_id:
                requirement.priority = RequirementPriority.query.get(priority_id)

            try:
                db.session.add(requirement)
                db.session.commit()
                flash('Requirement created successfully!', 'success')
                
                # Redirect to the phase view
                idea_phase = IdeaEvolutionPhase.query.get(idea_evolution_phase_id)
                return redirect(url_for('phases_show', id=idea_phase.phase.id))
            except Exception as e:
                db.session.rollback()
                flash('Error creating requirement. Please try again.', 'danger')
                return redirect(url_for('requirements_create'))

        # GET request - show create form
        # Get all available phases from all evolution cycles
        idea_evolution_phases = IdeaEvolutionPhase.query\
            .select_from(IdeaEvolutionPhase)\
            .join(IdeaEvolutionPhase.idea_evolution_cycle)\
            .join(IdeaEvolutionCycle.idea)\
            .join(IdeaEvolutionPhase.phase)\
            .add_columns(
                Idea.name.label('idea_name'),
                EvolutionCycle.name.label('cycle_name'),
                Phase.name.label('phase_name')
            ).all()

        types = RequirementType.query.all()
        priorities = RequirementPriority.query.all()
        
        return render_template('requirements/create.html',
                             idea_evolution_phases=idea_evolution_phases,
                             types=types,
                             priorities=priorities)

    @app.route('/requirements/<int:id>')
    def requirements_show(id):
        requirement = Requirement.query.get_or_404(id)
        return render_template('requirements/show.html', requirement=requirement)

    @app.route('/requirements/<int:id>/edit', methods=['GET', 'POST'])
    def requirements_edit(id):
        requirement = Requirement.query.get_or_404(id)
        if request.method == 'POST':
            requirement.name = request.form.get('name')
            requirement.description = request.form.get('description')
            
            # Update type if provided
            type_id = request.form.get('type_id')
            if type_id:
                requirement.type = RequirementType.query.get(type_id)
            
            # Update priority if provided
            priority_id = request.form.get('priority_id')
            if priority_id:
                requirement.priority = RequirementPriority.query.get(priority_id)
            
            # Update phase if provided
            idea_evolution_phase_id = request.form.get('idea_evolution_phase_id')
            if idea_evolution_phase_id:
                requirement.idea_evolution_phase_id = idea_evolution_phase_id

            try:
                db.session.commit()
                flash('Requirement updated successfully!', 'success')
                return redirect(url_for('requirements_show', id=requirement.id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating requirement. Please try again.', 'danger')
                return redirect(url_for('requirements_edit', id=requirement.id))

        # Get all available phases from all evolution cycles
        idea_evolution_phases = IdeaEvolutionPhase.query\
            .join(IdeaEvolutionPhase.idea_evolution_cycle)\
            .join(IdeaEvolutionCycle.idea)\
            .join(IdeaEvolutionPhase.phase)\
            .add_columns(
                Idea.name.label('idea_name'),
                EvolutionCycle.name.label('cycle_name'),
                Phase.name.label('phase_name')
            ).all()

        types = RequirementType.query.all()
        priorities = RequirementPriority.query.all()
        
        return render_template('requirements/edit.html',
                             requirement=requirement,
                             idea_evolution_phases=idea_evolution_phases,
                             types=types,
                             priorities=priorities)

    @app.route('/requirements/<int:id>/delete', methods=['POST'])
    def requirements_delete(id):
        requirement = Requirement.query.get_or_404(id)
        idea_phase = requirement.idea_evolution_phase
        db.session.delete(requirement)
        db.session.commit()
        flash('Requirement deleted successfully!', 'success')
        return redirect(url_for('phases_show', id=idea_phase.phase.id))

    # Phases routes
    @app.route('/phases')
    def phases():
        phases = Phase.query.all()
        return render_template('phases/index.html', phases=phases)

    @app.route('/phases/create', methods=['GET', 'POST'])
    def phases_create():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')

            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('phases_create'))

            # Get default status
            default_status = Status.query.filter_by(name='New').first()
            if not default_status:
                default_status = Status(name='New')
                db.session.add(default_status)
                db.session.commit()

            try:
                phase = Phase(
                    name=name,
                    description=description,
                    status=default_status
                )
                db.session.add(phase)
                db.session.commit()
                flash('Phase created successfully!', 'success')
                return redirect(url_for('phases'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating phase. Please try again.', 'danger')
                return redirect(url_for('phases_create'))

        return render_template('phases/create.html')

    @app.route('/phases/<int:id>')
    def phases_show(id):
        phase = Phase.query.get_or_404(id)
        
        # Get all evolution cycles using this phase
        idea_evolution_phases = IdeaEvolutionPhase.query\
            .select_from(IdeaEvolutionPhase)\
            .join(IdeaEvolutionCycle, IdeaEvolutionPhase.idea_evolution_cycle_id == IdeaEvolutionCycle.id)\
            .join(Idea, IdeaEvolutionCycle.idea_id == Idea.id)\
            .join(EvolutionCycle, IdeaEvolutionCycle.evolution_cycle_id == EvolutionCycle.id)\
            .join(Phase, IdeaEvolutionPhase.phase_id == Phase.id)\
            .filter(IdeaEvolutionPhase.phase_id == id)\
            .add_columns(
                Idea.id.label('idea_id'),
                Idea.name.label('idea_name'),
                EvolutionCycle.name.label('cycle_name'),
                Phase.name.label('phase_name'),
                IdeaEvolutionPhase.order.label('phase_order'),
                IdeaEvolutionPhase.status_id.label('status_id')
            )\
            .order_by(Idea.name, EvolutionCycle.name, IdeaEvolutionPhase.order)\
            .all()

        return render_template('phases/show.html', 
                             phase=phase,
                             idea_evolution_phases=idea_evolution_phases)

    @app.route('/phases/<int:id>/edit', methods=['GET', 'POST'])
    def phases_edit(id):
        phase = Phase.query.get_or_404(id)
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')

            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('phases_edit', id=id))

            try:
                phase.name = name
                phase.description = description
                db.session.commit()
                flash('Phase updated successfully!', 'success')
                return redirect(url_for('phases_show', id=phase.id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating phase. Please try again.', 'danger')
                return redirect(url_for('phases_edit', id=id))

        return render_template('phases/edit.html', phase=phase)

    @app.route('/phases/<int:id>/delete', methods=['POST'])
    def phases_delete(id):
        phase = Phase.query.get_or_404(id)
        
        # Delete all associated IdeaEvolutionPhases and their requirements first
        idea_phases = IdeaEvolutionPhase.query.filter_by(phase_id=id).all()
        for idea_phase in idea_phases:
            # Delete associated requirements
            Requirement.query.filter_by(idea_evolution_phase_id=idea_phase.id).delete()
            db.session.delete(idea_phase)
        
        db.session.delete(phase)
        db.session.commit()
        flash('Phase and all associated data deleted successfully!', 'success')
        return redirect(url_for('phases'))

    # Technology routes
    @app.route('/technologies')
    def technologies():
        technologies = Technology.query.all()
        # Pre-calculate counts for each technology
        for tech in technologies:
            # Count unique tech stacks through version aggregates
            tech.tech_stack_count = db.session.query(TechStack)\
                .join(tech_stack_technology_version)\
                .join(TechnologyVersionAggregate)\
                .filter(TechnologyVersionAggregate.technology_id == tech.id)\
                .distinct()\
                .count()
        return render_template('technologies/index.html', technologies=technologies)

    @app.route('/technologies/create', methods=['GET', 'POST'])
    def technologies_create():
        technology_types = TechnologyType.query.all()
        print(f"Found {len(technology_types)} technology types")  # Debug log
        if request.method == 'POST':
            # Check if technology with same name and type already exists
            existing_tech = Technology.query.filter_by(
                name=request.form['name'],
                type_id=request.form['type_id']
            ).first()
            
            if existing_tech:
                flash(f'A technology named "{request.form["name"]}" already exists for this type.', 'error')
                return render_template('technologies/create.html', technology_types=technology_types)
            
            technology = Technology(
                name=request.form['name'],
                description=request.form['description'],
                type_id=request.form['type_id']
            )
            try:
                db.session.add(technology)
                db.session.commit()
                flash('Technology created successfully! You can now add versions.', 'success')
                return redirect(url_for('add_technology_version', id=technology.id))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while creating the technology.', 'error')
                return render_template('technologies/create.html', technology_types=technology_types)

        return render_template('technologies/create.html', technology_types=technology_types)

    @app.route('/technologies/<int:id>/add-version', methods=['GET', 'POST'])
    def add_technology_version(id):
        technology = Technology.query.get_or_404(id)
        if request.method == 'POST':
            version = TechnologyVersion(
                technology=technology,
                version=request.form['version'],
                release_date=datetime.strptime(request.form['release_date'], '%Y-%m-%d').date() if request.form['release_date'] else None,
                end_of_life_date=datetime.strptime(request.form['end_of_life_date'], '%Y-%m-%d').date() if request.form['end_of_life_date'] else None,
                is_default=bool(request.form.get('is_default', False))
            )
            db.session.add(version)
            db.session.commit()
            flash('Version added successfully!', 'success')
            return redirect(url_for('technologies_show', id=technology.id))

        return render_template('technologies/add_version.html', technology=technology)

    @app.route('/technologies/<int:id>')
    def technologies_show(id):
        technology = Technology.query.get_or_404(id)
        return render_template('technologies/show.html', technology=technology)

    @app.route('/technologies/<int:id>/edit', methods=['GET', 'POST'])
    def technologies_edit(id):
        technology = Technology.query.get_or_404(id)
        technology_types = TechnologyType.query.all()
        if request.method == 'POST':
            technology.name = request.form['name']
            technology.description = request.form['description']
            technology.type_id = request.form['type_id']
            db.session.commit()
            flash('Technology updated successfully!', 'success')
            return redirect(url_for('technologies_show', id=technology.id))

        return render_template('technologies/edit.html', technology=technology, technology_types=technology_types)

    @app.route('/technologies/<int:id>/delete', methods=['POST'])
    def technologies_delete(id):
        technology = Technology.query.get_or_404(id)
        db.session.delete(technology)
        db.session.commit()
        flash('Technology deleted successfully!', 'success')
        return redirect(url_for('technologies'))

    @app.route('/technologies/<int:id>/versions', methods=['GET', 'POST'])
    def technology_versions(id):
        technology = Technology.query.get_or_404(id)
        if request.method == 'POST':
            version_id = request.form.get('version_id')
            if version_id:
                version = TechnologyVersion.query.get_or_404(version_id)
                # Create the association
                aggregate = TechnologyVersionAggregate(
                    technology=technology,
                    version=version
                )
                try:
                    db.session.add(aggregate)
                    db.session.commit()
                    flash('Version associated successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error associating version. This association might already exist.', 'danger')
            else:
                flash('Please select a version to associate.', 'warning')
            
            return redirect(url_for('technology_versions', id=id))

        # Get all versions that are not yet associated with this technology
        existing_version_ids = [va.version_id for va in technology.version_aggregates]
        available_versions = TechnologyVersion.query.filter(
            ~TechnologyVersion.id.in_(existing_version_ids) if existing_version_ids else True
        ).all()

        return render_template(
            'technologies/versions.html',
            technology=technology,
            available_versions=available_versions
        )

    @app.route('/technologies/<int:tech_id>/versions/<int:version_id>/remove', methods=['POST'])
    def technology_version_remove(tech_id, version_id):
        aggregate = TechnologyVersionAggregate.query.filter_by(
            technology_id=tech_id,
            version_id=version_id
        ).first_or_404()
        
        try:
            db.session.delete(aggregate)
            db.session.commit()
            flash('Version removed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error removing version.', 'danger')
        
        return redirect(url_for('technology_versions', id=tech_id))

    # Tech Stack routes
    @app.route('/techstacks')
    def techstacks():
        techstacks = TechStack.query.all()
        return render_template('techstacks/index.html', techstacks=techstacks)

    @app.route('/techstacks/<int:id>')
    def techstacks_show(id):
        stack = TechStack.query.get_or_404(id)
        return render_template('techstacks/show.html', stack=stack, now=datetime.now().date())

    @app.route('/techstacks/create', methods=['GET', 'POST'])
    def techstacks_create():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            type_id = request.form.get('type_id')

            if not name or not type_id:
                flash('Name and type are required.', 'danger')
                return redirect(url_for('techstacks_create'))

            try:
                # Create tech stack
                tech_stack = TechStack(
                    name=name,
                    description=description,
                    type_id=type_id
                )
                db.session.add(tech_stack)
                
                # Add technology versions
                selected_versions = request.form.getlist('technology_versions[]')
                for version_id in selected_versions:
                    if version_id:
                        version_aggregate = TechnologyVersionAggregate.query.get(version_id)
                        if version_aggregate:
                            tech_stack.technology_versions.append(version_aggregate)

                db.session.commit()
                flash('Tech Stack created successfully!', 'success')
                return redirect(url_for('techstacks'))

            except Exception as e:
                db.session.rollback()
                flash('Error creating tech stack. Please try again.', 'danger')
                return redirect(url_for('techstacks_create'))

        # GET request - show create form
        types = TechnologyType.query.order_by(TechnologyType.name).all()
        # Get all available technology versions
        technologies = Technology.query.all()
        return render_template('techstacks/create.html', 
                             types=types,
                             technologies=technologies)

    @app.route('/techstacks/<int:id>/edit', methods=['GET', 'POST'])
    def techstacks_edit(id):
        tech_stack = TechStack.query.get_or_404(id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            type_id = request.form.get('type_id')

            if not name or not type_id:
                flash('Name and type are required.', 'danger')
                return redirect(url_for('techstacks_edit', id=id))

            try:
                tech_stack.name = name
                tech_stack.description = description
                tech_stack.type_id = type_id

                # Update technology versions
                selected_versions = request.form.getlist('technology_versions[]')
                # Clear existing versions
                tech_stack.technology_versions = []
                # Add selected versions
                for version_id in selected_versions:
                    if version_id:
                        version_aggregate = TechnologyVersionAggregate.query.get(version_id)
                        if version_aggregate:
                            tech_stack.technology_versions.append(version_aggregate)

                db.session.commit()
                flash('Tech Stack updated successfully!', 'success')
                return redirect(url_for('techstacks_show', id=tech_stack.id))

            except Exception as e:
                db.session.rollback()
                flash('Error updating tech stack. Please try again.', 'danger')
                return redirect(url_for('techstacks_edit', id=id))

        # GET request - show edit form
        types = TechnologyType.query.order_by(TechnologyType.name).all()
        technologies = Technology.query.all()
        return render_template('techstacks/edit.html', 
                             tech_stack=tech_stack,
                             types=types,
                             technologies=technologies)

    @app.route('/techstacks/<int:id>/delete', methods=['POST'])
    def techstacks_delete(id):
        tech_stack = TechStack.query.get_or_404(id)
        db.session.delete(tech_stack)
        db.session.commit()
        flash('Tech Stack deleted successfully!', 'success')
        return redirect(url_for('techstacks'))

    # Technology Type routes
    @app.route('/technology-types')
    def technology_types():
        types = TechnologyType.query.order_by(TechnologyType.name).all()
        return render_template('technology_types/index.html', types=types)

    @app.route('/technology-types/create', methods=['GET', 'POST'])
    def technology_types_create():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')

            if not name:
                flash('Name is required.', 'danger')
                return redirect(url_for('technology_types_create'))

            try:
                tech_type = TechnologyType(name=name, description=description)
                db.session.add(tech_type)
                db.session.commit()
                flash('Technology type created successfully!', 'success')
                return redirect(url_for('technology_types'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating technology type. Please try again.', 'danger')
                return redirect(url_for('technology_types_create'))

        return render_template('technology_types/create.html')

    @app.route('/technology-types/<int:id>')
    def technology_types_show(id):
        tech_type = TechnologyType.query.get_or_404(id)
        return render_template('technology_types/show.html', type=tech_type)

    @app.route('/technology-types/<int:id>/edit', methods=['GET', 'POST'])
    def technology_types_edit(id):
        tech_type = TechnologyType.query.get_or_404(id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')

            if not name:
                flash('Name is required.', 'danger')
                return redirect(url_for('technology_types_edit', id=id))

            try:
                tech_type.name = name
                tech_type.description = description
                db.session.commit()
                flash('Technology type updated successfully!', 'success')
                return redirect(url_for('technology_types_show', id=tech_type.id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating technology type. Please try again.', 'danger')
                return redirect(url_for('technology_types_edit', id=id))

        return render_template('technology_types/edit.html', type=tech_type)

    @app.route('/technology-types/<int:id>/delete', methods=['POST'])
    def technology_types_delete(id):
        tech_type = TechnologyType.query.get_or_404(id)
        
        try:
            db.session.delete(tech_type)
            db.session.commit()
            flash('Technology type deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting technology type. Please try again.', 'danger')
        
        return redirect(url_for('technology_types'))

    # Control Panel routes
    @app.route('/ideas/<int:id>/control-panel')
    def idea_control_panel(id):
        idea = Idea.query.get_or_404(id)
        tech_stacks = TechStack.query.all()
        statuses = Status.query.all()
        requirement_types = RequirementType.query.all()
        
        # Get available phases for this idea's evolution cycles
        available_phases = IdeaEvolutionPhase.query\
            .join(IdeaEvolutionPhase.idea_evolution_cycle)\
            .join(IdeaEvolutionCycle.idea)\
            .join(IdeaEvolutionPhase.phase)\
            .filter(IdeaEvolutionCycle.idea_id == id)\
            .order_by(EvolutionCycle.name, IdeaEvolutionPhase.order)\
            .all()

        # Calculate statistics for this idea
        total_cycles = len(idea.evolution_cycles)
        completed_cycles = len([c for c in idea.evolution_cycles if c.status.name == 'Completed'])
        
        total_requirements = sum(len(phase.requirements) for cycle in idea.evolution_cycles for phase in cycle.phases)
        completed_requirements = sum(
            1 for cycle in idea.evolution_cycles 
            for phase in cycle.phases 
            for req in phase.requirements 
            if req.status.name == 'Completed'
        )

        # Calculate completion percentages for each evolution cycle
        for cycle in idea.evolution_cycles:
            total_phases = len(cycle.phases)
            completed_phases = len([p for p in cycle.phases if p.status.name == 'Completed'])
            cycle.completion_percentage = round((completed_phases / total_phases * 100) if total_phases > 0 else 0)
            
            # Calculate requirements completion for each phase
            for phase in cycle.phases:
                total_phase_reqs = len(phase.requirements)
                completed_phase_reqs = len([r for r in phase.requirements if r.status.name == 'Completed'])
                phase.completion_percentage = round((completed_phase_reqs / total_phase_reqs * 100) if total_phase_reqs > 0 else 0)

        stats = {
            'total_cycles': total_cycles,
            'completed_cycles': completed_cycles,
            'cycle_completion_rate': round((completed_cycles / total_cycles * 100) if total_cycles > 0 else 0),
            'total_requirements': total_requirements,
            'completed_requirements': completed_requirements,
            'requirement_completion_rate': round((completed_requirements / total_requirements * 100) if total_requirements > 0 else 0)
        }

        return render_template('control_panel/idea.html',
                             idea=idea,
                             tech_stacks=tech_stacks,
                             statuses=statuses,
                             requirement_types=requirement_types,
                             available_phases=available_phases,
                             stats=stats)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
