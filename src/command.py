import click
from .create_proxy import create_proxy


@click.command()
@click.option("--decklist", type=str, required=True, help="Deck list for which you want to create a proxy")
@click.option("--output", type=str, default="output.pdf", help="File name to print the proxy card")
def main(decklist, output):
    """
    Program for printing proxy cards from a deck list.
    """
    create_proxy(file_name=decklist, save_name=output)


if __name__ == "__main__":
    main()
