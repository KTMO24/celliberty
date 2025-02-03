import os
from IPython import get_ipython

# The full source code for the cell library functionality.
cell_library_source = r'''"""
cell_library.py

A simple library to treat Jupyter cells as “library” modules.

Usage:
  1. Mark a cell as a library cell:
  
     %%library my_lib
     def hello():
         print("Hello from my_lib!")
     
  2. Import a library cell into another cell:
  
     %import_library my_lib
     hello()  # prints: Hello from my_lib!
     
  3. Export a library cell to a .py file:
  
     %export_library my_lib my_lib.py
     
  4. (Optional) Inject an export button into the Notebook interface.
"""

import os
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import display, HTML, Javascript
from IPython import get_ipython

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
        # Execute the library cell code in the caller's global namespace.
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

# Register our magics so they are available in the notebook.
ip = get_ipython()
if ip:
    ip.register_magics(CellLibraryMagics)

# Optional: Inject a simple export button into the notebook interface.
def inject_export_button(lib_name):
    """
    Injects a button into the Jupyter notebook that, when clicked,
    calls a JavaScript function to trigger an export of the given library.
    
    Note: For demonstration purposes. In a real scenario, you might tie this
    to a Python callback via a server extension.
    """
    button_id = f"export-btn-{lib_name}"
    js_code = f"""
    (function() {{
        // Create a new button element
        var btn = document.createElement('button');
        btn.id = '{button_id}';
        btn.innerHTML = 'Export Library: {lib_name}';
        btn.style.margin = '5px';
        btn.onclick = function() {{
            // In a real extension, you might trigger a Python callback here.
            alert("This is where export logic would run for library: {lib_name}");
        }};
        // Append the button to the toolbar (or any other DOM element)
        var toolbar = document.querySelector('#maintoolbar-container') || document.body;
        toolbar.appendChild(btn);
    }})();
    """
    display(Javascript(js_code))
'''

# Define the file path where the library code will be saved.
install_path = os.path.join(os.getcwd(), "cell_library.py")

# Write the cell library source code to the file.
with open(install_path, "w", encoding="utf-8") as f:
    f.write(cell_library_source)

print(f"Installation complete: 'cell_library.py' has been written to {install_path}")

# Load the newly created module into the current notebook.
get_ipython().run_line_magic("run", "cell_library.py")

print("cell_library module loaded. You can now use the following magics and function:")
print("  - '%%library <lib_name>' to define a library cell")
print("  - '%import_library <lib_name>' to import a library cell")
print("  - '%export_library <lib_name> <file_path>' to export a library cell to a Python file")
print("  - 'inject_export_button(<lib_name>)' to add an export button to the notebook UI")
