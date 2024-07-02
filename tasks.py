from invoke import task
from pathlib import Path

# The first time invoke is called, it is to install dependencies, so toml is not yet installed
try:
    import toml
except ImportError:
    toml = None

# The first time invoke is called, it is to install dependencies, so at that point rich is not
# installed yet
try:
    from rich import print as rprint
    from rich.console import Console
except ImportError:
    rprint = print
    def Console(*args, **kwargs):
        raise RuntimeError("Install rich first")


THIS_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = THIS_DIR / "src"

@task(aliases=("check_black", "cb", "ccf"))
def check_code_format(context):
    """Check that the code is black formatted"""
    rprint("\n[bold]Checking code style...")
    with context.cd(THIS_DIR):
        result = context.run(f"black --check {SOURCE_DIR}")
        if result.return_code == 0:
            rprint("[bold green]Code format checked. No issues.")
    return result.return_code

@task(aliases=("b", "fc", "black"))
def format_code(context):
    """Format all of zilien_qt with black"""
    rprint("format called")
    context.run(f"black {SOURCE_DIR}")

@task(aliases=("pip", "deps"))
def dependencies(context):
    """Install all requirements and development requirements"""
    global toml
    if toml is None:
        context.run("python -m pip install toml")
        import toml
    with context.cd(THIS_DIR):
        context.run("python -m pip install --upgrade pip")
        data = toml.load(THIS_DIR / "pyproject.toml")
        context.run(f"pip install {' '.join(data['project']['dependencies'])}")
        context.run("pip install " f"{' '.join(data['project']['optional-dependencies']['dev'])}")

@task(aliases=["check", "c"])
def checks(context):
    """Check code with black, flake8, mypy and run tests"""
    combined_return_code = check_code_format(context)
    
    if combined_return_code == 0:
        rprint()
        rprint(r"+----------+")
        rprint(r"| All good |")
        rprint(r"+----------+")
    else:
        rprint()
        rprint(r"+---------------------+")
        rprint(r"| [bold red]Some checks [blink]FAILED![/blink][/bold red] |")
        rprint(r"| [bold]Check output above[/bold]  |")
        rprint(r"| [bold]run 'inv fc'[/bold]  |")
        rprint(r"+---------------------+")