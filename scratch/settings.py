# # import typer
# # from rich.console import Console
# # from typing import Optional
# #
# # app = typer.Typer()
# # console = Console()
# #
# #
# # @app.command()
# # def show(context: typer.Context):
# #     settings_manager = context.obj
# #     settings_manager.show_settings()
# #
# #
# # @app.command()
# # def set(context: typer.Context, key: str, value: str):
# #     settings_manager = context.obj
# #     settings_manager.set_setting(key, value)
# #     console.print(f"{key} -> {value}")
# #
# #
# # @app.command()
# # def back(context: typer.Context):
# #     settings_manager = context.obj
# #     if settings_manager.change_context(".."):
# #         console.print("[green]Moved to parent context")
# #     else:
# #         console.print("[yellow]Already at root context")
# #
# #
# # @app.callback()
# # def main(context: typer.Context):
# #     """Settings management"""
# #     pass
#
# import typer
# from rich.console import Console
# from rich.table import Table
#
# app = typer.Typer(help="Settings management")
# console = Console()
#
#
# @app.command()
# def show(ctx: typer.Context):
#     """Display current context settings"""
#     settings_manager = ctx.obj
#     settings_manager.show_settings()
#
#
# @app.command()
# def set(ctx: typer.Context, key: str, value: str):
#     """Set a setting in the current context"""
#     settings_manager = ctx.obj
#     settings_manager.set_setting(key, value)
#     console.print(f"[green]Set {key} -> {value}")
#
#
# @app.callback(invoke_without_command=True)
# def settings_callback(ctx: typer.Context):
#     """Settings management for the current context"""
#     if ctx.invoked_subcommand is None:
#         # Show settings if no subcommand is provided
#         settings_manager = ctx.obj
#         settings_manager.show_settings()
