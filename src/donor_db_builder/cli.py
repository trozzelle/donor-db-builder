# import click
# from dotenv import load_dotenv
# from .config import get_setting, set_setting
#
# load_dotenv("../../.env")
#
# @click.group()
# def cli():
#     """Donor Database Builder CLI"""
#     pass
#
# @cli.group()
# def config():
#     """Manage persistent configuration"""
#     pass
#
# @config.command()
# @click.argument("key")
# @click.argument("value")
# def set(key, value):
#     """Set a configuration value"""
#     set_setting(key, value)
#     click.echo(f"Set {key} to {value}")
#
# @config.command()
# @click.argument("key")
# def get(key):
#     """Get a configuration value"""
#     value = get_setting(key)
#     if value is None:
#         click.echo(f"No value set for {key}")
#     else:
#         click.echo(f"{key}: {value}")
#
# @cli.command()
# @click.option('--host', envvar='NEO_HOST',
#               default=lambda: get_setting('NEO_HOST', 'localhost'),
#               help='Neo4j DB host')
# @click.option('--port', envvar='NEO_PORT',
#               default=lambda: get_setting('NEO_PORT', '7687'),
#               help='Neo4j DB port')
# @click.option('--user', envvar='NEO_USER',
#               default=lambda: get_setting('NEO_USER', 'neo4j'),
#               help='Neo4j DB user')
# @click.option('--password', envvar='NEO_PASS',
#               default=lambda: get_setting('NEO_PASS', 'neo4j'),
#               help='Neo4j DB pass')
# def import_data(host, port, user, password):
#     """Import campaign finance data"""
#     uri = f"neo4j://{host}:{port}"
#     # Your existing import logic here
#     click.echo(f"Import data")
#     pass
#
#
# if __name__ == "__main__":
#     cli()
