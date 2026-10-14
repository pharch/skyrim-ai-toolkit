#!/usr/bin/env python3
"""Read-only Skyrim AE PEX inspection and narrow script-BSA research helpers.

The bytecode reader supports classic PEX 3.2 value and opcode forms. It is a
bounded inspection aid, not a complete Papyrus decompiler. Archive extraction
uses the verified local Skyrim data path and writes only below ignored
``.local/`` storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
from pathlib import Path, PureWindowsPath
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config  # noqa: E402

MAGIC = b"\xFA\x57\xC0\xDE"
OPCODES = [
    "NOP", "IADD", "FADD", "ISUB", "FSUB", "IMUL", "FMUL", "IDIV",
    "FDIV", "IMOD", "NOT", "INEG", "FNEG", "ASSIGN", "CAST",
    "CMP_EQ", "CMP_LT", "CMP_LTE", "CMP_GT", "CMP_GTE", "JMP", "JMPT",
    "JMPF", "CALLMETHOD", "CALLPARENT", "CALLSTATIC", "RETURN", "STRCAT",
    "PROPGET", "PROPSET", "ARRAY_CREATE", "ARRAY_LENGTH", "ARRAY_GET",
    "ARRAY_SET", "ARRAY_FIND", "ARRAY_RFIND", "IS",
]
FIXED = {
    0: 0, 1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3,
    10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 3, 16: 3, 17: 3, 18: 3,
    19: 3, 20: 1, 21: 2, 22: 2, 24: 3, 26: 1, 27: 3, 28: 3, 29: 3,
    30: 2, 31: 2, 32: 3, 33: 3, 34: 4, 35: 4, 36: 3,
}
TARGET_ACTOR_VALUES = (
    "AlterationPowerModifier", "ConjurationPowerModifier",
    "DestructionPowerModifier", "IllusionPowerModifier",
    "RestorationPowerModifier", "MarksmanPowerModifier",
)


class PexFormatError(ValueError):
    """The input is truncated, malformed, or uses an unsupported PEX form."""


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.strings: list[str] = []
        self.lines: list[str] = []

    def need(self, size: int) -> None:
        if size < 0 or self.pos + size > len(self.data):
            raise PexFormatError(
                f"truncated PEX at 0x{self.pos:X}: need {size} bytes, "
                f"have {max(0, len(self.data) - self.pos)}"
            )

    def u8(self) -> int:
        self.need(1)
        value = self.data[self.pos]
        self.pos += 1
        return value

    def u16(self) -> int:
        self.need(2)
        value = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return value

    def u32(self) -> int:
        self.need(4)
        value = struct.unpack_from(">I", self.data, self.pos)[0]
        self.pos += 4
        return value

    def u64(self) -> int:
        self.need(8)
        value = struct.unpack_from(">Q", self.data, self.pos)[0]
        self.pos += 8
        return value

    def raw_string(self) -> str:
        size = self.u16()
        self.need(size)
        value = self.data[self.pos:self.pos + size].decode("utf-8", "replace")
        self.pos += size
        return value

    def string(self) -> str:
        index = self.u16()
        if index >= len(self.strings):
            raise PexFormatError(f"string index {index} outside table of {len(self.strings)}")
        return self.strings[index]

    def value(self) -> tuple[str, object]:
        kind = self.u8()
        if kind == 0:
            return "none", None
        if kind in (1, 2):
            return ("id" if kind == 1 else "string"), self.string()
        if kind == 3:
            self.need(4)
            value = struct.unpack_from(">i", self.data, self.pos)[0]
            self.pos += 4
            return "int", value
        if kind == 4:
            self.need(4)
            value = struct.unpack_from(">f", self.data, self.pos)[0]
            self.pos += 4
            return "float", value
        if kind == 5:
            return "bool", bool(self.u8())
        raise PexFormatError(f"unsupported value type {kind} at 0x{self.pos - 1:X}")

    def function(self, name: str) -> None:
        start = self.pos
        return_type = self.string()
        self.string()  # documentation string
        user_flags = self.u32()
        function_flags = self.u8()
        parameters = [(self.string(), self.string()) for _ in range(self.u16())]
        locals_ = [(self.string(), self.string()) for _ in range(self.u16())]
        count = self.u16()
        self.lines.append(
            f"function {name} @ 0x{start:X} -> {return_type} "
            f"userFlags={user_flags} flags={function_flags}"
        )
        if parameters:
            self.lines.append(f"  parameters: {parameters}")
        if locals_:
            self.lines.append(f"  locals: {locals_}")
        for index in range(count):
            address = self.pos
            opcode = self.u8()
            if opcode in (23, 25):
                args = [self.value(), self.value(), self.value()]
                argument_count = self.value()
                if argument_count[0] != "int" or int(argument_count[1]) < 0:
                    raise PexFormatError(f"bad call argument count at 0x{address:X}")
                args.append(argument_count)
                args.extend(self.value() for _ in range(int(argument_count[1])))
            elif opcode in FIXED:
                args = [self.value() for _ in range(FIXED[opcode])]
            else:
                raise PexFormatError(f"unsupported opcode {opcode} at 0x{address:X}")
            op_name = OPCODES[opcode] if opcode < len(OPCODES) else str(opcode)
            self.lines.append(f"  {index:02d} 0x{address:X} {op_name} {args}")


def parse_pex(data: bytes) -> dict[str, object]:
    reader = Reader(data)
    if reader.u32() != 0xFA57C0DE:
        raise PexFormatError("not a Skyrim PEX (magic mismatch)")
    major, minor, game_id = reader.u8(), reader.u8(), reader.u16()
    compiled = reader.u64()
    source, _user, _machine = reader.raw_string(), reader.raw_string(), reader.raw_string()
    reader.strings = [reader.raw_string() for _ in range(reader.u16())]
    has_debug = reader.u8()
    if has_debug:
        reader.u64()
        for _ in range(reader.u16()):
            reader.u16(); reader.u16(); reader.u16(); reader.u8()
            for _ in range(reader.u16()):
                reader.u16()
    for _ in range(reader.u16()):
        reader.u16(); reader.u8()
    object_count = reader.u16()
    for _ in range(object_count):
        object_start = reader.pos
        name = reader.string()
        size = reader.u32()
        if size < 4:
            raise PexFormatError(f"invalid object size {size} at 0x{object_start:X}")
        object_end = reader.pos + size - 4
        if object_end > len(data):
            raise PexFormatError(f"object end 0x{object_end:X} exceeds file length 0x{len(data):X}")
        parent, _doc = reader.string(), reader.string()
        user_flags, auto_state = reader.u32(), reader.string()
        reader.lines.append(
            f"object {name} @ 0x{object_start:X} parent={parent} "
            f"userFlags={user_flags} autoState={auto_state!r}"
        )
        for _ in range(reader.u16()):
            variable_name, variable_type = reader.string(), reader.string()
            variable_flags, initial_value = reader.u32(), reader.value()
            reader.lines.append(
                f"  variable {variable_name}: {variable_type} "
                f"userFlags={variable_flags} initial={initial_value}"
            )
        for _ in range(reader.u16()):
            property_name, property_type = reader.string(), reader.string()
            reader.string()  # documentation string
            reader.u32()
            property_flags = reader.u8()
            if property_flags & 4:
                auto_variable = reader.string()
                reader.lines.append(
                    f"  auto property {property_name}: {property_type} "
                    f"flags={property_flags} variable={auto_variable}"
                )
            else:
                if property_flags & 1:
                    reader.function(f"{property_name}.get")
                if property_flags & 2:
                    reader.function(f"{property_name}.set")
        for _ in range(reader.u16()):
            state = reader.string()
            reader.lines.append(f"state {state!r}")
            for _ in range(reader.u16()):
                reader.function(reader.string())
        if reader.pos != object_end:
            raise PexFormatError(
                f"object ended at 0x{reader.pos:X}, expected 0x{object_end:X}"
            )
    return {
        "major": major, "minor": minor, "game_id": game_id,
        "compiled": compiled, "source": source, "object_count": object_count,
        "consumed_bytes": reader.pos, "trailing_bytes": len(data) - reader.pos,
        "lines": reader.lines,
    }


def _native_path(value: str) -> Path:
    win = PureWindowsPath(value)
    if win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        return Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    return Path(value).expanduser()


def configured_data_dir() -> Path:
    config = read_local_config(ROOT)
    value = config.get("SKYRIM_DATA", "")
    if not value:
        raise FileNotFoundError("SKYRIM_DATA is not set in ignored config/local.env")
    path = _native_path(value)
    if not path.is_dir():
        raise FileNotFoundError("configured Skyrim data directory is unavailable")
    return path


def _safe_local_output(value: str | None, default_name: str) -> Path:
    local_root = (ROOT / ".local").resolve()
    output = Path(value).expanduser() if value else local_root / "readiness" / "papyrus" / default_name
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    if output != local_root and local_root not in output.parents:
        raise ValueError("output must be inside ignored .local research storage")
    return output


def extract_pex_from_bsa(archive: Path, script: str) -> tuple[bytes, dict[str, object]]:
    stem = Path(script).stem
    source = (stem + ".psc").encode("ascii")
    data = archive.read_bytes()
    if data[:4] != b"BSA\0":
        raise ValueError("input does not have a BSA header")
    positions: list[int] = []
    cursor = 0
    while True:
        cursor = data.find(source, cursor)
        if cursor < 0:
            break
        positions.append(cursor)
        cursor += len(source)
    for source_at in positions:
        start = data.rfind(MAGIC, max(0, source_at - 4096), source_at)
        end = data.find(MAGIC, source_at + len(source))
        if start < 0 or end < 0 or end <= start:
            continue
        payload = data[start:end]
        try:
            parsed = parse_pex(payload)
        except (PexFormatError, struct.error):
            continue
        if Path(str(parsed["source"])).name.casefold() != source.decode("ascii").casefold():
            continue
        return payload, {
            "archive": archive.name,
            "archive_sha256": hashlib.sha256(data).hexdigest(),
            "source": str(parsed["source"]),
            "source_string_offset": source_at,
            "pex_offset": start,
            "pex_end_offset": end,
            "pex_size": len(payload),
            "parsed_bytes": parsed["consumed_bytes"],
            "trailing_bytes": parsed["trailing_bytes"],
        }
    raise FileNotFoundError(f"no supported PEX stream found for {source.decode('ascii')}")


def scan_literal_actor_values(data_dir: Path, *, include_creations: bool = False) -> dict[str, object]:
    archives = [data_dir / "Skyrim - Misc.bsa"]
    if include_creations:
        archives.extend(sorted(data_dir.glob("cc*.bsa")))
    archives = [path for path in archives if path.is_file()]
    hits: dict[str, list[dict[str, object]]] = {}
    for archive in archives:
        file_hits = []
        with archive.open("rb") as stream:
            size = stream.seek(0, 2)
            stream.seek(0)
            if size == 0:
                continue
            with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as blob:
                for target in TARGET_ACTOR_VALUES:
                    offset = blob.find(target.encode("ascii"))
                    if offset >= 0:
                        file_hits.append({"literal": target, "offset": offset})
        if file_hits:
            hits[archive.name] = file_hits
    return {
        "archive_count": len(archives),
        "archives": [path.name for path in archives],
        "target_literals": list(TARGET_ACTOR_VALUES),
        "hits": hits,
        "hit_count": sum(len(items) for items in hits.values()),
        "scope": ("Skyrim - Misc.bsa plus installed cc*.bsa; literal bytes only" if include_creations
                  else "Skyrim - Misc.bsa only; literal bytes only"),
        "limit": "absence does not exclude dynamically constructed strings or native calls",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    dis = sub.add_parser("disassemble", help="inspect a loose PEX file")
    dis.add_argument("pex", type=Path)
    extract = sub.add_parser("extract", help="extract one supported PEX stream from Skyrim - Misc.bsa")
    extract.add_argument("script", help="source script base name, with or without .psc/.pex")
    extract.add_argument("--data-dir", type=Path, help="override configured Skyrim data path")
    extract.add_argument("--output", help="output path under ignored .local/")
    scan = sub.add_parser("scan-literals", help="scan Skyrim - Misc.bsa for literal PowerModifier names")
    scan.add_argument("--include-creations", action="store_true",
                      help="also scan every installed cc*.bsa (can traverse several GB)")
    args = parser.parse_args(argv)
    try:
        if args.command == "disassemble":
            parsed = parse_pex(args.pex.read_bytes())
            print(f"PEX {parsed['major']}.{parsed['minor']} game={parsed['game_id']} "
                  f"compiled={parsed['compiled']} source={parsed['source']!r}")
            print("build user/machine fields: redacted")
            print("\n".join(parsed["lines"]))
            print(f"consumed_bytes={parsed['consumed_bytes']} trailing_bytes={parsed['trailing_bytes']}")
        elif args.command == "extract":
            data_dir = args.data_dir or configured_data_dir()
            archive = data_dir / "Skyrim - Misc.bsa"
            payload, metadata = extract_pex_from_bsa(archive, args.script)
            output = _safe_local_output(args.output, f"{Path(args.script).stem}.pex")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
            metadata.update({"output": str(output.relative_to(ROOT)),
                             "output_sha256": hashlib.sha256(payload).hexdigest()})
            print(json.dumps(metadata, indent=2))
        else:
            print(json.dumps(scan_literal_actor_values(
                configured_data_dir(), include_creations=args.include_creations), indent=2))
        return 0
    except (OSError, ValueError, UnicodeError, struct.error) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
