import click
from flask.cli import AppGroup
from app.extensions import db

cli_commands = AppGroup('db_ops')

@cli_commands.command('clear')
def clean_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())

    db.session.commit()
    click.echo("DB Cleared!")