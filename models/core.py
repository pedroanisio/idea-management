from datetime import datetime
from extensions import db

# Association tables
tech_stack_technology_version = db.Table('tech_stack_technology_version',
    db.Column('tech_stack_id', db.Integer, db.ForeignKey('tech_stacks.id')),
    db.Column('technology_version_id', db.Integer, db.ForeignKey('technology_version_aggregates.id')),
    db.PrimaryKeyConstraint('tech_stack_id', 'technology_version_id')
)

tech_stack_technology_association = db.Table('tech_stack_technology_association',
    db.Column('tech_stack_id', db.Integer, db.ForeignKey('tech_stacks.id')),
    db.Column('technology_id', db.Integer, db.ForeignKey('technologies.id')),
    db.PrimaryKeyConstraint('tech_stack_id', 'technology_id')
)

tech_stack_phase_association = db.Table('tech_stack_phase_association',
    db.Column('tech_stack_id', db.Integer, db.ForeignKey('tech_stacks.id')),
    db.Column('idea_evolution_phase_id', db.Integer, db.ForeignKey('idea_evolution_phases.id')),
    db.PrimaryKeyConstraint('tech_stack_id', 'idea_evolution_phase_id')
)

class Status(db.Model):
    __tablename__ = 'statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status relationship
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    status = db.relationship('Status', backref=db.backref('ideas', lazy=True))
    
    # Evolution Cycles through aggregation
    evolution_cycles = db.relationship('IdeaEvolutionCycle', back_populates='idea', lazy=True)

    def __repr__(self):
        return f'<Idea {self.title}>'

class EvolutionCycle(db.Model):
    __tablename__ = 'evolution_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status relationship
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    status = db.relationship('Status', backref=db.backref('evolution_cycles', lazy=True))
    
    # Ideas through aggregation
    ideas = db.relationship('IdeaEvolutionCycle', back_populates='evolution_cycle', lazy=True)

    # Phases relationship
    phases = db.relationship('Phase', back_populates='evolution_cycle', lazy=True)

    def __repr__(self):
        return f'<EvolutionCycle {self.name}>'

class IdeaEvolutionCycle(db.Model):
    """Aggregation table linking Ideas with Evolution Cycles"""
    __tablename__ = 'idea_evolution_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    evolution_cycle_id = db.Column(db.Integer, db.ForeignKey('evolution_cycles.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea = db.relationship('Idea', back_populates='evolution_cycles')
    evolution_cycle = db.relationship('EvolutionCycle', back_populates='ideas')
    status = db.relationship('Status', backref='idea_evolution_cycles')
    phases = db.relationship('IdeaEvolutionPhase', back_populates='idea_evolution_cycle', lazy=True)

    def __repr__(self):
        return f'<IdeaEvolutionCycle {self.id}>'

class Phase(db.Model):
    __tablename__ = 'phases'
    
    id = db.Column(db.Integer, primary_key=True)
    evolution_cycle_id = db.Column(db.Integer, db.ForeignKey('evolution_cycles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status relationship
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    status = db.relationship('Status', backref=db.backref('phases', lazy=True))
    
    # Evolution Cycle relationship
    evolution_cycle = db.relationship('EvolutionCycle', back_populates='phases')
    
    # Ideas and Evolution Cycles through aggregation
    idea_evolution_phases = db.relationship('IdeaEvolutionPhase', back_populates='phase', lazy=True)

    def __repr__(self):
        return f'<Phase {self.name}>'

class IdeaEvolutionPhase(db.Model):
    """Aggregation table linking IdeaEvolutionCycles with Phases"""
    __tablename__ = 'idea_evolution_phases'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_evolution_cycle_id = db.Column(db.Integer, db.ForeignKey('idea_evolution_cycles.id'), nullable=False)
    phase_id = db.Column(db.Integer, db.ForeignKey('phases.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea_evolution_cycle = db.relationship('IdeaEvolutionCycle', back_populates='phases')
    phase = db.relationship('Phase', back_populates='idea_evolution_phases')
    status = db.relationship('Status', backref='idea_evolution_phases')
    requirements = db.relationship('Requirement', back_populates='idea_evolution_phase', lazy=True)
    tech_stacks = db.relationship('TechStack', secondary=tech_stack_phase_association,
                                back_populates='idea_evolution_phases')

    def validate_tech_stacks(self):
        """Validate tech stack assignments for the phase"""
        if not self.tech_stacks:
            return True
            
        # Ensure no duplicate tech stacks
        tech_stack_ids = [ts.id for ts in self.tech_stacks]
        if len(tech_stack_ids) != len(set(tech_stack_ids)):
            raise ValueError("Duplicate tech stacks are not allowed")
            
        # Ensure tech stacks are compatible
        tech_types = {}
        for ts in self.tech_stacks:
            if ts.type_id in tech_types:
                # Allow multiple of same type only for certain types
                if ts.type.name not in ["Framework", "Library"]:
                    raise ValueError(f"Multiple tech stacks of type {ts.type.name} are not allowed")
            tech_types[ts.type_id] = ts
            
        return True

    def __repr__(self):
        return f'<IdeaEvolutionPhase {self.id}>'

class Requirement(db.Model):
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Type relationship
    type_id = db.Column(db.Integer, db.ForeignKey('requirement_types.id'))
    type = db.relationship('RequirementType', backref=db.backref('requirements', lazy=True))
    
    # Priority relationship
    priority_id = db.Column(db.Integer, db.ForeignKey('requirement_priorities.id'))
    priority = db.relationship('RequirementPriority', backref=db.backref('requirements', lazy=True))
    
    # Status relationship
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    status = db.relationship('Status', backref=db.backref('requirements', lazy=True))
    
    # Link to IdeaEvolutionPhase
    idea_evolution_phase_id = db.Column(db.Integer, db.ForeignKey('idea_evolution_phases.id'), nullable=False)
    idea_evolution_phase = db.relationship('IdeaEvolutionPhase', back_populates='requirements')

class RequirementType(db.Model):
    __tablename__ = 'requirement_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RequirementPriority(db.Model):
    __tablename__ = 'requirement_priorities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TechnologyType(db.Model):
    __tablename__ = 'technology_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TechnologyType {self.name}>'

class TechStack(db.Model):
    __tablename__ = 'tech_stacks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('technology_types.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    type = db.relationship('TechnologyType', backref=db.backref('tech_stacks', lazy=True))
    idea_evolution_phases = db.relationship('IdeaEvolutionPhase', secondary=tech_stack_phase_association,
                                          back_populates='tech_stacks')
    technologies = db.relationship('Technology', secondary=tech_stack_technology_association,
                                 backref=db.backref('tech_stacks', lazy=True))
    technology_versions = db.relationship('TechnologyVersionAggregate', secondary=tech_stack_technology_version,
                                        backref='tech_stacks')

    def __repr__(self):
        return f'<TechStack {self.name}>'

class TechnologyVersion(db.Model):
    __tablename__ = 'technology_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    technology_id = db.Column(db.Integer, db.ForeignKey('technologies.id'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    release_date = db.Column(db.Date)
    end_of_life_date = db.Column(db.Date)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    technology = db.relationship('Technology', back_populates='versions')
    version_aggregates = db.relationship('TechnologyVersionAggregate', back_populates='version',
                                       overlaps="technology")

    __table_args__ = (
        db.UniqueConstraint('technology_id', 'version', name='uq_tech_version'),
    )

    def __repr__(self):
        return f'<TechnologyVersion {self.technology.name}:{self.version}>'

class Technology(db.Model):
    __tablename__ = 'technologies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('technology_types.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    technology_type = db.relationship('TechnologyType', backref=db.backref('technologies', lazy=True))
    versions = db.relationship('TechnologyVersion', back_populates='technology', lazy='dynamic')
    version_aggregates = db.relationship('TechnologyVersionAggregate', back_populates='technology',
                                       overlaps="versions")

    __table_args__ = (
        db.UniqueConstraint('name', 'type_id', name='uq_technology_name_type'),
    )

    def __repr__(self):
        return f'<Technology {self.name}>'

class TechnologyVersionAggregate(db.Model):
    __tablename__ = 'technology_version_aggregates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    technology_id = db.Column(db.Integer, db.ForeignKey('technologies.id'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('technology_versions.id'), nullable=False)

    # Relationships
    technology = db.relationship('Technology', back_populates='version_aggregates',
                               overlaps="versions")
    version = db.relationship('TechnologyVersion', back_populates='version_aggregates',
                            overlaps="technology")

    def __repr__(self):
        return f'<TechnologyVersionAggregate {self.technology.name} {self.version.version}>'
