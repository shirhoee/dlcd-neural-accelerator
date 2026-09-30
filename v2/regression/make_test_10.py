import os
import sys

with open("harness.py", "r") as f:
    code = f.read()
    
# Modify to run only 10 images
code = code.replace("for i in range(10000):", "for i in range(10):")
code = code.replace("Total Images\": 10000", "Total Images\": 10")

with open("test_10.py", "w") as f:
    f.write(code)
