"""
Automated Project Structure Creator for AI Productivity Suite
Run this script to create the complete folder structure and placeholder files
"""

import os
from pathlib import Path


def create_directory_structure():
    """Create the complete project directory structure."""
    
    # Define the project structure
    structure = {
        'config': ['__init__.py', 'settings.py', 'logging_config.py'],
        'src': ['__init__.py', 'main.py'],
        'src/agents': ['__init__.py', 'base_agent.py', 'task_manager_agent.py', 
                       'calendar_agent.py', 'email_agent.py', 'note_agent.py',
                       'analytics_agent.py', 'priority_agent.py'],
        'src/tools': ['__init__.py', 'google_search_tool.py', 'code_execution_tool.py',
                      'calendar_api_tool.py', 'email_api_tool.py', 'notification_tool.py'],
        'src/memory': ['__init__.py', 'session_manager.py', 'memory_bank.py', 'vector_store.py'],
        'src/models': ['__init__.py', 'schemas.py', 'database.py'],
        'src/orchestration': ['__init__.py', 'agent_orchestrator.py', 'workflow_engine.py'],
        'src/observability': ['__init__.py', 'telemetry.py', 'metrics.py'],
        'src/utils': ['__init__.py', 'helpers.py', 'validators.py'],
        'scripts': ['__init__.py', 'setup_db.py', 'seed_data.py'],
        'tests': ['__init__.py', 'test_agents.py', 'test_tools.py', 'test_workflows.py'],
        'docs': ['architecture.md', 'api_docs.md'],
        'data': [],
        'data/chroma': [],
        'logs': ['.gitkeep'],
    }
    
    # Root files
    root_files = [
        'README.md',
        'QUICKSTART.md',
        'COMPLETE_SETUP_GUIDE.md',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'docker-compose.yml',
        'Dockerfile',
        'init_project.sh',
    ]
    
    print("=" * 60)
    print("AI Productivity Suite - Project Structure Creator")
    print("=" * 60)
    print()
    
    # Get current directory
    base_path = Path.cwd()
    print(f"Creating project structure in: {base_path}")
    print()
    
    # Create directories and files
    created_dirs = []
    created_files = []
    
    # Create directory structure
    for directory, files in structure.items():
        dir_path = base_path / directory
        
        # Create directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)
            print(f"✓ Created directory: {directory}/")
        
        # Create files in directory
        for file in files:
            file_path = dir_path / file
            if not file_path.exists():
                file_path.touch()
                created_files.append(f"{directory}/{file}")
                print(f"  ✓ Created file: {directory}/{file}")
    
    # Create root files
    print()
    print("Creating root files...")
    for file in root_files:
        file_path = base_path / file
        if not file_path.exists():
            file_path.touch()
            created_files.append(file)
            print(f"✓ Created file: {file}")
    
    # Create a simple project info file
    info_file = base_path / 'PROJECT_INFO.txt'
    with open(info_file, 'w') as f:
        f.write("AI Personal Productivity & Workflow Suite\n")
        f.write("=" * 50 + "\n\n")
        f.write("Project Structure Created Successfully!\n\n")
        f.write(f"Total Directories: {len(created_dirs)}\n")
        f.write(f"Total Files: {len(created_files)}\n\n")
        f.write("Next Steps:\n")
        f.write("1. Copy code from artifacts into respective files\n")
        f.write("2. Install dependencies: pip install -r requirements.txt\n")
        f.write("3. Configure .env file with your API keys\n")
        f.write("4. Run: python scripts/setup_db.py\n")
        f.write("5. Run: python src/main.py\n\n")
        f.write("For detailed instructions, see README.md\n")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Created {len(created_dirs)} directories")
    print(f"✓ Created {len(created_files)} files")
    print(f"✓ Project structure ready at: {base_path}")
    print()
    print("Next steps:")
    print("1. Copy code from provided artifacts into each file")
    print("2. See PROJECT_INFO.txt for setup instructions")
    print("3. Review QUICKSTART.md for quick setup guide")
    print("=" * 60)


def print_tree_structure():
    """Print a visual tree structure of the project."""
    print()
    print("=" * 60)
    print("Project Tree Structure")
    print("=" * 60)
    print("""
productivity-suite/
│
├── 📄 README.md
├── 📄 QUICKSTART.md
├── 📄 COMPLETE_SETUP_GUIDE.md
├── 📄 requirements.txt
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 init_project.sh
│
├── 📁 config/
│   ├── __init__.py
│   ├── settings.py
│   └── logging_config.py
│
├── 📁 src/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── 📁 agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── task_manager_agent.py
│   │   ├── calendar_agent.py
│   │   ├── email_agent.py
│   │   ├── note_agent.py
│   │   ├── analytics_agent.py
│   │   └── priority_agent.py
│   │
│   ├── 📁 tools/
│   │   ├── __init__.py
│   │   ├── google_search_tool.py
│   │   ├── code_execution_tool.py
│   │   ├── calendar_api_tool.py
│   │   ├── email_api_tool.py
│   │   └── notification_tool.py
│   │
│   ├── 📁 memory/
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── memory_bank.py
│   │   └── vector_store.py
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── database.py
│   │
│   ├── 📁 orchestration/
│   │   ├── __init__.py
│   │   ├── agent_orchestrator.py
│   │   └── workflow_engine.py
│   │
│   ├── 📁 observability/
│   │   ├── __init__.py
│   │   ├── telemetry.py
│   │   └── metrics.py
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
│
├── 📁 scripts/
│   ├── __init__.py
│   ├── setup_db.py
│   └── seed_data.py
│
├── 📁 tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_workflows.py
│
├── 📁 docs/
│   ├── architecture.md
│   └── api_docs.md
│
├── 📁 data/
│   └── 📁 chroma/
│
└── 📁 logs/
    └── .gitkeep
    """)
    print("=" * 60)


if __name__ == "__main__":
    try:
        create_directory_structure()
        print_tree_structure()
        print("\n✅ Project structure created successfully!")
        print("\n📝 Now copy the code from each artifact into the corresponding file.")
        print("   You can find all the code in the chat artifacts above.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure you have write permissions in the current directory.")