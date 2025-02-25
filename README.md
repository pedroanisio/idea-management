# Idea Management

A comprehensive web application for managing ideas, their evolution cycles, and associated technical requirements.

## Description

Idea Management is a Flask-based web application that helps you organize and track your ideas from conception to implementation. It provides a structured way to manage ideas, their evolution cycles, phases, requirements, and technical specifications.

## Entity Relationship Model

### Core Entities

1. **Idea**
   - Primary entity for project ideas
   - Fields: title, description, timestamps
   - Relations:
     - Has one Status
     - Has many EvolutionCycles through IdeaEvolutionCycle

2. **EvolutionCycle**
   - Represents development cycles/stages
   - Fields: name, description, timestamps
   - Relations:
     - Has one Status
     - Has many Ideas through IdeaEvolutionCycle
     - Has many Phases

3. **Phase**
   - Represents stages within an evolution cycle
   - Fields: name, description, order, timestamps
   - Relations:
     - Belongs to one EvolutionCycle
     - Has one Status
     - Connected to Ideas through IdeaEvolutionPhase

4. **Requirement**
   - Represents project requirements
   - Fields: name, description, timestamps
   - Relations:
     - Has one RequirementType
     - Has one RequirementPriority
     - Has one Status
     - Belongs to one IdeaEvolutionPhase

### Technology Stack Entities

5. **TechStack**
   - Represents collections of technologies
   - Fields: name, description, timestamps
   - Relations:
     - Has one TechnologyType
     - Connected to IdeaEvolutionCycles
     - Connected to Technologies and Versions

6. **Technology**
   - Represents individual technologies
   - Fields: name, description, timestamps
   - Relations:
     - Has one TechnologyType
     - Has many Versions
     - Has many VersionAggregates

7. **TechnologyVersion**
   - Represents specific versions of technologies
   - Fields: version, release_date, end_of_life_date, is_default
   - Relations:
     - Belongs to one Technology
     - Has many VersionAggregates

### Supporting Entities

- **Status**: Used across multiple entities for state tracking
- **RequirementType**: Classifies requirements
- **RequirementPriority**: Defines priority levels
- **TechnologyType**: Classifies technologies and tech stacks

## Features

### Idea Management
- Create and manage project ideas
- Track idea status and progress
- Organize ideas through evolution cycles and phases
- Manage requirements with types and priorities

### Technology Stack Management
- Define technology stacks for each phase
- Track technology versions and compatibility
- Manage technology relationships and dependencies
- Validate tech stack assignments based on type rules

### Evolution Cycles
- Create development cycles for ideas
- Define ordered phases within cycles
- Track progress through status updates
- Associate tech stacks with specific phases

### Requirements
- Create and manage requirements
- Categorize by type and priority
- Associate with specific phases
- Track requirement status

### Export/Import
- Export idea data to YAML format
- Include/exclude specific components:
  - Evolution cycles
  - Phases
  - Requirements
  - Tech stacks
- Filter exports by:
  - Evolution cycles
  - Phases
  - Requirement types

## Entity Relationships

The application uses a sophisticated entity relationship model that connects ideas, evolution cycles, phases, requirements, and technology stacks. Key relationships include:

- Ideas have multiple evolution cycles
- Evolution cycles contain ordered phases
- Phases contain requirements and tech stacks
- Tech stacks are associated with specific phases
- Tech stacks contain multiple technologies with versions

For a detailed view of the entity relationships, see [ER Documentation](docs/ER.md).

## Routes and Templates

### Main Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/` | GET | `index.html` | Home page |
| `/ideas` | GET | `ideas/index.html` | List all ideas |
| `/ideas/create` | GET, POST | `ideas/create.html` | Create new idea |
| `/ideas/<id>` | GET | `ideas/show.html` | View idea details |
| `/ideas/<id>/edit` | GET, POST | `ideas/edit.html` | Edit idea |
| `/ideas/<id>/delete` | POST | - | Delete idea |
| `/ideas/<id>/export` | POST | - | Export idea data to YAML |
| `/ideas/<id>/control-panel` | GET | `control_panel/idea.html` | Idea control panel |

### Evolution Cycle Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/evolutions` | GET | `evolutions/index.html` | List evolution cycles |
| `/evolutions/create` | GET, POST | `evolutions/create.html` | Create evolution cycle |
| `/evolutions/<id>` | GET | `evolutions/show.html` | View evolution cycle |
| `/evolutions/<id>/edit` | GET, POST | `evolutions/edit.html` | Edit evolution cycle |
| `/evolutions/<id>/delete` | POST | - | Delete evolution cycle |
| `/evolutions/link/<idea_id>` | GET, POST | `evolutions/link.html` | Link evolution to idea |
| `/evolutions/<id>/techstacks/add` | GET, POST | `evolutions/add_techstack.html` | Add tech stack |

### Phase Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/phases/<id>` | GET | `phases/show.html` | View phase |
| `/phases/<id>/edit` | GET, POST | `phases/edit.html` | Edit phase |
| `/phases/<id>/delete` | POST | - | Delete phase |
| `/evolutions/<eid>/phases/create` | GET, POST | `evolutions/phases/create.html` | Create phase |
| `/evolutions/<eid>/phases/<pid>/edit` | GET, POST | `evolutions/phases/edit.html` | Edit phase |
| `/evolutions/<eid>/phases/<pid>/delete` | POST | - | Delete phase |

### Requirement Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/requirements` | GET | `requirements/index.html` | List requirements |
| `/requirements/create` | GET, POST | `requirements/create.html` | Create requirement |
| `/requirements/<id>` | GET | `requirements/show.html` | View requirement |
| `/requirements/<id>/edit` | GET, POST | `requirements/edit.html` | Edit requirement |
| `/requirements/<id>/delete` | POST | - | Delete requirement |

### Technology Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/technologies` | GET | `technologies/index.html` | List technologies |
| `/technologies/create` | GET, POST | `technologies/create.html` | Create technology |
| `/technologies/<id>` | GET | `technologies/show.html` | View technology |
| `/technologies/<id>/edit` | GET, POST | `technologies/edit.html` | Edit technology |
| `/technologies/<id>/delete` | POST | - | Delete technology |
| `/technologies/<id>/add-version` | GET, POST | `technologies/add_version.html` | Add version |
| `/technologies/<id>/versions` | GET, POST | `technologies/versions.html` | Manage versions |

### Tech Stack Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/techstacks` | GET | `techstacks/index.html` | List tech stacks |
| `/techstacks/create` | GET, POST | `techstacks/create.html` | Create tech stack |
| `/techstacks/<id>` | GET | `techstacks/show.html` | View tech stack |
| `/techstacks/<id>/edit` | GET, POST | `techstacks/edit.html` | Edit tech stack |
| `/techstacks/<id>/delete` | POST | - | Delete tech stack |

### Technology Type Routes

| Route | Method | Template | Description |
|-------|---------|----------|-------------|
| `/technology-types` | GET | `technology_types/index.html` | List types |
| `/technology-types/create` | GET, POST | `technology_types/create.html` | Create type |
| `/technology-types/<id>` | GET | `technology_types/show.html` | View type |
| `/technology-types/<id>/edit` | GET, POST | `technology_types/edit.html` | Edit type |
| `/technology-types/<id>/delete` | POST | - | Delete type |

## UI/UX Features

- Modern, responsive design using Tailwind CSS
- Dual navigation system:
  - Top navbar for quick access
  - Control panel for idea management
- Active state indicators for current page
- Flash messages with dismissal option
- Mobile-friendly layout
- Consistent styling across all pages

## Tech Stack

- **Backend**: Python 3.11, Flask
- **Database**: SQLAlchemy, SQLite
- **Frontend**: 
  - Tailwind CSS for styling
  - Responsive design
  - Modern UI components
- **Development Tools**:
  - Flask-Migrate for database migrations
  - Flask-SQLAlchemy for ORM
  - Python dotenv for configuration

## Project Structure

```
idea-management/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── models/               # Database models
│   ├── core.py          # Core models (Idea, Phase, etc.)
│   └── __init__.py
├── templates/            # Jinja2 templates
│   ├── layouts/         # Base templates and components
│   ├── control_panel/   # Control panel views
│   ├── ideas/           # Idea management views
│   ├── evolutions/      # Evolution cycle views
│   ├── phases/          # Phase management views
│   ├── requirements/    # Requirement management views
│   ├── techstacks/     # Tech stack views
│   └── technologies/    # Technology views
├── static/              # Static assets
│   ├── css/            # Custom CSS
│   └── js/             # JavaScript files
├── migrations/          # Database migrations
└── requirements.txt     # Python dependencies
```

## Installation and Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   ```
5. Run the application:
   ```bash
   flask run
   ```

## Version

Current version: v1.0.0-poc

## Known Issues and Missing Features

### Route and Template Inconsistencies

1. **Routes Without Templates**
   - `/ideas/<id>/tech-stacks/manage` (POST only)
   - `/ideas/<id>/evolution-cycles/<cycle_id>` and its edit/delete routes
   - `/evolutions/<id>/techstacks/<stack_id>/remove` (POST only)
   - `/technologies/<tech_id>/versions/<version_id>/remove` (POST only)

2. **Templates Without Direct Routes**
   - `errors/404.html` and `errors/500.html` (error pages)
   - `layouts/navbar.html` (included in other templates)
   - `evolutions/detail.html` (possibly redundant with show.html)

### Missing Features

1. **User Management**
   - User authentication and authorization
   - User roles and permissions
   - Team collaboration features

2. **Data Management**
   - Bulk import/export of data
   - Data validation rules
   - Data archiving functionality

3. **Integration Features**
   - API endpoints for external integration
   - Webhook support
   - Third-party service integrations

4. **Advanced Features**
   - Search and filtering across all entities
   - Advanced reporting and analytics
   - Custom fields for entities
   - Template support for ideas and requirements

5. **UI/UX Improvements**
   - Rich text editor for descriptions
   - Drag-and-drop interface for ordering
   - Real-time updates
   - Advanced filtering in lists
   - Bulk actions on items
