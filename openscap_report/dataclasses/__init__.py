try:
    from dataclasses import dataclass, asdict, field, replace
except ImportError:
    from .dataclasses import dataclass, asdict, field, replace
