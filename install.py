import os
import sys
import types
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import display, Javascript

###############################
# CELL LIBRARY CORE DEFINITION
###############################

# Global registry to store library cell code by name.
_LIBRARY_REGISTRY = {}

@magics_class
class CellLibraryMagics(Magics):

    @cell_magic
    def library(self, line, cell):
        """
        Mark the current cell as a library cell.
        Usage:
            %%library <library_name>
            # Your code here...
        The cell's code is stored under the given name.
        """
        lib_name = line.strip()
        if not lib_name:
            print("Please provide a library name. Usage: %%library <library_name>")
            return
        _LIBRARY_REGISTRY[lib_name] = cell
        print(f"Library cell '{lib_name}' stored successfully.")

    @line_magic
    def import_library(self, line):
        """
        Import a library cell by name.
        Usage:
            %import_library <library_name>
        The code of the library cell is executed in the caller's global scope.
        """
        lib_name = line.strip()
        if lib_name not in _LIBRARY_REGISTRY:
            print(f"Library '{lib_name}' not found. Please define it with %%library first.")
            return
        code = _LIBRARY_REGISTRY[lib_name]
        caller_globals = self.shell.user_ns
        try:
            exec(code, caller_globals)
            print(f"Library '{lib_name}' imported successfully.")
        except Exception as e:
            print(f"Error importing library '{lib_name}': {e}")

    @line_magic
    def export_library(self, line):
        """
        Export a library cell to a Python file.
        Usage:
            %export_library <library_name> <file_path>
        The cell's code is written to the given file.
        """
        parts = line.strip().split()
        if len(parts) != 2:
            print("Usage: %export_library <library_name> <file_path>")
            return
        lib_name, file_path = parts
        if lib_name not in _LIBRARY_REGISTRY:
            print(f"Library '{lib_name}' not found. Please define it with %%library first.")
            return
        code = _LIBRARY_REGISTRY[lib_name]
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"Library '{lib_name}' exported to '{file_path}'.")
        except Exception as e:
            print(f"Error exporting library '{lib_name}': {e}")

# Register the magics so they are available in the notebook.
ip = get_ipython()
if ip:
    ip.register_magics(CellLibraryMagics)

##########################################
# CUSTOM IMPORT HOOK: FINDER & LOADER
##########################################

class CellLibraryLoader:
    """
    A loader that creates a module from a library cell.
    """
    def __init__(self, lib_name, code):
        self.lib_name = lib_name
        self.code = code

    def create_module(self, spec):
        # Use default module creation semantics.
        return None

    def exec_module(self, module):
        try:
            exec(self.code, module.__dict__)
        except Exception as e:
            raise ImportError(f"Error loading cell library '{self.lib_name}': {e}")

class CellLibraryFinder:
    """
    A meta path finder that looks for modules in _LIBRARY_REGISTRY.
    It supports:
      - import cell.<lib_name>
      - from cell.<lib_name> import *
    It also optionally supports aliasing (see note below).
    """
    def find_spec(self, fullname, path, target=None):
        # We handle module names that start with "cell." or exactly "cell"
        parts = fullname.split('.')
        if parts[0] == "cell":
            # If fullname is exactly "cell", we create a pseudo-package that lists available libraries.
            if len(parts) == 1:
                spec = types.ModuleType(fullname)
                spec.__package__ = fullname
                spec.__spec__ = None
                # We add an __all__ attribute for convenience.
                spec.__all__ = list(_LIBRARY_REGISTRY.keys())
                sys.modules[fullname] = spec
                return None  # Returning None defers to normal import behavior.
            elif len(parts) == 2:
                lib_name = parts[1]
                if lib_name in _LIBRARY_REGISTRY:
                    from importlib.machinery import ModuleSpec
                    code = _LIBRARY_REGISTRY[lib_name]
                    loader = CellLibraryLoader(lib_name, code)
                    spec = ModuleSpec(fullname, loader, is_package=False)
                    return spec
        else:
            # Optionally, if the fullname itself matches a key in _LIBRARY_REGISTRY,
            # then allow direct import (e.g., "import testing" if "testing" is a cell).
            if fullname in _LIBRARY_REGISTRY:
                from importlib.machinery import ModuleSpec
                code = _LIBRARY_REGISTRY[fullname]
                loader = CellLibraryLoader(fullname, code)
                spec = ModuleSpec(fullname, loader, is_package=False)
                return spec
        return None

# Insert the finder at the front of sys.meta_path so it takes priority.
if not any(isinstance(f, CellLibraryFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, CellLibraryFinder())

##########################################
# OPTIONAL: UI BUTTON FOR EXPORT
##########################################

def inject_export_button(lib_name):
    """
    Injects a button into the Jupyter notebook that, when clicked,
    calls a JavaScript function to trigger an export of the given library.
    
    Note: For demonstration purposes only.
    """
    button_id = f"export-btn-{lib_name}"
    js_code = f"""
    (function() {{
        var btn = document.createElement('button');
        btn.id = '{button_id}';
        btn.innerHTML = 'Export Library: {lib_name}';
        btn.style.margin = '5px';
        btn.onclick = function() {{
            alert("Export logic for library: {lib_name} would run here.");
        }};
        var toolbar = document.querySelector('#maintoolbar-container') || document.body;
        toolbar.appendChild(btn);
    }})();
    """
    display(Javascript(js_code))

##########################################
# WRITE OUT THE MODULE (INSTALLER)
##########################################

# Combine all the above source code into a string.
cell_library_source = r'''import os
import sys
import types
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import display, Javascript

# Global registry to store library cell code by name.
_LIBRARY_REGISTRY = {}

@magics_class
class CellLibraryMagics(Magics):

    @cell_magic
    def library(self, line, cell):
        lib_name = line.strip()
        if not lib_name:
            print("Please provide a library name. Usage: %%library <library_name>")
            return
        _LIBRARY_REGISTRY[lib_name] = cell
        print(f"Library cell '{lib_name}' stored successfully.")

    @line_magic
    def import_library(self, line):
        lib_name = line.strip()
        if lib_name not in _LIBRARY_REGISTRY:
            print(f"Library '{lib_name}' not found. Please define it with %%library first.")
            return
        code = _LIBRARY_REGISTRY[lib_name]
        caller_globals = self.shell.user_ns
        try:
            exec(code, caller_globals)
            print(f"Library '{lib_name}' imported successfully.")
        except Exception as e:
            print(f"Error importing library '{lib_name}': {e}")

    @line_magic
    def export_library(self, line):
        parts = line.strip().split()
        if len(parts) != 2:
            print("Usage: %export_library <library_name> <file_path>")
            return
        lib_name, file_path = parts
        if lib_name not in _LIBRARY_REGISTRY:
            print(f"Library '{lib_name}' not found. Please define it with %%library first.")
            return
        code = _LIBRARY_REGISTRY[lib_name]
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"Library '{lib_name}' exported to '{file_path}'.")
        except Exception as e:
            print(f"Error exporting library '{lib_name}': {e}")

ip = get_ipython()
if ip:
    ip.register_magics(CellLibraryMagics)

class CellLibraryLoader:
    def __init__(self, lib_name, code):
        self.lib_name = lib_name
        self.code = code

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        try:
            exec(self.code, module.__dict__)
        except Exception as e:
            raise ImportError(f"Error loading cell library '{self.lib_name}': {e}")

class CellLibraryFinder:
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split('.')
        if parts[0] == "cell":
            if len(parts) == 1:
                spec = types.ModuleType(fullname)
                spec.__package__ = fullname
                spec.__spec__ = None
                spec.__all__ = list(_LIBRARY_REGISTRY.keys())
                sys.modules[fullname] = spec
                return None
            elif len(parts) == 2:
                lib_name = parts[1]
                if lib_name in _LIBRARY_REGISTRY:
                    from importlib.machinery import ModuleSpec
                    code = _LIBRARY_REGISTRY[lib_name]
                    loader = CellLibraryLoader(lib_name, code)
                    spec = ModuleSpec(fullname, loader, is_package=False)
                    return spec
        else:
            if fullname in _LIBRARY_REGISTRY:
                from importlib.machinery import ModuleSpec
                code = _LIBRARY_REGISTRY[fullname]
                loader = CellLibraryLoader(fullname, code)
                spec = ModuleSpec(fullname, loader, is_package=False)
                return spec
        return None

if not any(isinstance(f, CellLibraryFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, CellLibraryFinder())

def inject_export_button(lib_name):
    button_id = f"export-btn-{lib_name}"
    js_code = f\"
    (function() {{
        var btn = document.createElement('button');
        btn.id = '{button_id}';
        btn.innerHTML = 'Export Library: {lib_name}';
        btn.style.margin = '5px';
        btn.onclick = function() {{
            alert("Export logic for library: {lib_name} would run here.");
        }};
        var toolbar = document.querySelector('#maintoolbar-container') || document.body;
        toolbar.appendChild(btn);
    }})();
    \"
    display(Javascript(js_code))
'''

# Define the installation path.
install_path = os.path.join(os.getcwd(), "cell_library.py")

with open(install_path, "w", encoding="utf-8") as f:
    f.write(cell_library_source)

print(f"Installation complete: 'cell_library.py' has been written to {install_path}")

# Load the newly created module into the current notebook.
get_ipython().run_line_magic("run", "cell_library.py")

print("cell_library module loaded.")
print("You may now use the following in your notebook:")
print("  - '%%library <lib_name>' to define a library cell")
print("  - '%import_library <lib_name>' to import a library cell")
print("  - '%export_library <lib_name> <file_path>' to export a library cell")
print("  - Standard import syntax such as:")
print("       import cell.test         (loads the cell library named 'test')")
print("       from cell.4 import *      (loads the cell library named '4')")
print("  - Optionally, 'inject_export_button(<lib_name>)' to add a UI export button")
