# Results

The body+0x28 pointer and +0x38 count initialize to zero. Its first initializer-driven cleanup calls FUN_140e94580, whose loop skips all child entries at count zero. Later child-array writes remain unresolved [EV-0354].
