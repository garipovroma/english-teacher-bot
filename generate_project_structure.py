import os

# Define the project structure
project_structure = {
    '.': ['main.py', 'config.py', 'requirements.txt'],
    'handlers': ['__init__.py', 'user_handlers.py', 'admin_handlers.py'],
    'middlewares': ['__init__.py', 'example_middleware.py'],
    'services': ['__init__.py', 'llama_service.py'],
    'utils': ['__init__.py', 'helpers.py'],
    'tests': ['__init__.py', 'test_llama_service.py', 'test_database.py']
}

# Create the project directories and files
for directory, files in project_structure.items():
    if directory == '.':
        for file in files:
            with open(file, 'w') as f:
                pass
    else:
        os.makedirs(directory, exist_ok=True)
        for file in files:
            with open(os.path.join(directory, file), 'w') as f:
                pass

print("Project structure created successfully.")