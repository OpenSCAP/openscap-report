try:
    from dataclasses import asdict, dataclass, field, replace
except ImportError:
    from .dataclasses import asdict, dataclass, field, replace
