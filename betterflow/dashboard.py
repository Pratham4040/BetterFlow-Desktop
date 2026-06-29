"""
Terminal dashboard — beautiful rich TUI showing stats and live status.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from betterflow import APP_NAME, APP_VERSION, APP_TAGLINE
from betterflow.config import CONFIG_FILE
from betterflow.stats import (
    get_today_stats, get_streak, get_week_words,
    get_month_words, get_total_stats,
)

console = Console()


def print_dashboard(cfg: dict):
    """Print the full terminal dashboard on startup."""
    console.clear()

    # Header
    header = Text()
    header.append("  ☕ ", style="bold")
    header.append(f"{APP_NAME}", style="bold #d97757")
    header.append(f" v{APP_VERSION}", style="dim")
    header.append(f"  —  {APP_TAGLINE}", style="italic #b8a99e")

    console.print(Panel(header, border_style="#d97757", box=box.ROUNDED))
    console.print()

    # Stats cards
    today = get_today_stats()
    streak = get_streak()
    week = get_week_words()
    month = get_month_words()
    total = get_total_stats()

    stats_table = Table(box=box.SIMPLE_HEAD, show_edge=False, pad_edge=False)
    stats_table.add_column("📅 Today", justify="center", style="#7bc47f")
    stats_table.add_column("🔥 Streak", justify="center", style="#ff9a6c")
    stats_table.add_column("📊 This Week", justify="center", style="#84b6eb")
    stats_table.add_column("📈 This Month", justify="center", style="#a2eeef")
    stats_table.add_column("🏆 All Time", justify="center", style="#ffd93d")

    stats_table.add_row(
        f"{today['words']} words\n{today['dictations']} dictations",
        f"{streak} day{'s' if streak != 1 else ''}",
        f"{week} words",
        f"{month} words",
        f"{total['total_words']} words\n{total['days_active']} days",
    )

    console.print(Panel(stats_table, title="[bold]📊 Your Stats[/]", border_style="#3d2e25", box=box.ROUNDED))
    console.print()


    # Config info
    config_table = Table(box=None, show_header=False, pad_edge=False)
    config_table.add_column("Key", style="#b8a99e", min_width=12)
    config_table.add_column("Value", style="#fff5e6")

    config_table.add_row("Hotkey", f"[bold #d97757]{cfg['hotkey']}[/]")
    config_table.add_row("Model", f"{cfg['model_size']} ({cfg['device']})")
    config_table.add_row("Language", cfg.get('language') or "auto-detect")
    config_table.add_row("Voice stop", "[#7bc47f]say 'stop listening'[/]")
    config_table.add_row("Config", str(CONFIG_FILE))

    console.print(Panel(config_table, title="[bold]⚙️  Settings[/]", border_style="#3d2e25", box=box.ROUNDED))
    console.print()

    # Controls
    controls = Text()
    controls.append("  🎙️  ", style="bold")
    controls.append("Click icon", style="#d97757")
    controls.append(" or press ", style="dim")
    controls.append(cfg['hotkey'], style="bold #d97757")
    controls.append(" to start dictating\n", style="dim")
    controls.append("  🛑  ", style="bold")
    controls.append("Say ", style="dim")
    controls.append("'stop listening'", style="bold #ff6b6b")
    controls.append(" or press hotkey again to stop\n", style="dim")
    controls.append("  👆  ", style="bold")
    controls.append("Right-click icon", style="dim")
    controls.append(" for Settings & Quit", style="dim")

    console.print(Panel(controls, title="[bold]🎮 Controls[/]", border_style="#3d2e25", box=box.ROUNDED))
    console.print()


def print_dictation_result(text: str, duration: float, transcribe_time: float):
    """Print a completed dictation to the terminal."""
    word_count = len(text.split())
    console.print(f"  [#7bc47f]✓[/] [bold]{word_count}[/] words in [dim]{duration:.1f}s[/] (transcribed in {transcribe_time:.1f}s)")
    # Show first 80 chars of the text
    preview = text[:80] + ("..." if len(text) > 80 else "")
    console.print(f"    [dim]→[/] {preview}")
    console.print()


def print_status(message: str, style: str = "dim"):
    """Print a status message."""
    console.print(f"  [dim]•[/] [{style}]{message}[/]")
