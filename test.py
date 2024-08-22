import sys
import os
import site

# Obtenez le chemin du site-packages
site_packages = site.getsitepackages()[0]

# Ajoutez le chemin de pywin32_system32 au PATH
pywin32_path = os.path.join(site_packages, 'pywin32_system32')
if os.path.exists(pywin32_path):
    os.environ['PATH'] = f"{pywin32_path};{os.environ['PATH']}"
    sys.path.append(pywin32_path)
    print(f"Added {pywin32_path} to PATH")
else:
    print("pywin32_system32 directory not found")