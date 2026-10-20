# Results

FUN_140b48720 initializes the exact callback pointer/count empty. FUN_140b91bb0's matching +0x40/+0x48 writes target a separate 0xB0/0xD0 constraint-data payload passed into the constructor and stored at instance +0x18. The ProcessTrapHit factory reaches FUN_140ecdfc0, whose direct body has no callback-field store after construction but makes unresolved virtual calls at +0x128/+0x188 [EV-0365].
