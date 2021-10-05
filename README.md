# MTGPROXY

This is the scripts for automatically creating a proxy from the deck list.

## Getting Started

### Dependencies

OS:

- MacOS Big Sur(11.6)

Python modules:

- python ≧ 3.9
- mtgsdk ≧ 1.3.1
- tqdm ≧ 4.62.3
- more-itertools ≧ 8.10.0
- click ≧ 8.0.1
- reportlab ≧ 3.6.1
- Pillow ≧ 8.3.2

Please check [poetry.lock](https://github.com/reonyanarticle/mtg_proxy/blob/main/poetry.lock)for more details.

#### Note

I only checked it on Mac OS, so if there is a problem on Windows or Linux, I would appreciate it if you could issue a report.

### Installing

Using pip:

```sh
pip install mtgproxy
```

Using poetry:

```sh
git clone git@github.com:reonyanarticle/mtg_proxy.git
cd mtg_proxy
poetry install
```

Please check [here](https://github.com/python-poetry/poetry) for how to use poetry.

### Executing program

To run directly from a file:

```sh
python src/commamd.py --decklist foo.txt
```

To run with poetry:

```sh
poetry run mtgproxy --decklist foo.txt
```

## Help

Please use `--help` to check the details of the execution command.

```sh
poetry run mtgproxy --help
# Usage: mtgproxy [OPTIONS]

#   Program for printing proxy cards from a deck list.

# Options:
#   --decklist TEXT  Deck list for which you want to create a proxy
#                    [required]
#   --output TEXT    File name to print the proxy card
#   --help           Show this message and exit.
```

## Authors

Contributors names and contact info

- Reona [@reonaarticlemtg](https://twitter.com/reonaarticleMtG)

## Version History

- 0.1
  - Initial Release

## License

MIT Lisence.

## Acknowledgments

Inspiration, code snippets, etc.

- [Magic: The Gathering SDK](https://github.com/MagicTheGathering/mtg-sdk-python)
