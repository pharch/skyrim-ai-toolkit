# Competing models

- H1: matching +0x40/+0x48 writes populate the hkpConstraintInstance callback array.
- H2: the writes belong to a separate constraint-data object passed into constructor +0x18.

Exact receiver identity and constructor argument flow discriminate these models.
