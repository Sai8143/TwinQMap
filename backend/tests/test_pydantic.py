import pydantic
from pydantic_core import core_schema
print("Pydantic version:", pydantic.__version__)
try:
    print(dir(core_schema))
except Exception as e:
    print("Error:", e)
