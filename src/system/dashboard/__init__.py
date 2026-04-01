"""
System Dashboard Module - 系統儀表板模塊
動態、階層和互動式儀表板
"""

__version__ = "1.0.0"

try:
    from . import dynamic_dashboard
    from . import hierarchical_dashboard
    from . import interactive_dashboard
    __all__ = ['dynamic_dashboard', 'hierarchical_dashboard', 'interactive_dashboard']
except ImportError:
    __all__ = []
