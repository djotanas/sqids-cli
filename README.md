# sqids-cli

CLI to convert numeric IDs ↔ [Sqids](https://sqids.org/), replicating the encoder of the **Sqids 3.1.0** NuGet package. Requires only `bash` and `python3`, no external dependencies.

## Installation

Run from the directory where you want the repository to live (the symlink uses `$PWD`):

```bash
git clone git@github.com:djotanas/sqids-cli.git
ln -s "$PWD/sqids-cli/sqid-convert" ~/.local/bin/sqid-convert
```

The wrapper resolves the symlink and finds `sqid_convert.py` next to it.

## Usage

```bash
sqid-convert <numeric_id>      # encode
sqid-convert <sqid>            # decode
sqid-convert encode <id>       # force encode
sqid-convert decode <sqid>     # force decode
sqid-convert -c | --config     # (re)configure
sqid-convert -c <value>        # reconfigure, then convert
```

## Configuration

On the first run, the command prompts for:

| Field       | Type                                | Required | Notes                                                    |
|-------------|-------------------------------------|----------|----------------------------------------------------------|
| `alphabet`  | string                              | yes      | ≥ 3 ASCII characters, no repeats, no whitespace          |
| `minLength` | number                              | yes      | integer from 0 to 255                                    |
| `blocklist` | array `["string1", ..., "stringN"]` | no       | Enter uses the Sqids default list; `[]` disables it      |

With `-c`/`--config`, each prompt shows the current value in brackets and an empty Enter keeps it.

The config is stored at `${XDG_CONFIG_HOME:-~/.config}/sqid-convert/config.json`:

```json
{
  "alphabet": "...",
  "minLength": 5,
  "blocklist": null
}
```

`"blocklist": null` means the Sqids default list, filtered by the alphabet.
