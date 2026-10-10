from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/'tools/package_actions_v7.py'),init_globals={'OUT_OVERRIDE':root/'actions-v9'})
