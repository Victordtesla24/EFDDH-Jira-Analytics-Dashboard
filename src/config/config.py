from typing import Dict, List, Optional, Union, Any

try:
    import matplotlib
    matplotlib.use("Agg")
except ImportError:
    print("Error: matplotlib is not installed. Please run: pip install matplotlib")
    exit(1)
