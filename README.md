# csv-insight

A command-line tool that summarises the columns of a CSV file. It uses only the Python standard library.

For each column it reports the number of values, missing values and unique values. Numeric columns also get min, max, mean and median. Text columns get their most common values.

## Install

Requires Python 3.9 or newer.

```bash
pip install -e .
```

## Usage

```bash
csv-insight people.csv
```

```
name (text)
  values: 4  missing: 0  unique: 4
  most common: Amina (1), Brian (1), Chloe (1)

age (numeric)
  values: 3  missing: 1  unique: 3
  min: 25  max: 41  mean: 32.00  median: 30

city (text)
  values: 4  missing: 0  unique: 2
  most common: Nairobi (3), Mombasa (1)
```

| Option | Description |
|--------|-------------|
| `-d`, `--delimiter` | Field delimiter, default `,` |
| `--top N` | Common values shown for text columns, default `3` |
| `--json` | Print the summary as JSON |
| `-` as the file | Read from standard input |

```bash
cat data.csv | csv-insight - --json
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

A column counts as numeric only when every non-empty value parses as a number. Short rows are padded and the padding counts as missing.

## License

MIT
