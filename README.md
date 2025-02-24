# Idea Management

A comprehensive web application for managing ideas, their evolution cycles, and associated technical requirements.

## Description

Idea Management is a Flask-based web application that helps you organize and track your ideas from conception to implementation. It provides a structured way to manage ideas, their evolution cycles, phases, requirements, and technical specifications.

## Features

### Core Features

#### Ideas Management
- Create, view, edit, and delete ideas
- Track idea status and evolution
- Associate ideas with tech stacks

#### Evolution Cycles
- Organize idea development into evolution cycles
- Track cycle progress and status
- Link cycles to specific phases

#### Phases Management
- Create and manage development phases
- Order phases sequentially
- Associate requirements with phases
- Track phase completion status

#### Requirements Management
- Define and categorize requirements
- Set requirement priorities
- Link requirements to phases
- Track requirement status

#### Tech Stack Management
- Create and manage tech stacks
- Associate technologies with tech stacks
- Link tech stacks to ideas

#### Technologies Management
- Maintain a catalog of technologies
- Track technology usage across tech stacks
- View technology relationships

### UI/UX Features

- Modern, responsive design using Tailwind CSS
- Dual navigation system:
  - Top navbar for quick access
  - Sidebar for hierarchical navigation
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

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd idea-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

   The application will be available at `http://localhost:5000`

## Database Models

- **Idea**: Core concept being developed
- **EvolutionCycle**: Development iteration of an idea
- **Phase**: Stage within an evolution cycle
- **Requirement**: Specific need or feature
- **RequirementType**: Categorization of requirements
- **RequirementPriority**: Priority level of requirements
- **Status**: Current state of various entities
- **TechStack**: Collection of technologies
- **Technology**: Individual technology or tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Status

Current status: Beta
- All core features implemented
- UI/UX improvements ongoing
- Ready for testing and feedback
