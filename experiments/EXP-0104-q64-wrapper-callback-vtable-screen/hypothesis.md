# Competing models

- H1: wrapper setup or its exact hkpConstraintInstance constructors populate callback pointer/count after initialization.
- H2: the traced path links wrapper state and adjusts references; callback population requires a distinct writer or later event.

Receiver identity and exact machine-level write semantics discriminate these models.
