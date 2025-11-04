"""
hash.all - Secure password manager
ver 0.1.1a
"""

import sys
import os
from pathlib import Path


def setup_imports():

    # Get the full path to the project dir
    project_root = Path(__file__).parent.absolute()

    # Add this to sys.path if not in it
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Check avaliable modules / logs if error
    try:
        ...  # placeholder
    except ImportError as e:
        print(f"Import error: {e}")
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.path}")
        return False


def main():

    # Fail message
    if not setup_imports():
        print(
            "Failed to setup imports. Please check\n1. All required files are present\n2. You have necessary permissions"
        )

    # Trying to initialize window / logs if error
    try:
        ...  # placeholder
    except Exception as e:
        print(f"Critial error: {e}")
        sys.exit(1)


# Start application
if __name__ == "__main__":
    main()
