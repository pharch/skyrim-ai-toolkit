# Results

FUN_140736be0 loads the named resource `Actors\\Character\\1stPerson\\Skel` through FUN_140e05900; the generic loader prepends `meshes\\` and obtains a reference-counted object from a resource handle member at +0x28. FUN_140736be0 stores the object at PlayerCharacter+0x8F8 and uses virtual slots +0x28 and +0x150. The NIF root class and exact slot +0x8 target remain unknown [EV-0347].
