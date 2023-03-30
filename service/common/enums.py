from enum import Enum


class CustomerStatus(Enum):
    """Enum representing the status of a Customer"""
    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'

    def __str__(self):
        """Returns the string representation of the CustomerStatus"""
        return self.value

    @classmethod
    def from_string(cls, label: str):
        """Converts a string to a CustomerStatus"""
        if not label:
            return None
        try:
            return cls[label.upper()]
        except KeyError as exc:
            raise ValueError(f'Invalid CustomerStatus: {label}') from exc

    @classmethod
    def string_equals(cls, label, other):
        """Compares a string to a CustomerStatus"""
        return cls.from_string(label) == other
