from kinai.classes.cli import KinaiCLI
from kinai.classes.paths import Paths
import typer

VERSION = "0.1.0"

kinai = KinaiCLI()

app = typer.Typer(help="KINAI - Mayan Language ASR")

ITER_OPT = typer.Option("01", "--iter", "-i", help="Iteration id (e.g. 01, 02, iter_03)")


def version_callback(value: bool):
    if value:
        typer.echo(f"KINAI v{VERSION}")
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


# --- COMMANDS ---
@app.command()
def download(
    json: str = typer.Option("source_segments.json", "--json", "-j"),
    force: bool = typer.Option(False, "--force", "-f")
):
    paths = Paths()
    kinai.download(paths, json=paths.annotations / json, force=force)


@app.command()
def correct():
    paths = Paths()
    kinai.correct(paths)


@app.command()
def train(
    iter_id: str = ITER_OPT,
    experiment: str = typer.Option("mono", "--exp", "-e", help="Experiment (mono, tri, tdnn)"),
    nj: int = typer.Option(1, "--nj", help="Number of parallel jobs"),
):
    pass
    #paths = paths_builder.iteration(iter_id)
    #kinai.train(paths, experiment, nj)


@app.command()
def align(
    iter_id: str = ITER_OPT,
    model: str = typer.Option(..., "--model", "-m", help="Model as <iter>/<experiment> (e.g. 02/tri)"),
    nj: int = typer.Option(1, "--nj", help="Number of parallel jobs"),
):
    pass
    #paths = paths_builder.iteration(iter_id)
    #model_path, _ = _resolve_model(model)
    #kinai.align(paths, model_path, nj)


@app.command()
def segment(
    iter_id: str = ITER_OPT,
    model: str = typer.Option(..., "--model", "-m", help="Model as <iter>/<experiment> (e.g. 02/tri)"),
    nj: int = typer.Option(1, "--nj", help="Number of parallel jobs"),
):
    pass
    #paths = paths_builder.iteration(iter_id)
    #model_path, lang_path = _resolve_model(model)
    #kinai.segment(paths, model_path, lang_path, nj)


@app.command()
def build_lm(
    iter_id: str = ITER_OPT,
    kind: str = typer.Option("flat", "--kind", "-k", help="flat | ngram"),
    order: int = typer.Option(3, "--order", help="n-gram order (solo kind=ngram)"),
    transcripts_weight: int = typer.Option(
        3, "--transcripts-weight", "-w",
        help="Repetición del texto de transcripciones vs biblia (solo kind=ngram)",
    ),
):
    pass
    #paths = paths_builder.iteration(iter_id)
    #kinai.build_lm(paths, kind=kind, order=order, transcripts_weight=transcripts_weight)


@app.command()
def gen_lexicon(
    iter_id: str = ITER_OPT,
    include_lm_text: bool = typer.Option(
        False, "--include-lm-text/--no-lm-text",
        help="Incluir vocabulario de assets/text/*.txt",
    ),
):
    pass
    #paths = paths_builder.iteration(iter_id)
    #kinai.gen_lexicon(paths, include_lm_text)

@app.command()
def gen_data(
    manifest: str = typer.Option("data_manifest.json", "--man", "-m"),
    out_dir: str = typer.Option("train", "--out-dir", "-od")
):
    paths = Paths()
    kinai.gen_data(paths, manifest, out_dir)

@app.command()
def gen_manifest(
    json: str = typer.Option("source_segments.json", "--json", "-j"),
    file_name: str = typer.Option("train", "--file-name", "-f")
):
    paths = Paths()
    kinai.gen_manifest(paths, json, file_name)



@app.command()
def where():
    pass
    #print(paths_builder.root)


@app.command()
def entry():
    app()


if __name__ == "__main__":
    app()
