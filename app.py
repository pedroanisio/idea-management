from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
        # Get all models
        ideas = Idea.query.all()
        evolution_cycles = EvolutionCycle.query.all()
        tech_stacks = TechStack.query.all()
        requirements = Requirement.query.all()
        technologies = Technology.query.all()
        
        # Get recent activities (last 5 activities)
        activities = []
        
        # Ideas activity
        for idea in sorted(ideas, key=lambda x: x.created_at, reverse=True)[:5]:
            activities.append({
                'type': 'idea',
                'description': f'New idea created: {idea.title}',
                'created_at': idea.created_at,
                'sort_date': idea.created_at
            })
            
        # Requirements activity
        for req in sorted(requirements, key=lambda x: x.created_at, reverse=True)[:5]:
            activities.append({
                'type': 'requirement',
                'description': f'New requirement added: {req.name}',
                'created_at': req.created_at,
                'sort_date': req.created_at
            })
            
        # Sort all activities by created_at
        activities = sorted(activities, key=lambda x: x['sort_date'], reverse=True)[:5]
        
        return render_template('index.html',
                             ideas=ideas,
                             evolution_cycles=evolution_cycles,
                             tech_stacks=tech_stacks,
                             ideas_count=len(ideas),
                             evolutions_count=len(evolution_cycles),
                             techstacks_count=len(tech_stacks),
                             requirements_count=len(requirements),
                             technologies_count=len(technologies),
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
            title = request.form.get('title')
            description = request.form.get('description')

            if not title or not description:
                flash('Title and description are required.', 'danger')
                return redirect(url_for('ideas_create'))

            idea = Idea(
                title=title,
                description=description,
                status=default_status
            )

            try:
                db.session.add(idea)
                
                # Create initial evolution cycle
                evolution_cycle = EvolutionCycle(
                    name="Initial Cycle",
                    description="Initial evolution cycle for the idea",
                    status=default_status
                )
                db.session.add(evolution_cycle)
                
                # Create IdeaEvolutionCycle association
                idea_evolution_cycle = IdeaEvolutionCycle(
                    idea=idea,
                    evolution_cycle=evolution_cycle,
                    status=default_status
                )
                db.session.add(idea_evolution_cycle)

                # Handle tech stacks
                tech_stack_ids = request.form.getlist('tech_stack')
                if tech_stack_ids:
                    tech_stacks = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all()
                    idea_evolution_cycle.tech_stacks.extend(tech_stacks)

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
            idea.title = request.form['title']
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

    @app.route('/ideas/<int:id>/export', methods=['POST'])
    def ideas_export(id):
        idea = db.session.query(Idea)\
            .options(
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.evolution_cycle),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.phase),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.requirements)
                .joinedload(Requirement.status),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.requirements)
                .joinedload(Requirement.type),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.tech_stacks),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.status)
            )\
            .filter(Idea.id == id)\
            .first_or_404()

        # Get filters from form
        include_evolution_cycles = request.form.get('include_evolution_cycles') == 'true'
        include_phases = request.form.get('include_phases') == 'true'
        include_requirements = request.form.get('include_requirements') == 'true'
        include_tech_stacks = request.form.get('include_tech_stacks') == 'true'
        
        # Get filter values
        status_filter = request.form.getlist('status_filter')
        evolution_cycle_filter = request.form.getlist('evolution_cycle_filter')
        phase_filter = request.form.getlist('phase_filter')
        requirement_type_filter = request.form.getlist('requirement_type_filter')

        # Build the export data
        export_data = {
            'idea': {
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'created_at': idea.created_at.isoformat(),
                'updated_at': idea.updated_at.isoformat() if idea.updated_at else None,
            }
        }

        if include_evolution_cycles:
            export_data['evolution_cycles'] = []
            for cycle in idea.evolution_cycles:
                # Skip if status doesn't match filter
                if status_filter != ['all'] and str(cycle.status.id) not in status_filter:
                    continue
                    
                # Skip if evolution cycle doesn't match filter
                if evolution_cycle_filter != ['all'] and str(cycle.evolution_cycle.id) not in evolution_cycle_filter:
                    continue

                cycle_data = {
                    'id': cycle.id,
                    'name': cycle.evolution_cycle.name,
                    'status': cycle.status.name,
                }

                if include_tech_stacks:
                    cycle_data['tech_stacks'] = [
                        {'id': ts.id, 'name': ts.name}
                        for ts in cycle.tech_stacks
                    ]

                if include_phases:
                    cycle_data['phases'] = []
                    for phase in cycle.phases:
                        # Skip if status doesn't match filter
                        if status_filter != ['all'] and str(phase.status.id) not in status_filter:
                            continue
                            
                        # Skip if phase doesn't match filter
                        if phase_filter != ['all'] and str(phase.phase.id) not in phase_filter:
                            continue

                        phase_data = {
                            'id': phase.id,
                            'name': phase.phase.name,
                            'description': phase.phase.description,
                            'status': phase.status.name,
                            'order': phase.order,
                        }

                        if include_requirements:
                            phase_data['requirements'] = []
                            for req in phase.requirements:
                                # Skip if status doesn't match filter
                                if status_filter != ['all'] and str(req.status.id) not in status_filter:
                                    continue
                                    
                                # Skip if requirement type doesn't match filter
                                if requirement_type_filter != ['all'] and str(req.type_id) not in requirement_type_filter:
                                    continue

                                phase_data['requirements'].append({
                                    'id': req.id,
                                    'name': req.name,
                                    'description': req.description,
                                    'type': req.type.name if req.type else None,
                                    'status': req.status.name,
                                })

                        if phase_data['requirements'] or not include_requirements:
                            cycle_data['phases'].append(phase_data)

                if cycle_data.get('phases') or not include_phases:
                    export_data['evolution_cycles'].append(cycle_data)

        # Create a temporary file to store the YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            yaml.dump(export_data, temp_file, default_flow_style=False, sort_keys=False)

        # Send the file
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'idea_{idea.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml',
            mimetype='application/x-yaml'
        )

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

    @app.route('/evolutions/<int:id>/phases/create', methods=['GET', 'POST'])
    def evolution_phases_create(id):
        evolution_cycle = EvolutionCycle.query.get_or_404(id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            order = request.form.get('order')

            print(f"Creating phase with name={name}, description={description}, order={order}")  # Debug log

            # Validate order is a positive integer
            try:
                order = int(order)
                if order <= 0:
                    raise ValueError("Order must be positive")
            except (TypeError, ValueError):
                flash('Order must be a positive number.', 'danger')
                return redirect(url_for('evolution_phases_create', id=id))

            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('evolution_phases_create', id=id))

            # Get default status
            default_status = Status.query.filter_by(name='New').first()
            if not default_status:
                default_status = Status(name='New')
                db.session.add(default_status)
                db.session.commit()

            try:
                # Create the phase
                phase = Phase(
                    name=name,
                    description=description,
                    evolution_cycle_id=id,
                    order=order,
                    status_id=default_status.id  # Use status_id instead of status object
                )
                print(f"Created phase object: {phase}")  # Debug log
                db.session.add(phase)
                db.session.flush()  # Flush to get the phase ID
                
                # Add this phase to all existing idea evolution cycles
                idea_cycles = IdeaEvolutionCycle.query.filter_by(evolution_cycle_id=id).all()
                print(f"Found {len(idea_cycles)} idea cycles")  # Debug log
                
                for idea_cycle in idea_cycles:
                    idea_phase = IdeaEvolutionPhase(
                        idea_evolution_cycle_id=idea_cycle.id,  # Use IDs instead of objects
                        phase_id=phase.id,
                        order=order,
                        status_id=default_status.id
                    )
                    print(f"Created idea phase: {idea_phase}")  # Debug log
                    db.session.add(idea_phase)

                db.session.commit()
                flash('Phase created successfully!', 'success')
                return redirect(url_for('evolutions_show', id=id))
            except Exception as e:
                db.session.rollback()
                print(f"Error creating phase: {str(e)}")  # Debug log
                flash('Error creating phase. Please try again.', 'danger')
                return redirect(url_for('evolution_phases_create', id=id))

        return render_template('evolutions/phases/create.html', evolution_cycle=evolution_cycle)

    @app.route('/evolutions/<int:evolution_id>/phases/<int:phase_id>/edit', methods=['GET', 'POST'])
    def evolution_phases_edit(evolution_id, phase_id):
        evolution_cycle = EvolutionCycle.query.get_or_404(evolution_id)
        phase = Phase.query.get_or_404(phase_id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            order = request.form.get('order', type=int)

            if not name or not description or not order:
                flash('Name, description, and order are required.', 'danger')
                return redirect(url_for('evolution_phases_edit', evolution_id=evolution_id, phase_id=phase_id))

            try:
                phase.name = name
                phase.description = description
                phase.order = order
                db.session.commit()
                flash('Phase updated successfully!', 'success')
                return redirect(url_for('evolutions_show', id=evolution_id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating phase. Please try again.', 'danger')
                return redirect(url_for('evolution_phases_edit', evolution_id=evolution_id, phase_id=phase_id))

        return render_template('evolutions/phases/edit.html', 
                             evolution_cycle=evolution_cycle,
                             phase=phase)

    @app.route('/evolutions/<int:evolution_id>/phases/<int:phase_id>/delete', methods=['POST'])
    def evolution_phases_delete(evolution_id, phase_id):
        evolution_cycle = EvolutionCycle.query.get_or_404(evolution_id)
        phase = Phase.query.get_or_404(phase_id)
        
        try:
            # Delete all associated IdeaEvolutionPhases and their requirements first
            idea_phases = IdeaEvolutionPhase.query.filter_by(phase_id=phase_id).all()
            for idea_phase in idea_phases:
                # Delete associated requirements
                Requirement.query.filter_by(idea_evolution_phase_id=idea_phase.id).delete()
                db.session.delete(idea_phase)
            
            db.session.delete(phase)
            db.session.commit()
            flash('Phase and all associated data deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting phase. Please try again.', 'danger')
            
        return redirect(url_for('evolutions_show', id=evolution_id))

    @app.route('/ideas/<int:idea_id>/evolutions/<int:evolution_id>/phases/<int:phase_id>')
    def evolution_phases_show(idea_id, evolution_id, phase_id):
        # Get the IdeaEvolutionPhase with all necessary relationships
        idea_phase = db.session.query(IdeaEvolutionPhase)\
            .options(
                db.joinedload(IdeaEvolutionPhase.phase),
                db.joinedload(IdeaEvolutionPhase.status),
                db.joinedload(IdeaEvolutionPhase.requirements)
                .joinedload(Requirement.status),
                db.joinedload(IdeaEvolutionPhase.requirements)
                .joinedload(Requirement.type),
                db.joinedload(IdeaEvolutionPhase.idea_evolution_cycle)
                .joinedload(IdeaEvolutionCycle.idea),
                db.joinedload(IdeaEvolutionPhase.idea_evolution_cycle)
                .joinedload(IdeaEvolutionCycle.evolution_cycle)
            )\
            .join(IdeaEvolutionPhase.idea_evolution_cycle)\
            .filter(
                IdeaEvolutionPhase.phase_id == phase_id,
                IdeaEvolutionCycle.idea_id == idea_id,
                IdeaEvolutionCycle.evolution_cycle_id == evolution_id
            )\
            .first_or_404()

        requirement_types = RequirementType.query.all()
        
        return render_template('evolutions/phases/show.html',
                             idea_phase=idea_phase,
                             requirement_types=requirement_types)

    @app.route('/phases/<int:id>')
    def phases_show(id):
        phase = Phase.query.get_or_404(id)
        # Get all idea evolution phases that use this phase
        idea_evolution_phases = db.session.query(
            IdeaEvolutionPhase.id,
            Idea.id.label('idea_id'),
            Idea.title.label('idea_name'),  
            EvolutionCycle.name.label('cycle_name'),
            Phase.order.label('phase_order')
        ).join(
            IdeaEvolutionPhase.idea_evolution_cycle
        ).join(
            IdeaEvolutionCycle.idea
        ).join(
            IdeaEvolutionCycle.evolution_cycle
        ).join(
            IdeaEvolutionPhase.phase
        ).filter(
            Phase.id == id
        ).all()
        
        return render_template('phases/show.html', 
                             phase=phase,
                             idea_evolution_phases=idea_evolution_phases)

    @app.route('/phases/<int:id>/edit', methods=['GET', 'POST'])
    def phases_edit(id):
        phase = Phase.query.get_or_404(id)
        if request.method == 'POST':
            phase.name = request.form.get('name')
            phase.description = request.form.get('description')
            phase.order = request.form.get('order', type=int)
            
            # Update status if provided
            status_id = request.form.get('status_id')
            if status_id:
                phase.status = Status.query.get(status_id)
            
            try:
                db.session.commit()
                flash('Phase updated successfully!', 'success')
                return redirect(url_for('phases_show', id=phase.id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating phase. Please try again.', 'danger')
                return redirect(url_for('phases_edit', id=phase.id))

        statuses = Status.query.all()
        return render_template('phases/edit.html', phase=phase, statuses=statuses)

    @app.route('/phases/<int:id>/delete', methods=['POST'])
    def phases_delete(id):
        phase = Phase.query.get_or_404(id)
        evolution_id = None
        
        # If this phase belongs to an evolution cycle, get its ID for redirect
        idea_evolution_phase = IdeaEvolutionPhase.query.filter_by(phase_id=id).first()
        if idea_evolution_phase:
            evolution_id = idea_evolution_phase.idea_evolution_cycle.evolution_cycle.id
        
        try:
            db.session.delete(phase)
            db.session.commit()
            flash('Phase deleted successfully!', 'success')
            if evolution_id:
                return redirect(url_for('evolutions_show', id=evolution_id))
            return redirect(url_for('evolutions'))
        except Exception as e:
            db.session.rollback()
            flash('Error deleting phase. Please try again.', 'danger')
            return redirect(url_for('phases_show', id=id))

    # Requirements routes
    @app.route('/requirements')
    def requirements():
        requirements = Requirement.query.all()
        return render_template('requirements/index.html', requirements=requirements)

    @app.route('/requirements/create', methods=['GET', 'POST'])
    def requirements_create():
        idea_evolution_phase_id = request.args.get('idea_evolution_phase_id', type=int)
        
        if not idea_evolution_phase_id:
            flash('No phase specified.', 'danger')
            return redirect(url_for('index'))
            
        # Get the phase details
        phase_details = db.session.query(
            IdeaEvolutionPhase,
            Phase.name.label('phase_name'),
            Idea.title.label('idea_name'),  
            EvolutionCycle.name.label('evolution_name')
        ).join(
            Phase, IdeaEvolutionPhase.phase_id == Phase.id
        ).join(
            IdeaEvolutionCycle, IdeaEvolutionPhase.idea_evolution_cycle_id == IdeaEvolutionCycle.id
        ).join(
            Idea, IdeaEvolutionCycle.idea_id == Idea.id
        ).join(
            EvolutionCycle, IdeaEvolutionCycle.evolution_cycle_id == EvolutionCycle.id
        ).filter(
            IdeaEvolutionPhase.id == idea_evolution_phase_id
        ).first()
        
        if not phase_details:
            flash('Phase not found.', 'danger')
            return redirect(url_for('index'))

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            type_id = request.form.get('type_id', type=int)
            priority_id = request.form.get('priority_id', type=int)

            if not all([name, description, type_id, priority_id]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('requirements_create', idea_evolution_phase_id=idea_evolution_phase_id))

            try:
                # Get default status
                default_status = Status.query.filter_by(name='New').first()
                if not default_status:
                    default_status = Status(name='New')
                    db.session.add(default_status)
                    db.session.commit()

                requirement = Requirement(
                    name=name,
                    description=description,
                    type_id=type_id,
                    priority_id=priority_id,
                    status=default_status,
                    idea_evolution_phase_id=idea_evolution_phase_id
                )
                db.session.add(requirement)
                db.session.commit()
                flash('Requirement created successfully!', 'success')
                return redirect(url_for('ideas_show', id=phase_details.IdeaEvolutionPhase.idea_evolution_cycle.idea_id))
            except Exception as e:
                db.session.rollback()
                flash('Error creating requirement. Please try again.', 'danger')
                return redirect(url_for('requirements_create', idea_evolution_phase_id=idea_evolution_phase_id))

        requirement_types = RequirementType.query.all()
        requirement_priorities = RequirementPriority.query.all()
        
        return render_template('requirements/create.html',
                             phase_details=phase_details,
                             requirement_types=requirement_types,
                             requirement_priorities=requirement_priorities)

    @app.route('/requirements/<int:id>')
    def requirements_show(id):
        requirement = Requirement.query.get_or_404(id)
        return render_template('requirements/show.html', requirement=requirement)

    @app.route('/requirements/<int:id>/edit', methods=['GET', 'POST'])
    def requirements_edit(id):
        requirement = Requirement.query.get_or_404(id)
        requirement_types = RequirementType.query.all()
        statuses = Status.query.all()

        if request.method == 'POST':
            requirement.name = request.form['name']
            requirement.description = request.form['description']
            requirement.type_id = request.form['requirement_type_id']
            requirement.status_id = request.form['status_id']

            try:
                db.session.commit()
                flash('Requirement updated successfully!', 'success')
                return redirect(url_for('evolution_phases_show',
                                      idea_id=requirement.idea_evolution_phase.idea_evolution_cycle.idea.id,
                                      evolution_id=requirement.idea_evolution_phase.idea_evolution_cycle.evolution_cycle.id,
                                      phase_id=requirement.idea_evolution_phase.phase.id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating requirement. Please try again.', 'danger')

        return render_template('requirements/edit.html',
                             requirement=requirement,
                             requirement_types=requirement_types,
                             statuses=statuses)

    @app.route('/requirements/<int:id>/delete', methods=['POST'])
    def requirements_delete(id):
        requirement = Requirement.query.get_or_404(id)
        idea_phase = requirement.idea_evolution_phase
        db.session.delete(requirement)
        db.session.commit()
        flash('Requirement deleted successfully!', 'success')
        return redirect(url_for('evolutions_show', id=idea_phase.idea_evolution_cycle.evolution_cycle.id))

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
        tech_stacks = TechStack.query.all()
        return render_template('techstacks/index.html', tech_stacks=tech_stacks)

    @app.route('/techstacks/create', methods=['GET', 'POST'])
    def techstacks_create():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            type_id = request.form.get('type_id')

            if not name or not type_id:
                flash('Name and type are required.', 'danger')
                return redirect(url_for('techstacks_create'))

            tech_stack = TechStack(
                name=name,
                description=description,
                type_id=type_id
            )

            try:
                db.session.add(tech_stack)
                db.session.commit()
                flash('Tech Stack created successfully!', 'success')
                return redirect(url_for('techstacks'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating tech stack.', 'danger')
                return redirect(url_for('techstacks_create'))

        technology_types = TechnologyType.query.all()
        return render_template('techstacks/create.html', technology_types=technology_types)

    @app.route('/techstacks/<int:id>')
    def techstacks_show(id):
        stack = TechStack.query.get_or_404(id)
        return render_template('techstacks/show.html', stack=stack, now=datetime.now().date())

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

        technology_types = TechnologyType.query.all()
        technologies = Technology.query.all()
        return render_template('techstacks/edit.html', 
                             tech_stack=tech_stack,
                             technology_types=technology_types,
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
        # Get idea with all necessary relationships loaded
        idea = db.session.query(Idea)\
            .options(
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.evolution_cycle),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.phase),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.requirements),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.tech_stacks),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.status),
                db.joinedload(Idea.evolution_cycles)
                .joinedload(IdeaEvolutionCycle.phases)
                .joinedload(IdeaEvolutionPhase.status)
            )\
            .filter(Idea.id == id)\
            .first_or_404()

        tech_stacks = TechStack.query.all()
        statuses = Status.query.all()
        requirement_types = RequirementType.query.all()

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
                             stats=stats)

    @app.route('/ideas/<int:id>/tech-stacks/manage', methods=['POST'])
    def tech_stacks_manage(id):
        idea = Idea.query.get_or_404(id)
        tech_stack_ids = request.form.getlist('tech_stack')
        
        try:
            # Get the first evolution cycle (assuming it exists)
            if idea.evolution_cycles:
                cycle = idea.evolution_cycles[0]
                # Update tech stacks
                cycle.tech_stacks = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all() if tech_stack_ids else []
                db.session.commit()
                flash('Tech stacks updated successfully!', 'success')
            else:
                flash('No evolution cycle found for this idea.', 'warning')
            
            return redirect(url_for('idea_control_panel', id=id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating tech stacks. Please try again.', 'danger')
            return redirect(url_for('idea_control_panel', id=id))

    @app.route('/ideas/<int:idea_id>/evolution-cycles/<int:cycle_id>')
    def evolution_cycle_detail(idea_id, cycle_id):
        idea = Idea.query.get_or_404(idea_id)
        idea_evolution_cycle = IdeaEvolutionCycle.query\
            .filter_by(idea_id=idea_id, id=cycle_id)\
            .first_or_404()
        
        # Get all phases for this evolution cycle
        phases = Phase.query\
            .join(IdeaEvolutionPhase)\
            .filter(IdeaEvolutionPhase.idea_evolution_cycle_id == cycle_id)\
            .order_by(Phase.order)\
            .all()
        
        # Get all requirements grouped by phase
        requirements_by_phase = {}
        for phase in phases:
            requirements = Requirement.query\
                .join(IdeaEvolutionPhase)\
                .filter(
                    IdeaEvolutionPhase.phase_id == phase.id,
                    IdeaEvolutionPhase.idea_evolution_cycle_id == cycle_id
                )\
                .all()
            requirements_by_phase[phase.id] = requirements
        
        return render_template('evolutions/detail.html',
                             idea=idea,
                             cycle=idea_evolution_cycle,
                             phases=phases,
                             requirements_by_phase=requirements_by_phase)

    @app.route('/ideas/<int:idea_id>/evolution-cycles/<int:cycle_id>/edit', methods=['GET', 'POST'])
    def evolution_cycle_edit(idea_id, cycle_id):
        idea = Idea.query.get_or_404(idea_id)
        idea_evolution_cycle = IdeaEvolutionCycle.query\
            .filter_by(idea_id=idea_id, id=cycle_id)\
            .first_or_404()
        
        if request.method == 'POST':
            try:
                # Update evolution cycle
                idea_evolution_cycle.evolution_cycle.name = request.form.get('name')
                idea_evolution_cycle.evolution_cycle.description = request.form.get('description')
                
                # Update status if provided
                status_id = request.form.get('status')
                if status_id:
                    idea_evolution_cycle.status_id = status_id
                
                # Update tech stacks
                tech_stack_ids = request.form.getlist('tech_stack')
                if tech_stack_ids:
                    tech_stacks = TechStack.query.filter(TechStack.id.in_(tech_stack_ids)).all()
                    idea_evolution_cycle.tech_stacks = tech_stacks
                
                db.session.commit()
                flash('Evolution cycle updated successfully!', 'success')
                return redirect(url_for('evolution_cycle_detail', idea_id=idea_id, cycle_id=cycle_id))
            except Exception as e:
                db.session.rollback()
                flash('Error updating evolution cycle. Please try again.', 'danger')
        
        # Get all available tech stacks and statuses for the form
        tech_stacks = TechStack.query.all()
        statuses = Status.query.all()
        
        return render_template('evolutions/edit.html',
                             idea=idea,
                             cycle=idea_evolution_cycle,
                             tech_stacks=tech_stacks,
                             statuses=statuses)

    @app.route('/ideas/<int:idea_id>/evolution-cycles/<int:cycle_id>/delete', methods=['POST'])
    def evolution_cycle_delete(idea_id, cycle_id):
        idea = Idea.query.get_or_404(idea_id)
        idea_evolution_cycle = IdeaEvolutionCycle.query\
            .filter_by(idea_id=idea_id, id=cycle_id)\
            .first_or_404()
        
        try:
            # Delete associated phases and requirements first
            for phase in idea_evolution_cycle.phases:
                # Delete requirements for this phase
                Requirement.query.filter_by(phase_id=phase.id).delete()
                db.session.delete(phase)
            
            # Delete the evolution cycle
            evolution_cycle = idea_evolution_cycle.evolution_cycle
            db.session.delete(idea_evolution_cycle)
            db.session.delete(evolution_cycle)
            
            db.session.commit()
            flash('Evolution cycle deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting evolution cycle. Please try again.', 'danger')
        
        return redirect(url_for('idea_control_panel', id=idea_id))

    @app.route('/ideas/<int:id>/tech-stacks/update', methods=['POST'])
    def idea_tech_stacks_update(id):
        idea = Idea.query.get_or_404(id)
        cycle_id = request.form.get('cycle_id')
        
        if not cycle_id:
            flash('Evolution cycle is required.', 'danger')
            return redirect(url_for('idea_control_panel', id=id))
            
        cycle = IdeaEvolutionCycle.query.get_or_404(cycle_id)
        tech_stack_ids = request.form.getlist('tech_stacks[]')
        
        try:
            # Update tech stacks for the cycle
            cycle.tech_stacks = []
            for stack_id in tech_stack_ids:
                stack = TechStack.query.get(stack_id)
                if stack:
                    cycle.tech_stacks.append(stack)
            
            db.session.commit()
            flash('Tech stacks updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating tech stacks.', 'danger')
            
        return redirect(url_for('idea_control_panel', id=id))

    @app.route('/ideas/<int:id>/tech-stacks')
    def idea_tech_stacks(id):
        cycle = IdeaEvolutionCycle.query.get_or_404(id)
        return jsonify({
            'tech_stacks': [stack.id for stack in cycle.tech_stacks]
        })

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
