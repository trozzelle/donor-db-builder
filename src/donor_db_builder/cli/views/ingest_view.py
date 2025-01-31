from functools import partial
from typing import cast, List, Set, Any
from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll, Vertical
from textual.events import Focus, Show
from textual.screen import ScreenResultCallbackType
from textual.widget import Widget
from textual.widgets import Input, TabbedContent, Label
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem, InputState
from donor_db_builder.settings import get_project_path
from rich.text import Text
from textual import log
import os
import polars as pd

# def get_path_suggestions(current_input_state: InputState) -> List[DropdownItem]:
#     current_input = current_input_state.value
#     if not current_input:
#         current_input = "."
#     path = Path(current_input)
#
#     if not path.is_absolute():
#         path = Path(get_project_path("root")) / path
#
#     if current_input.endswith("/"):
#         base_path = path
#         filter_text = path.name.lower()
#     else:
#         base_path = path.parent
#         filter_text = path.name.lower()
#
#     try:
#         # Get all items in directory and filter them
#         items = []
#         for path in base_path.iterdir():
#             name = path.name
#             if filter_text.lower() in name.lower():
#                 display_name = f"{name}/" if path.is_dir() else f"{name}"
#                 type_label = "DIR" if path.is_dir() else "FILE"
#                 items.append(
#                     DropdownItem(
#                         main=display_name,
#                         left_meta=Text(str("")),
#                         right_meta=Text(str("")),
#                     )
#                 )
#         log.warning(items)
#         ordered = sorted(
#             items, key=lambda x: (x.main.plain.startswith(current_input.lower()))
#         )
#         return ordered
#     except PermissionError:
#         return []


# def get_path_suggestions(
#     input_path: InputState, ignore_patterns: Set[str] = None
# ) -> List[str]:
#     PROJECT_ROOT = get_project_path("absolute")
#     partial_path = input_path.value
#     if ignore_patterns is None:
#         ignore_patterns = {".venv/*", ".*", "__pycache__/*", "*.pyc", "node_modules/*"}
#
#     # Convert to Path object and separate into directory and partial name
#     # path = PROJECT_ROOT / partial_path
#     # directory = path.parent if path.name else path
#     # prefix = path.name.lower()
#     # stem = path.stem
#
#     base_path = PROJECT_ROOT  # ..../Projects/donor-db-builder
#     path = base_path / partial_path
#     stem = path.stem if partial_path else None
#     directory = path.parent if stem is not None else path
#     prefix = stem
#     log.warning(f"""
#     partial_path: {partial_path}
#     path: {path}
#     directory: {directory}
#     prefix: {prefix}
#     """)
#     try:
#         completions = []
#         # Scan directory
#         for entry in os.scandir(str(directory)):
#             # Check if entry matches any ignore patterns
#             if any(Path(entry.path).match(pattern) for pattern in ignore_patterns):
#                 continue
#
#             name = entry.name
#
#             # Show all items if path is directory
#             if path.is_dir():
#                 DropdownItem(
#                     main=(f"{name}/" if entry.is_dir() else name),
#                     left_meta=str(""),
#                     right_meta=str(""),
#                 )
#
#             elif name.lower().startswith(prefix):
#                 completions.append(
#                     DropdownItem(
#                         main=(f"{name}/" if entry.is_dir() else name),
#                         left_meta=str(""),
#                         right_meta=str(""),
#                     )
#                 )
#
#         return sorted(
#             completions,
#             key=lambda x: x.main.plain.lower(),
#         )
#
#     except (PermissionError, FileNotFoundError):
#         return []

PROJECT_ROOT = get_project_path("root")


def get_path_completions(
    input_path: InputState, ignore_patterns: Set[str] = None
) -> List[str]:
    input_path = input_path.value
    current_path = PROJECT_ROOT / input_path
    stem = current_path.stem
    # current_directory = current_path.parent if input_path else current_path

    if input_path is None or current_path.is_dir():
        current_directory = current_path
    else:
        current_directory = current_path.parent

    ignore_patterns = [
        ".venv/*",
        ".*",
        "__pycache__/*",
        "*.pyc",
        "node_modules/*",
    ]

    try:
        completions = []
        # Scan directory
        for entry in os.scandir(str(current_directory)):
            # Check if entry matches any ignore patterns
            if any(Path(entry.path).match(pattern) for pattern in ignore_patterns):
                continue

            name = entry.name

            # Show all items if path is directory
            if current_path.is_dir():
                completions.append(
                    DropdownItem(
                        main=(f"{name}/" if entry.is_dir() else name),
                        left_meta=str(""),
                        right_meta=str(""),
                    )
                )

            elif name.lower().startswith(stem):
                completions.append(
                    DropdownItem(
                        main=(f"{name}/" if entry.is_dir() else name),
                        left_meta=str(""),
                        right_meta=str(""),
                    )
                )

        items = sorted(
            completions,
            key=lambda x: x.main.plain.lower(),
        )

        return items

    except (PermissionError, FileNotFoundError):
        return []


class IngestView(Vertical):
    DEFAULT_CSS = """
    IngestView {
        /*layers: textual-autocomplete;*/
        height: 1fr;
        width: 1fr;
        # #filepath {
        #     margin-bottom: 1;
        # }
        GridList {
            min-height: 1fr;
        }
    }
    
    
            #filepath {
            width: 75%;
        }
        
        #filepath-label {
            width: 100%;
            content-align: center middle;
            color: $secondary;
            text-style: bold;
            padding: 1 1 1 0;
        }
        
        #path-dropdown {
            max-width: 40;
            max-height: 6;
            /*border-left: wide magenta;*/
            /*scrollbar-color: greenyellow;*/
            /*background: darkgreen;*/
        }
        #info-text {
            padding: 1 8;
            color: $text;
            height: auto;
            width: 100%;
            text-align: center;
        }
    
    """

    filepath_input: Input
    file: Any
    filepath_root: Path = get_project_path("absolute")
    current_directory: Path

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.sub_title = "Ingest"
        self.filepath_input = Input(id="filepath", placeholder="Enter the file")
        self.file = None

    def _on_show(self, event: Show) -> None:
        with self.screen.prevent(TabbedContent.TabActivated):
            self.filepath_input.focus()

    def compose(self) -> ComposeResult:
        with self.prevent(Focus, TabbedContent.TabActivated):
            yield Container(
                Label("File:", id="filepath-label"),
                AutoComplete(
                    self.filepath_input,
                    Dropdown(
                        items=get_path_completions,
                        id="path-dropdown",
                    ),
                ),
            )
            with VerticalScroll():
                pass

    async def on_mount(self) -> None:
        pass

    def action_filepath_input_focus(self) -> None:
        self.filepath_input.focus()

    def action_submit(self) -> None:
        path = self.filepath_input.value

        try:
            if path.lower().endswith(".csv"):
                self.file = pd.read_csv(path)
                log.warning(self.file)
        except FileNotFoundError:
            log.error(f"File {path} not found")
            pass
        except Exception as e:
            log.error(e)
            pass
