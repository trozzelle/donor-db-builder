# import typer
# from rich.console import Console
# from rich.table import Table
# from typing import Optional
# import sys
# from donor_db_builder.config import SettingsManager
# from . import settings
#
#
# # settings_manager = SettingsManager()
#
#
# def interactive_shell(settings_manager: SettingsManager) -> typer.Typer:
#     """Interactive shell mode"""
#
#     app = typer.Typer(help="Donor DB Builder - NYS Campaign Finance Data Import Tool")
#     console = Console()
#
#     app.add_typer(settings.app, name="settings", help="Settings management")
#
#     @app.callback(invoke_without_command=True)
#     def main(ctx: typer.Context):
#         """
#         Donor DB Builder CLI - Interactive Mode
#         """
#         # Set the settings_manager in the context for subcommands to access
#         ctx.obj = settings_manager
#
#         # Only show welcome message if no subcommand is being executed
#         if ctx.invoked_subcommand is None:
#             console.print("[bold green]Interactive shell mode[/bold green]")
#             console.print("Type 'exit' to quit")
#             console.print("Type 'help' for help")
#             console.print("Type 'back' to return to parent context")
#
#             while True:
#                 try:
#                     prompt = f"{settings_manager.get_prompt_path()}> "
#                     command = typer.prompt(prompt, type=str)
#
#                     if not command:
#                         continue
#
#                     if command.lower() == "exit":
#                         console.print("[yellow]Goodbye![/yellow]")
#                         sys.exit(0)
#
#                     if command.lower() == "back":
#                         if settings_manager.change_context(".."):
#                             console.print("[green]Moved to parent context[/green]")
#                         else:
#                             console.print("[yellow]Already at root context[/yellow]")
#                         continue
#
#                     # if command.lower() == "help":
#                     #     show_help(console)
#                     #     continue
#
#                     # Split command and arguments
#                     parts = command.split()
#                     if not parts:
#                         continue
#
#                     # Handle context navigation
#                     if parts[0] in [
#                         "settings",
#                         "ingest",
#                         "nlp",
#                     ]:  # Add other valid contexts
#                         if settings_manager.change_context(parts[0]):
#                             console.print(f"[green]Moved to {parts[0]} context[/green]")
#                         continue
#
#                     # Execute typer command
#                     try:
#                         app(parts)
#                     except SystemExit:
#                         # Catch SystemExit to prevent shell from closing
#                         continue
#                     except Exception as e:
#                         console.print(f"[red]Error: {str(e)}[/red]")
#
#                 except KeyboardInterrupt:
#                     console.print("\n[yellow]Use 'exit' to quit[/yellow]")
#                     continue
#                 except EOFError:
#                     console.print("\n[yellow]Goodbye![/yellow]")
#                     sys.exit(0)
#
#     # console.print("[bold green]Interactive shell mode[/bold green]")
#     # console.print("Type 'exit' to quit")
#     # console.print("Type 'help' for help")
#     # console.print("Type 'back' to return to parent context")
#     #
#     # while True:
#     #     prompt = f"{settings_manager.get_prompt_path()}> "
#     #     command = typer.prompt(prompt, type=str)
#     #
#     #     if not command:
#     #         continue
#     #
#     #     if command.lower() == "exit":
#     #         console.print("Bye!")
#     #         sys.exit(0)
#     #
#     #     if command.lower() == "back":
#     #         if settings_manager.change_context(".."):
#     #             console.print("[green]Moved to parent context[/green]")
#     #         else:
#     #             console.print("[yellow]Already at root context[/yellow]")
#     #         continue
#     #
#     #     # Split command and arguments
#     #     parts = command.split()
#     #     if not parts:
#     #         continue
#     #
#     #     # Handle context navigation
#     #     if parts[0] in ["settings", "ingest", "nlp"]:  # Add other valid contexts
#     #         if settings_manager.change_context(parts[0]):
#     #             console.print(f"[green]Moved to {parts[0]} context[/green]")
#     #         continue
#     #
#     #     # Execute typer command
#     #     try:
#     #         app(parts)
#     #     except SystemExit:
#     #         # Catch SystemExit to prevent shell from closing
#     #         continue
#     #     except Exception as e:
#     #         console.print(f"[red]Error: {str(e)}[/red]")
#     #
#     #     # parts = command.split()
#     #     # cmd, *args = parts if parts else (None, [])
#     #
#     # # @app.command()
#     # # def help():
#     # #     """Show help"""
#     # #
#     # #     table = Table(title="Available Commands")
#     # #     table.add_column("Command", style="cyan")
#     # #     table.add_column("Description", style="green")
#     # #
#     # #     table.add_row("exit", "Exit the shell")
#     # #     table.add_row("help", "Show this help message")
#     # #
#     # #     console.print(table)
#     #
#     # @app.callback()
#     # def main(context: typer.Context):
#     #     """
#     #     Donor tool shell interface
#     #     """
#     #     command_path = context.command_path.split()
#     #     if len(command_path) > 1:
#     #         settings_manager.change_context(command_path[1])
#     #
#     #     context.settings = settings_manager
#
#     return app
#
#
# if __name__ == "__main__":
#     typer.run(interactive_shell)

# import typer
# from rich.console import Console
# from rich.table import Table
# from typing import Optional
# import sys
# from donor_db_builder.config import SettingsManager
# from . import settings
#
#
# def interactive_shell(settings_manager: SettingsManager) -> typer.Typer:
#     """Interactive shell mode"""
#     app = typer.Typer(help="Donor DB Builder - NYS Campaign Finance Data Import Tool")
#     console = Console()
#
#     # Add command groups
#     app.add_typer(settings.app, name="settings", help="Settings management")
#
#     @app.callback(invoke_without_command=True)
#     def main(ctx: typer.Context):
#         """
#         Donor DB Builder CLI - Interactive Mode
#         """
#         # Set the settings_manager in the context for subcommands to access
#         ctx.obj = settings_manager
#
#         # Only show welcome message if no subcommand is being executed
#         if ctx.invoked_subcommand is None:
#             console.print("[bold green]Interactive shell mode[/bold green]")
#             console.print("Type 'exit' to quit")
#             console.print("Type 'help' for help")
#             console.print("Type 'back' to return to parent context")
#
#             while True:
#                 try:
#                     prompt = f"{settings_manager.get_prompt_path()}> "
#                     command = typer.prompt(prompt, type=str)
#
#                     if not command:
#                         continue
#
#                     if command.lower() == "exit":
#                         console.print("[yellow]Goodbye![/yellow]")
#                         sys.exit(0)
#
#                     if command.lower() == "back":
#                         if settings_manager.change_context(".."):
#                             console.print("[green]Moved to parent context[/green]")
#                         else:
#                             console.print("[yellow]Already at root context[/yellow]")
#                         continue
#
#                     if command.lower() == "help":
#                         show_help(console)
#                         continue
#
#                     # Split command and arguments
#                     parts = command.split()
#                     if not parts:
#                         continue
#
#                     # Handle context navigation and command execution
#                     if parts[0] in ["settings", "ingest", "nlp"]:
#                         # First try to change context
#                         if settings_manager.change_context(parts[0]):
#                             console.print(f"[green]Moved to {parts[0]} context[/green]")
#                             # If there are additional parts, try to execute them as a command
#                             if len(parts) > 1:
#                                 try:
#                                     app(parts[1:])
#                                 except SystemExit:
#                                     continue
#                                 except Exception as e:
#                                     console.print(f"[red]Error: {str(e)}[/red]")
#                             continue
#
#                     # If not a context change, try to execute as a command
#                     try:
#                         app(parts)
#                     except SystemExit:
#                         continue
#                     except Exception as e:
#                         console.print(f"[red]Error: {str(e)}[/red]")
#
#                 except KeyboardInterrupt:
#                     console.print("\n[yellow]Use 'exit' to quit[/yellow]")
#                     continue
#                 except EOFError:
#                     console.print("\n[yellow]Goodbye![/yellow]")
#                     sys.exit(0)
#
#     return app
#
#
# def show_help(console: Console):
#     """Show help information"""
#     table = Table(title="Available Commands")
#     table.add_column("Command", style="cyan")
#     table.add_column("Description", style="green")
#
#     table.add_row("exit", "Exit the shell")
#     table.add_row("help", "Show this help message")
#     table.add_row("back", "Return to parent context")
#     table.add_row("settings", "Enter settings context")
#     # Add other available contexts/commands
#
#     console.print(table)

import typer
from rich.console import Console
from rich.table import Table
import sys
from donor_db_builder.config import SettingsManager
from scratch import settings


def interactive_shell(settings_manager: SettingsManager) -> typer.Typer:
    """Interactive shell mode"""
    app = typer.Typer(help="Donor DB Builder - NYS Campaign Finance Data Import Tool")
    console = Console()

    # Add command groups
    settings_app = typer.Typer(help="Settings management")
    app.add_typer(settings.app, name="settings")

    @app.callback(invoke_without_command=True)
    def main(ctx: typer.Context):
        """
        Donor DB Builder CLI - Interactive Mode
        """
        ctx.obj = settings_manager

        if ctx.invoked_subcommand is None:
            console.print("[bold green]Interactive shell mode[/bold green]")
            console.print("Type 'exit' to quit")
            console.print("Type 'help' for help")
            console.print("Type 'back' to return to parent context")

            while True:
                try:
                    prompt = f"{settings_manager.get_prompt_path()}> "
                    command = typer.prompt(prompt, type=str)

                    if not command:
                        continue

                    if command.lower() == "exit":
                        console.print("[yellow]Goodbye![/yellow]")
                        sys.exit(0)

                    if command.lower() == "back":
                        if settings_manager.change_context(".."):
                            console.print("[green]Moved to parent context[/green]")
                        else:
                            console.print("[yellow]Already at root context[/yellow]")
                        continue

                    if command.lower() == "help":
                        show_help(console)
                        continue

                    # Split command and arguments
                    parts = command.split()
                    if not parts:
                        continue

                    # Handle context navigation and command execution
                    if parts[0] == "settings":
                        # Change context first
                        settings_manager.change_context("settings")
                        console.print("[green]Moved to settings context[/green]")

                        # If there are additional parts, execute them as a command
                        if len(parts) > 1:
                            try:
                                settings.app(parts[1:])
                            except SystemExit:
                                continue
                            except Exception as e:
                                console.print(f"[red]Error: {str(e)}[/red]")
                        continue

                    # Try to execute as a command in current context
                    try:
                        if settings_manager.get_prompt_path() == "main/settings":
                            settings.app(parts)
                        else:
                            app(parts)
                    except SystemExit:
                        continue
                    except Exception as e:
                        console.print(f"[red]Error: {str(e)}[/red]")

                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                    continue
                except EOFError:
                    console.print("\n[yellow]Goodbye![/yellow]")
                    sys.exit(0)

    return app


def show_help(console: Console):
    """Show help information"""
    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")

    table.add_row("exit", "Exit the shell")
    table.add_row("help", "Show this help message")
    table.add_row("back", "Return to parent context")
    table.add_row("settings", "Enter settings context")
    # Add other available contexts/commands

    console.print(table)
