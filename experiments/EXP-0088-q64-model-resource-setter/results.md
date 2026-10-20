# Results

FUN_1407445d0 selects +0x9A8 when its mode is zero and +0x9A0 otherwise, retains the incoming pointer, and final-releases the replaced pointer through dynamic slot +0x8. One caller passes the model-resource output from FUN_140216b40; the object's class and destructor remain unresolved [EV-0350], [EV-0349].
