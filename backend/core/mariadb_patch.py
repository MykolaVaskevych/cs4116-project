#!/usr/bin/env python
import os
import sys
import re
import django

# Find the path to the Django settings module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Load Django settings
django.setup()

# Function to patch Django's MySQL backend to work with MariaDB 10.4
def patch_django_mysql_backend():
    """
    Patch Django's MySQL backend to bypass the MariaDB version check
    """
    try:
        # Find the path to the Django MySQL backend
        from django.db.backends.mysql import base
        backend_path = base.__file__
        
        print(f"Found MySQL backend at: {backend_path}")
        
        # Read the content of the file
        with open(backend_path, 'r') as file:
            content = file.read()
        
        # Check if the file already contains our patch
        if "# PATCHED FOR MARIADB 10.4" in content:
            print("MySQL backend already patched for MariaDB 10.4")
            return True
            
        # Look for the version check
        pattern = r"(\s+)if mariadb_version_info >= \(10, 5\):([\s\S]+?)else:[\s\S]+?(\s+)raise ImproperlyConfigured\("
        
        # Create the replacement with patched code
        replacement = r"\1# PATCHED FOR MARIADB 10.4\1if True:  # Originally: if mariadb_version_info >= (10, 5):\2else:\3print('WARNING: Using MariaDB 10.4 with Django compatibility patch')"
        
        # Apply the patch
        patched_content = re.sub(pattern, replacement, content)
        
        # Write the patched content back to the file
        with open(backend_path, 'w') as file:
            file.write(patched_content)
            
        print("Successfully patched Django MySQL backend for MariaDB 10.4")
        return True
        
    except Exception as e:
        print(f"Error patching Django MySQL backend: {e}")
        return False

if __name__ == "__main__":
    print("Applying MariaDB 10.4 compatibility patch...")
    
    # Apply the patch
    if patch_django_mysql_backend():
        print("Patch successful. Please run setup_db.py again to complete the setup.")
    else:
        print("Patch failed. Please manually modify Django's MySQL backend.")