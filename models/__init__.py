# Import all models to ensure they are registered with SQLAlchemy
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
