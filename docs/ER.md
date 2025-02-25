# Entity Relationship Model

## Core Entities

### Idea
- **Description**: Represents a project idea or concept
- **Key Fields**: id, title, description, status_id
- **Relationships**:
  - Has many Evolution Cycles through IdeaEvolutionCycle
  - Has one Status

### EvolutionCycle
- **Description**: Represents a development cycle or iteration
- **Key Fields**: id, name, description, status_id
- **Relationships**:
  - Has many Ideas through IdeaEvolutionCycle
  - Has many Phases
  - Has one Status

### Phase
- **Description**: A specific stage within an evolution cycle
- **Key Fields**: id, name, description, order, evolution_cycle_id
- **Relationships**:
  - Belongs to one EvolutionCycle
  - Has many IdeaEvolutionPhases
  - Has one Status

### IdeaEvolutionPhase
- **Description**: Links an idea's evolution cycle to specific phases
- **Key Fields**: id, idea_evolution_cycle_id, phase_id, status_id, order
- **Relationships**:
  - Belongs to one IdeaEvolutionCycle
  - Belongs to one Phase
  - Has many Requirements
  - Has many TechStacks through tech_stack_phase_association
  - Has one Status

### Requirement
- **Description**: Specific requirements for an idea in a particular phase
- **Key Fields**: id, name, description, type_id, priority_id, status_id, idea_evolution_phase_id
- **Relationships**:
  - Belongs to one IdeaEvolutionPhase
  - Has one RequirementType
  - Has one RequirementPriority
  - Has one Status

### TechStack
- **Description**: A collection of technologies used in a phase
- **Key Fields**: id, name, description, type_id
- **Relationships**:
  - Has many IdeaEvolutionPhases through tech_stack_phase_association
  - Has many Technologies through tech_stack_technology_association
  - Has many TechnologyVersions through tech_stack_technology_version
  - Has one TechnologyType

### Technology
- **Description**: Individual technology or tool
- **Key Fields**: id, name, description, type_id
- **Relationships**:
  - Has many TechStacks through tech_stack_technology_association
  - Has many Versions (TechnologyVersion)
  - Has one TechnologyType

## Association Tables

### tech_stack_phase_association
- **Purpose**: Links TechStacks to IdeaEvolutionPhases
- **Fields**: tech_stack_id, idea_evolution_phase_id

### tech_stack_technology_association
- **Purpose**: Links TechStacks to Technologies
- **Fields**: tech_stack_id, technology_id

### tech_stack_technology_version
- **Purpose**: Links TechStacks to specific TechnologyVersions
- **Fields**: tech_stack_id, technology_version_id

## Support Entities

### Status
- **Description**: Represents the current state of various entities
- **Key Fields**: id, name
- **Used By**: Idea, EvolutionCycle, IdeaEvolutionPhase, Requirement

### RequirementType
- **Description**: Categorizes requirements
- **Key Fields**: id, name
- **Used By**: Requirement

### RequirementPriority
- **Description**: Defines priority levels for requirements
- **Key Fields**: id, name
- **Used By**: Requirement

### TechnologyType
- **Description**: Categorizes technologies and tech stacks
- **Key Fields**: id, name
- **Used By**: Technology, TechStack

### TechnologyVersion
- **Description**: Specific versions of technologies
- **Key Fields**: id, technology_id, version, release_date, end_of_life_date
- **Relationships**:
  - Belongs to one Technology
  - Has many TechStacks through tech_stack_technology_version

## Validation Rules

### TechStack Assignment
1. No duplicate tech stacks allowed in a phase
2. Multiple tech stacks of the same type are only allowed for:
   - Framework
   - Library
3. Each phase must have compatible tech stacks based on their types

## Database Diagram
```mermaid
erDiagram
    Idea ||--o{ IdeaEvolutionCycle : has
    EvolutionCycle ||--o{ IdeaEvolutionCycle : has
    EvolutionCycle ||--o{ Phase : contains
    IdeaEvolutionCycle ||--o{ IdeaEvolutionPhase : has
    Phase ||--o{ IdeaEvolutionPhase : has
    IdeaEvolutionPhase ||--o{ Requirement : contains
    IdeaEvolutionPhase }o--o{ TechStack : uses
    TechStack }o--o{ Technology : includes
    Technology ||--o{ TechnologyVersion : has
    TechStack }o--o{ TechnologyVersion : uses
    
    Status ||--o{ Idea : status
    Status ||--o{ EvolutionCycle : status
    Status ||--o{ IdeaEvolutionPhase : status
    Status ||--o{ Requirement : status
    
    RequirementType ||--o{ Requirement : type
    RequirementPriority ||--o{ Requirement : priority
    TechnologyType ||--o{ Technology : type
    TechnologyType ||--o{ TechStack : type