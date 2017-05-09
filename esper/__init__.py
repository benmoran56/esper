from .world import World, CachedWorld
from .templates import Processor

from .meta import (author as __author__,
                   version as __version__,
                   license as __license__)

__copyright__ = __author__

__all__ = ("Processor", "World", "CachedWorld")
