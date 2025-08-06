"""
File Manager Package

Provides utilities for managing files, directories, compression, synchronization,
hashing, and monitoring with a progress bar.
"""

from .progress import ProgressPercentage
from .file_ops import *
from .zip_ops import *
from .hash_ops import *
from .search_ops import *
from .stats_ops import *
from .sync_ops import *
from .monitor_ops import *
from .temp_file_utils import *

__all__ = [
    "ProgressPercentage",
] + file_ops.__all__ + zip_ops.__all__ + hash_ops.__all__ + search_ops.__all__ + stats_ops.__all__ + sync_ops.__all__ + monitor_ops.__all__ + temp_file_utils.__all__
