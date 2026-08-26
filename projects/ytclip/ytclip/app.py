"""CLI `ytclip`: descarga audio de sus fuentes y lo recorta en utterances.

Lee un manifiesto de procedencia (`data/final/manifests/source_segments.json`),
descarga el audio largo cuando hace falta y produce un wav por segmento en
`data/work/segments/`.

⚠ Estado: `download` y `correct` esperan todavía el formato ANTIGUO del
manifiesto (lista de vídeos con `maya`/`spanish`). El manifiesto vigente es un
dict de tres grupos sin texto, así que el lector hay que adaptarlo antes de
poder reconstruir el corpus de punta a punta. Ver projects/corpus/README.md.
"""

import typer

from ytclip.cli import YtclipCLI
from ytclip.paths import Paths

VERSION = "0.1.0"

ytclip = YtclipCLI()

app = typer.Typer(help="ytclip - recorte de audio para el corpus de maya yucateco")


def version_callback(value: bool):
    if value:
        typer.echo(f"ytclip v{VERSION}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        help="Muestra la versión",
        callback=version_callback,
        is_eager=True,
    )
):
    pass


@app.command()
def download(
    json: str = typer.Option("source_segments.json", "--json", "-j",
                             help="Manifiesto dentro de data/final/manifests/"),
    force: bool = typer.Option(False, "--force", "-f",
                               help="Rehace los recortes que ya existan"),
):
    """Descarga las fuentes y recorta cada segmento en data/work/segments/."""
    paths = Paths()
    ytclip.download(paths, json=paths.manifests / json, force=force)


@app.command()
def correct():
    """Editor interactivo de los timestamps del manifiesto."""
    paths = Paths()
    ytclip.correct(paths)


@app.command("gen-manifest")
def gen_manifest(
    json: str = typer.Option("source_segments.json", "--json", "-j",
                             help="Manifiesto dentro de data/final/manifests/"),
    out: str = typer.Option("data_manifest.csv", "--out", "-o",
                            help="CSV de salida dentro de data/final/manifests/"),
):
    """Aplana el manifiesto a un CSV de una fila por utterance."""
    paths = Paths()
    ytclip.gen_manifest(paths, paths.manifests / json, paths.manifests / out)


@app.command()
def where():
    """Muestra dónde está resolviendo el proyecto sus rutas."""
    from mayanlab import paths as p

    for name in ("REPO_ROOT", "DATA", "SOURCE", "WORK", "FINAL", "AUDIO", "TRANSCRIPTS"):
        typer.echo(f"{name:<12} {getattr(p, name)}")


def entry():
    app()


if __name__ == "__main__":
    app()
