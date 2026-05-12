"""Execute the term-project notebook in place, capturing any cell error."""
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

PROJ = Path(__file__).parent
NB = PROJ / "DTSC610 Term Project - Correlation Analysis of Life Expectancy and Different Variables.ipynb"

print(f"Executing: {NB.name}")
nb = nbformat.read(NB, as_version=4)
ep = ExecutePreprocessor(timeout=180, kernel_name="python3")
try:
    ep.preprocess(nb, {"metadata": {"path": str(PROJ)}})
    nbformat.write(nb, NB)
    print(f"OK - {len(nb.cells)} cells executed, written back.")
except CellExecutionError as e:
    nbformat.write(nb, NB)
    print("FAILED during execution:")
    print(e)
