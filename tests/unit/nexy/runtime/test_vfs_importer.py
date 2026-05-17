import sys
import pytest
from nexy.utils.fs.vfs import VFS
from nexy.runtime.importer import install_vfs_importer

def test_vfs_import():
    vfs = VFS()
    vfs.clear()
    
    # Create a virtual module
    module_code = "def hello(): return 'world'"
    vfs.write("__nexy__/test_module.py", module_code)
    vfs.write("__nexy__/__init__.py", "")
    
    install_vfs_importer()
    
    # Import the virtual module
    import __nexy__.test_module
    assert __nexy__.test_module.hello() == 'world'
    
    # Update the module in VFS
    vfs.write("__nexy__/test_module.py", "def hello(): return 'updated'")
    
    # Invalidation (Task 03 will handle this more robustly, but let's test)
    if "__nexy__.test_module" in sys.modules:
        del sys.modules["__nexy__.test_module"]
        
    import __nexy__.test_module
    import importlib
    importlib.reload(__nexy__.test_module)
    assert __nexy__.test_module.hello() == 'updated'

def test_vfs_package():
    vfs = VFS()
    vfs.write("__nexy__/pkg/__init__.py", "X = 1")
    vfs.write("__nexy__/pkg/sub.py", "Y = 2")
    
    install_vfs_importer()
    
    from __nexy__.pkg import X
    from __nexy__.pkg.sub import Y
    
    assert X == 1
    assert Y == 2
