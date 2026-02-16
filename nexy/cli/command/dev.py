import os
from typing import Optional

import uvicorn
from nexy.__version__ import __Version__
from nexy.builder import Builder

import multiprocessing
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from nexy.compiler import Compiler
from nexy.nexyconfig import NexyConfig

class State:
    def __init__(self, initial):
        self.value = initial 
    def get(self):
        return self.value
    def set(self, new_value):
        self.value = new_value


class MonHandler(PatternMatchingEventHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_event_time = 0
        self.last_path = ""
        self.count = State(0)
        self.compiler = Compiler()

    def should_trigger(self, path):
        """Vérifie si assez de temps s'est écoulé pour le même fichier."""
        current_time = time.time()
        # Si c'est le même fichier et qu'il s'est écoulé moins de 0.1s, on ignore
        if path == self.last_path and (current_time - self.last_event_time) < 0.1:
            return False
        
        self.last_event_time = current_time
        self.last_path = path
        return True

    def _compile(self, path):
        if path.endswith(".nexy") or path.endswith(".mdx"):
            print(f"ŋ compile : {path}")
            self.compiler.compile(path)
        
    def on_modified(self, event):
        if self.should_trigger(event.src_path):
            if  event.src_path.startswith(("./.git/", "./.venv/", "./__nexy__/", "./__pycache__/", "./venv/", "./node_modules/")):
                pass
            print(f"File : '{event.src_path}' is updated")
            self._compile(event.src_path)

    def on_deleted(self, event):
        if self.should_trigger(event.src_path):
            compiled_path = event.src_path
            template_path = event.src_path
            if event.src_path.endswith(".nexy"):
                compiled_path = NexyConfig.NAMESPACE + event.src_path.replace(".nexy", ".py")
                template_path = NexyConfig.NAMESPACE + event.src_path.replace(".nexy", ".html")
            elif event.src_path.endswith(".mdx"):
                compiled_path = NexyConfig.NAMESPACE + event.src_path.replace(".mdx", ".py")
                template_path = NexyConfig.NAMESPACE + event.src_path.replace(".mdx", ".md")
            if os.path.exists(compiled_path) and event.src_path.endswith((".nexy", ".mdx")):
                os.remove(compiled_path)
                os.remove(template_path)
                print(f"File : '{event.src_path}' is deleted")
            
            
                
               

def dev(port:Optional[int] = None):
    path = "."
    extensions = ["*.py", "*.mdx", "*.nexy"]
    exclusions = ["*/.git/*", "*./.venv/*", "*./__nexy__/*", "*/__pycache__/*", "*/venv/*", "*/.venv/*", "*/__nexy__/*", "*/node_modules/*", "*.tmp"]
    
    version = __Version__().get()
    print(f"> nexy@{version} dev")

    print("ŋ compile...")
    Builder().build()

    event_handler = MonHandler(
        patterns=extensions,
        ignore_patterns=exclusions,
        ignore_directories=True
    )
    
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    uvicorn.run("nexy.server.app:_server", host="0.0.0.0", port=8000, reload=False)
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
