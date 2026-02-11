"""
hash.all - Secure password manager
version 1.0b
"""

import sys
from pathlib import Path


def setup_imports():
    "Add root project dir into sys.path"
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def main():
    "Main function"
    # Setting up imports
    setup_imports()

    try:
        from gui_v2.app import Runtime

        # Creating object and run
        app_instance = Runtime()
        app_instance.run()
    except ImportError as e:
        print(f"Import error: {e}")
        print(
            "Make sure, that you run file from project root and all dependecies are installed"
        )
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)


# Start application
if __name__ == "__main__":
    main()
