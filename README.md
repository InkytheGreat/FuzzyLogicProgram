Fuzzy steering demo

This small demo implements a Mamdani-style fuzzy controller that takes two inputs:
- angle (degrees): negative = goal is to the left, positive = goal is to the right
- distance (units): positive distance to the goal

Output:
- direction: fuzzy output in range [-1, 1] where -1 is full left, 0 is straight, +1 is full right

Files:
- `fuzzy_control.py` - the controller implementation
- `fuzzyExample.py` - demo script that runs sample evaluations and plots membership functions
- `requirements.txt` - minimal dependencies

Run:

1. Create/activate a Python environment (recommended Python 3.8+)
2. Install requirements:

   python -m pip install -r requirements.txt

3. Run the demo:

   python fuzzyExample.py

Notes:
- The demo uses matplotlib for visualization; on headless systems you may need to configure backend or save plots to files.
- The controller is small and intended for learning — you can extend membership shapes and rules as needed.
