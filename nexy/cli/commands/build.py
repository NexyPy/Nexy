from nexy.__version__ import __Version__
from nexy.builder import Builder


def build():
    version = __Version__().get()
    print(f"> nexy@{version} dev")

    print("ŋ compile...")
    Builder().build()