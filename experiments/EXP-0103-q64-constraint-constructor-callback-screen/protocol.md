# Protocol

Validate the constructor caller census and query identity. Trace each +0x40/+0x48 store's base object and the hkpConstraintInstance constructor arguments. Then follow exact ProcessTrapHit wrapper virtual slots +0x128/+0x188; constructor-zero state alone is not a no-writer result.
