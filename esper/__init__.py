# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from .world import CachedWorld, World
from .templates import Processor

from .meta import (author as __author__,
                   version as __version__,
                   license as __license__)

__copyright__ = __author__

__all__ = ("CachedWorld", "Processor", "World")
