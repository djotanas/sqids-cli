#!/usr/bin/env python3
"""
Numeric ID <-> Sqid converter that exactly replicates the encoder of the
Sqids 3.1.0 NuGet package.

Alphabet, minLength and blocklist are configurable and stored in
$XDG_CONFIG_HOME/sqid-convert/config.json (default ~/.config/...). When no
blocklist is configured (null), the default list bundled with Sqids 3.1.0 is
used, filtered by the alphabet.
"""

import ast
import json
import os
import sys

CONFIG_PATH = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "sqid-convert",
    "config.json",
)
MIN_LENGTH_LIMIT = 255

_RAW_BLOCKLIST = [
    "0rgasm",
    "1d10t",
    "1d1ot",
    "1di0t",
    "1diot",
    "1eccacu10",
    "1eccacu1o",
    "1eccacul0",
    "1eccaculo",
    "1mbec11e",
    "1mbec1le",
    "1mbeci1e",
    "1mbecile",
    "a11upat0",
    "a11upato",
    "a1lupat0",
    "a1lupato",
    "aand",
    "ah01e",
    "ah0le",
    "aho1e",
    "ahole",
    "al1upat0",
    "al1upato",
    "allupat0",
    "allupato",
    "ana1",
    "ana1e",
    "anal",
    "anale",
    "anus",
    "arrapat0",
    "arrapato",
    "arsch",
    "arse",
    "ass",
    "b00b",
    "b00be",
    "b01ata",
    "b0ceta",
    "b0iata",
    "b0ob",
    "b0obe",
    "b0sta",
    "b1tch",
    "b1te",
    "b1tte",
    "ba1atkar",
    "balatkar",
    "bastard0",
    "bastardo",
    "batt0na",
    "battona",
    "bitch",
    "bite",
    "bitte",
    "bo0b",
    "bo0be",
    "bo1ata",
    "boceta",
    "boiata",
    "boob",
    "boobe",
    "bosta",
    "bran1age",
    "bran1er",
    "bran1ette",
    "bran1eur",
    "bran1euse",
    "branlage",
    "branler",
    "branlette",
    "branleur",
    "branleuse",
    "c0ck",
    "c0g110ne",
    "c0g11one",
    "c0g1i0ne",
    "c0g1ione",
    "c0gl10ne",
    "c0gl1one",
    "c0gli0ne",
    "c0glione",
    "c0na",
    "c0nnard",
    "c0nnasse",
    "c0nne",
    "c0u111es",
    "c0u11les",
    "c0u1l1es",
    "c0u1lles",
    "c0ui11es",
    "c0ui1les",
    "c0uil1es",
    "c0uilles",
    "c11t",
    "c11t0",
    "c11to",
    "c1it",
    "c1it0",
    "c1ito",
    "cabr0n",
    "cabra0",
    "cabrao",
    "cabron",
    "caca",
    "cacca",
    "cacete",
    "cagante",
    "cagar",
    "cagare",
    "cagna",
    "cara1h0",
    "cara1ho",
    "caracu10",
    "caracu1o",
    "caracul0",
    "caraculo",
    "caralh0",
    "caralho",
    "cazz0",
    "cazz1mma",
    "cazzata",
    "cazzimma",
    "cazzo",
    "ch00t1a",
    "ch00t1ya",
    "ch00tia",
    "ch00tiya",
    "ch0d",
    "ch0ot1a",
    "ch0ot1ya",
    "ch0otia",
    "ch0otiya",
    "ch1asse",
    "ch1avata",
    "ch1er",
    "ch1ng0",
    "ch1ngadaz0s",
    "ch1ngadazos",
    "ch1ngader1ta",
    "ch1ngaderita",
    "ch1ngar",
    "ch1ngo",
    "ch1ngues",
    "ch1nk",
    "chatte",
    "chiasse",
    "chiavata",
    "chier",
    "ching0",
    "chingadaz0s",
    "chingadazos",
    "chingader1ta",
    "chingaderita",
    "chingar",
    "chingo",
    "chingues",
    "chink",
    "cho0t1a",
    "cho0t1ya",
    "cho0tia",
    "cho0tiya",
    "chod",
    "choot1a",
    "choot1ya",
    "chootia",
    "chootiya",
    "cl1t",
    "cl1t0",
    "cl1to",
    "clit",
    "clit0",
    "clito",
    "cock",
    "cog110ne",
    "cog11one",
    "cog1i0ne",
    "cog1ione",
    "cogl10ne",
    "cogl1one",
    "cogli0ne",
    "coglione",
    "cona",
    "connard",
    "connasse",
    "conne",
    "cou111es",
    "cou11les",
    "cou1l1es",
    "cou1lles",
    "coui11es",
    "coui1les",
    "couil1es",
    "couilles",
    "cracker",
    "crap",
    "cu10",
    "cu1att0ne",
    "cu1attone",
    "cu1er0",
    "cu1ero",
    "cu1o",
    "cul0",
    "culatt0ne",
    "culattone",
    "culer0",
    "culero",
    "culo",
    "cum",
    "cunt",
    "d11d0",
    "d11do",
    "d1ck",
    "d1ld0",
    "d1ldo",
    "damn",
    "de1ch",
    "deich",
    "depp",
    "di1d0",
    "di1do",
    "dick",
    "dild0",
    "dildo",
    "dyke",
    "encu1e",
    "encule",
    "enema",
    "enf01re",
    "enf0ire",
    "enfo1re",
    "enfoire",
    "estup1d0",
    "estup1do",
    "estupid0",
    "estupido",
    "etr0n",
    "etron",
    "f0da",
    "f0der",
    "f0ttere",
    "f0tters1",
    "f0ttersi",
    "f0tze",
    "f0utre",
    "f1ca",
    "f1cker",
    "f1ga",
    "fag",
    "fica",
    "ficker",
    "figa",
    "foda",
    "foder",
    "fottere",
    "fotters1",
    "fottersi",
    "fotze",
    "foutre",
    "fr0c10",
    "fr0c1o",
    "fr0ci0",
    "fr0cio",
    "fr0sc10",
    "fr0sc1o",
    "fr0sci0",
    "fr0scio",
    "froc10",
    "froc1o",
    "froci0",
    "frocio",
    "frosc10",
    "frosc1o",
    "frosci0",
    "froscio",
    "fuck",
    "g00",
    "g0o",
    "g0u1ne",
    "g0uine",
    "gandu",
    "go0",
    "goo",
    "gou1ne",
    "gouine",
    "gr0gnasse",
    "grognasse",
    "haram1",
    "harami",
    "haramzade",
    "hund1n",
    "hundin",
    "id10t",
    "id1ot",
    "idi0t",
    "idiot",
    "imbec11e",
    "imbec1le",
    "imbeci1e",
    "imbecile",
    "j1zz",
    "jerk",
    "jizz",
    "k1ke",
    "kam1ne",
    "kamine",
    "kike",
    "leccacu10",
    "leccacu1o",
    "leccacul0",
    "leccaculo",
    "m1erda",
    "m1gn0tta",
    "m1gnotta",
    "m1nch1a",
    "m1nchia",
    "m1st",
    "mam0n",
    "mamahuev0",
    "mamahuevo",
    "mamon",
    "masturbat10n",
    "masturbat1on",
    "masturbate",
    "masturbati0n",
    "masturbation",
    "merd0s0",
    "merd0so",
    "merda",
    "merde",
    "merdos0",
    "merdoso",
    "mierda",
    "mign0tta",
    "mignotta",
    "minch1a",
    "minchia",
    "mist",
    "musch1",
    "muschi",
    "n1gger",
    "neger",
    "negr0",
    "negre",
    "negro",
    "nerch1a",
    "nerchia",
    "nigger",
    "orgasm",
    "p00p",
    "p011a",
    "p01la",
    "p0l1a",
    "p0lla",
    "p0mp1n0",
    "p0mp1no",
    "p0mpin0",
    "p0mpino",
    "p0op",
    "p0rca",
    "p0rn",
    "p0rra",
    "p0uff1asse",
    "p0uffiasse",
    "p1p1",
    "p1pi",
    "p1r1a",
    "p1rla",
    "p1sc10",
    "p1sc1o",
    "p1sci0",
    "p1scio",
    "p1sser",
    "pa11e",
    "pa1le",
    "pal1e",
    "palle",
    "pane1e1r0",
    "pane1e1ro",
    "pane1eir0",
    "pane1eiro",
    "panele1r0",
    "panele1ro",
    "paneleir0",
    "paneleiro",
    "patakha",
    "pec0r1na",
    "pec0rina",
    "pecor1na",
    "pecorina",
    "pen1s",
    "pendej0",
    "pendejo",
    "penis",
    "pip1",
    "pipi",
    "pir1a",
    "pirla",
    "pisc10",
    "pisc1o",
    "pisci0",
    "piscio",
    "pisser",
    "po0p",
    "po11a",
    "po1la",
    "pol1a",
    "polla",
    "pomp1n0",
    "pomp1no",
    "pompin0",
    "pompino",
    "poop",
    "porca",
    "porn",
    "porra",
    "pouff1asse",
    "pouffiasse",
    "pr1ck",
    "prick",
    "pussy",
    "put1za",
    "puta",
    "puta1n",
    "putain",
    "pute",
    "putiza",
    "puttana",
    "queca",
    "r0mp1ba11e",
    "r0mp1ba1le",
    "r0mp1bal1e",
    "r0mp1balle",
    "r0mpiba11e",
    "r0mpiba1le",
    "r0mpibal1e",
    "r0mpiballe",
    "rand1",
    "randi",
    "rape",
    "recch10ne",
    "recch1one",
    "recchi0ne",
    "recchione",
    "retard",
    "romp1ba11e",
    "romp1ba1le",
    "romp1bal1e",
    "romp1balle",
    "rompiba11e",
    "rompiba1le",
    "rompibal1e",
    "rompiballe",
    "ruff1an0",
    "ruff1ano",
    "ruffian0",
    "ruffiano",
    "s1ut",
    "sa10pe",
    "sa1aud",
    "sa1ope",
    "sacanagem",
    "sal0pe",
    "salaud",
    "salope",
    "saugnapf",
    "sb0rr0ne",
    "sb0rra",
    "sb0rrone",
    "sbattere",
    "sbatters1",
    "sbattersi",
    "sborr0ne",
    "sborra",
    "sborrone",
    "sc0pare",
    "sc0pata",
    "sch1ampe",
    "sche1se",
    "sche1sse",
    "scheise",
    "scheisse",
    "schlampe",
    "schwachs1nn1g",
    "schwachs1nnig",
    "schwachsinn1g",
    "schwachsinnig",
    "schwanz",
    "scopare",
    "scopata",
    "sexy",
    "sh1t",
    "shit",
    "slut",
    "sp0mp1nare",
    "sp0mpinare",
    "spomp1nare",
    "spompinare",
    "str0nz0",
    "str0nza",
    "str0nzo",
    "stronz0",
    "stronza",
    "stronzo",
    "stup1d",
    "stupid",
    "succh1am1",
    "succh1ami",
    "succhiam1",
    "succhiami",
    "sucker",
    "t0pa",
    "tapette",
    "test1c1e",
    "test1cle",
    "testic1e",
    "testicle",
    "tette",
    "topa",
    "tr01a",
    "tr0ia",
    "tr0mbare",
    "tr1ng1er",
    "tr1ngler",
    "tring1er",
    "tringler",
    "tro1a",
    "troia",
    "trombare",
    "turd",
    "twat",
    "vaffancu10",
    "vaffancu1o",
    "vaffancul0",
    "vaffanculo",
    "vag1na",
    "vagina",
    "verdammt",
    "verga",
    "w1chsen",
    "wank",
    "wichsen",
    "x0ch0ta",
    "x0chota",
    "xana",
    "xoch0ta",
    "xochota",
    "z0cc01a",
    "z0cc0la",
    "z0cco1a",
    "z0ccola",
    "z1z1",
    "z1zi",
    "ziz1",
    "zizi",
    "zocc01a",
    "zocc0la",
    "zocco1a",
    "zoccola"
]


def _consistent_shuffle(chars):
    chars = list(chars)
    n = len(chars)
    i, j = 0, n - 1
    while j > 0:
        r = (i * j + ord(chars[i]) + ord(chars[j])) % n
        chars[i], chars[r] = chars[r], chars[i]
        i += 1
        j -= 1
    return chars


def _build_filtered_blocklist(alphabet, blocklist):
    alphabet_lower_chars = set(alphabet.lower())
    filtered = set()
    for word in blocklist:
        if len(word) < 3:
            continue
        lowered = word.lower()
        if all(c in alphabet_lower_chars for c in lowered):
            filtered.add(lowered)
    return filtered


class Sqids:
    def __init__(self, alphabet, min_length, blocklist=None):
        self._min_length = min_length
        if blocklist is None:
            blocklist = _RAW_BLOCKLIST
        self._blocklist = _build_filtered_blocklist(alphabet, blocklist)
        self._alphabet = "".join(_consistent_shuffle(alphabet))

    def _to_id(self, num, alphabet):
        chars = []
        base = len(alphabet)
        result = num
        while True:
            chars.insert(0, alphabet[result % base])
            result //= base
            if result <= 0:
                break
        return "".join(chars)

    def _to_number(self, id_chunk, alphabet):
        result = 0
        for ch in id_chunk:
            result = result * len(alphabet) + alphabet.index(ch)
        return result

    def _is_blocked_id(self, id_str):
        id_lower = id_str.lower()
        for word in self._blocklist:
            if len(word) > len(id_lower):
                continue
            if (len(id_lower) <= 3 or len(word) <= 3) and id_lower == word:
                return True
            if any(c.isdigit() for c in word) and (
                id_lower.startswith(word) or id_lower.endswith(word)
            ):
                return True
            if word in id_lower:
                return True
        return False

    def encode(self, numbers, _increment=0):
        if not numbers:
            return ""
        alphabet = self._alphabet
        if _increment > len(alphabet):
            raise ValueError("Reached max attempts to re-generate the ID.")

        offset = 0
        for i, n in enumerate(numbers):
            offset += ord(alphabet[n % len(alphabet)]) + i
        offset = (len(numbers) + offset) % len(alphabet)
        offset = (offset + _increment) % len(alphabet)

        alphabet_temp = alphabet[offset:] + alphabet[:offset]
        prefix = alphabet_temp[0]
        alphabet_temp = alphabet_temp[::-1]

        parts = [prefix]
        for i, n in enumerate(numbers):
            alphabet_without_separator = alphabet_temp[1:]
            parts.append(self._to_id(n, alphabet_without_separator))
            if i < len(numbers) - 1:
                parts.append(alphabet_temp[0])
                alphabet_temp = "".join(_consistent_shuffle(alphabet_temp))

        result = "".join(parts)

        if len(result) < self._min_length:
            result += alphabet_temp[0]
            while len(result) < self._min_length:
                alphabet_temp = "".join(_consistent_shuffle(alphabet_temp))
                take = min(self._min_length - len(result), len(alphabet_temp))
                result += alphabet_temp[:take]

        if self._is_blocked_id(result):
            result = self.encode(numbers, _increment + 1)

        return result

    def decode(self, id_str):
        if not id_str:
            return []

        alphabet = self._alphabet
        for ch in id_str:
            if ch not in alphabet:
                return []

        prefix = id_str[0]
        offset = alphabet.index(prefix)
        alphabet_temp = alphabet[offset:] + alphabet[:offset]
        alphabet_temp = alphabet_temp[::-1]

        remaining = id_str[1:]
        result = []
        while remaining:
            separator = alphabet_temp[0]
            if separator in remaining:
                idx = remaining.index(separator)
                chunk, remaining = remaining[:idx], remaining[idx + 1 :]
            else:
                chunk, remaining = remaining, ""

            if chunk == "":
                return result

            alphabet_without_separator = alphabet_temp[1:]
            result.append(self._to_number(chunk, alphabet_without_separator))

            if remaining:
                alphabet_temp = "".join(_consistent_shuffle(alphabet_temp))

        return result


def _validate_alphabet(alphabet):
    if len(alphabet) < 3:
        return "the alphabet must have at least 3 characters."
    if len(set(alphabet)) != len(alphabet):
        return "the alphabet must not contain repeated characters."
    if not alphabet.isascii() or any(c.isspace() for c in alphabet):
        return "the alphabet must contain only ASCII characters, no whitespace."
    return None


def _parse_min_length(raw):
    try:
        value = int(raw)
    except ValueError:
        return None, "minLength must be an integer."
    if not 0 <= value <= MIN_LENGTH_LIMIT:
        return None, f"minLength must be between 0 and {MIN_LENGTH_LIMIT}."
    return value, None


def _parse_blocklist(raw):
    try:
        value = json.loads(raw)
    except ValueError:
        try:
            value = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return None, 'invalid blocklist. Expected format: ["string1", ..., "stringN"]'
    if not isinstance(value, list) or not all(isinstance(w, str) for w in value):
        return None, 'blocklist must be an array of strings: ["string1", ..., "stringN"]'
    return value, None


def _describe_blocklist(blocklist):
    if blocklist is None:
        return f"Sqids default ({len(_RAW_BLOCKLIST)} words)"
    return json.dumps(blocklist, ensure_ascii=False)


def load_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        return None
    except ValueError:
        print(f"Invalid config at {CONFIG_PATH}; reconfigure with -c.", file=sys.stderr)
        return None
    if not isinstance(config.get("alphabet"), str) or not isinstance(config.get("minLength"), int):
        return None
    return config


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _ask(prompt, current, parse):
    """Prompt until a valid value is given. An empty Enter keeps `current`
    (when there is one); with no current value, the field is required."""
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            print(file=sys.stderr)
            raise SystemExit("Configuration cancelled.")
        if raw == "":
            if current is not _MISSING:
                return current
            print("  This field is required.", file=sys.stderr)
            continue
        value, error = parse(raw)
        if error:
            print(f"  {error}", file=sys.stderr)
            continue
        return value


_MISSING = object()


def configure(current):
    if not sys.stdin.isatty():
        print("Configuration requires an interactive terminal.", file=sys.stderr)
        raise SystemExit(1)

    current = current or {}
    alphabet_cur = current.get("alphabet", _MISSING)
    min_length_cur = current.get("minLength", _MISSING)
    # On first setup, Enter on blocklist uses the Sqids default.
    blocklist_cur = current.get("blocklist")

    print(f"Configuring sqid-convert ({CONFIG_PATH})", file=sys.stderr)
    print("Press Enter to keep the current value (in brackets).", file=sys.stderr)

    def hint(value, text=None):
        return "required" if value is _MISSING else (text or str(value))

    alphabet = _ask(
        f"alphabet [{hint(alphabet_cur)}]: ",
        alphabet_cur,
        lambda raw: (raw, _validate_alphabet(raw)),
    )
    min_length = _ask(f"minLength [{hint(min_length_cur)}]: ", min_length_cur, _parse_min_length)
    blocklist = _ask(
        f"blocklist [{_describe_blocklist(blocklist_cur)}]: ",
        blocklist_cur,
        _parse_blocklist,
    )

    config = {"alphabet": alphabet, "minLength": min_length, "blocklist": blocklist}
    save_config(config)
    print("Configuration saved.", file=sys.stderr)
    return config


def main(argv):
    reconfigure = False
    if argv and argv[0] in ("-c", "--config"):
        reconfigure = True
        argv = argv[1:]

    if argv and (len(argv) != 2 or argv[0] not in ("encode", "decode")):
        print("Usage: sqid_convert.py [-c|--config] [encode <numeric_id> | decode <sqid>]", file=sys.stderr)
        return 1

    config = load_config()
    if reconfigure or config is None:
        config = configure(config)

    if not argv:
        return 0

    mode, value = argv
    sqids = Sqids(config["alphabet"], config["minLength"], config.get("blocklist"))

    if mode == "encode":
        try:
            number = int(value)
        except ValueError:
            print(f"Invalid value for encode: {value!r} (expected an integer)", file=sys.stderr)
            return 1
        if number < 0:
            print("Id must be greater than or equal to zero.", file=sys.stderr)
            return 1
        print(sqids.encode([number]))
        return 0

    decoded = sqids.decode(value)
    decoded = decoded[0] if decoded else None
    if decoded is None:
        print(f"Invalid sqid: {value!r}", file=sys.stderr)
        return 1
    print(decoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
