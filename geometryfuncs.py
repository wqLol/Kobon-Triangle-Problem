from decimal import Decimal, getcontext

getcontext().prec = 50 

class Vec2:
    """
    A 2D vector or point class using Decimal for precise floating-point arithmetic.
    """
    def __init__(self, x: Decimal = Decimal(0), y: Decimal = Decimal(0)):

        self.x: Decimal = Decimal(x) 
        self.y: Decimal = Decimal(y)

    def __str__(self) -> str:
        """String representation for printing."""
        return f"Vec2(x={self.x}, y={self.y})"

    def __repr__(self) -> str:
        """Official string representation for debugging."""
        return self.__str__()


    def __add__(self, other: 'Vec2') -> 'Vec2':
        """Vector addition: self + other."""
        if not isinstance(other, Vec2):
            return NotImplemented
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2') -> 'Vec2':
        """Vector subtraction: self - other."""
        if not isinstance(other, Vec2):
            return NotImplemented
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Decimal) -> 'Vec2':
        """Scalar multiplication: self * scalar."""
        if not isinstance(scalar, (Decimal, int, float)): # Allow int/float for convenience, but convert to Decimal
            return NotImplemented
        scalar_dec = Decimal(scalar)
        return Vec2(self.x * scalar_dec, self.y * scalar_dec)

    def __rmul__(self, scalar: Decimal) -> 'Vec2':
        """Reverse scalar multiplication: scalar * self."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Decimal) -> 'Vec2':
        """Scalar division: self / scalar."""
        if not isinstance(scalar, (Decimal, int, float)):
            return NotImplemented
        scalar_dec = Decimal(scalar)
        if scalar_dec == Decimal(0):
            raise ZeroDivisionError("Cannot divide Vec2 by zero.")
        return Vec2(self.x / scalar_dec, self.y / scalar_dec)


    def dot(self, other: 'Vec2') -> Decimal:
        """Dot product with another vector."""
        if not isinstance(other, Vec2):
            return NotImplemented
        return self.x * other.x + self.y * other.y

    def magnitude(self) -> Decimal:
        """Calculates the Euclidean magnitude (length) of the vector."""
        return (self.x**2 + self.y**2).sqrt()

    @staticmethod
    def dist(p1: 'Vec2', p2: 'Vec2') -> Decimal:
        """Calculates the Euclidean distance between two Vec2 points."""

        return (p1 - p2).magnitude()

    def normalize(self) -> 'Vec2':
        """Returns a normalized version of the vector (unit vector)."""
        mag = self.magnitude()
        if mag == Decimal(0):
            raise ValueError("Cannot normalize a zero vector.")
        return Vec2(self.x / mag, self.y / mag)


    def __eq__(self, other: object) -> bool:
        """Checks if two Vec2 objects are equal."""
        if not isinstance(other, Vec2):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Allows Vec2 objects to be used in sets or as dictionary keys."""
        return hash((self.x, self.y))


def getEquation(p1: Vec2, p2: Vec2) -> tuple[Decimal, Decimal, Decimal]:
    """
    Calculates the coefficients A, B, and C for the line equation Ax + By + C = 0
    passing through two Vec2 points p1 and p2.

    Args:
        p1 (Vec2): The first point on the line.
        p2 (Vec2): The second point on the line.

    Returns:
        tuple[Decimal, Decimal, Decimal]: A tuple (A, B, C) representing the line equation.
    """
    A = p2.y - p1.y
    B = p1.x - p2.x
    C = -(A * p1.x + B * p1.y)
    
    return A, B, C