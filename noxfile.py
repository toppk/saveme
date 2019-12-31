import nox

nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True
nox.options.keywords = "not serve"
nox.options.install_cache = "180"

source_files = ("lib/saveme", "tools", "tests", "setup.py", "noxfile.py")


@nox.session
def lint(session):
    session.install(
        "--upgrade", "autoflake", "black", "flake8", "isort", "seed-isort-config"
    )

    session.run("autoflake", "--in-place", "--recursive", *source_files)
    session.run(
        "seed-isort-config",
        "--application-directories=lib/saveme",
        success_codes=[0, 1],
    )
    session.run("isort", "--project=saveme", "--recursive", "--apply", *source_files)
    session.run("black", "--target-version=py36", *source_files)

    check(session)


@nox.session
def check(session):
    session.install(
        "--upgrade",
        "black",
        "flake8",
        "flake8-bugbear",
        "flake8-comprehensions",
        "flake8-pie",
        "isort",
        "mypy",
    )

    session.run("black", "--check", "--diff", "--target-version=py36", *source_files)
    session.run("flake8", *source_files)
    session.run("mypy", "lib/saveme")
    session.run(
        "isort", "--check", "--diff", "--project=saveme", "--recursive", *source_files,
    )


@nox.session
def docs(session):
    session.install(
        "--upgrade", "mkdocs", "mkdocs-material", "mkautodoc>=0.1.0", "snakefood3"
    )
    session.install("-e", ".")
    session.run("mkdocs", "build")


@nox.session(reuse_venv=True)
def serve(session):
    session.install(
        "--upgrade", "mkdocs", "mkdocs-material", "mkautodoc>=0.1.0", "snakefood3"
    )
    session.install("-e", ".")
    session.run("mkdocs", "serve")


@nox.session(python=["3.6", "3.7", "3.8"])
def test(session):
    session.install("--upgrade", "-r", "test-requirements.txt")
    session.run("nosetests", "--with-coverage", "tests/python.py")
