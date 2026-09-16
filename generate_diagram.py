"""Renders architecture.png -- the 3-tier diagram for the README.

Run:  python generate_diagram.py
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BLUE, GREEN, ORANGE, GREY, GOLD = "#1a56b0", "#137333", "#b06000", "#5f6368", "#8a6d00"
PRESENTATION = ("#e8f0fe", BLUE)
BUSINESS = ("#e6f4ea", GREEN)
DATA = ("#fdf0e3", ORANGE)
STORAGE = ("#f1f3f4", GREY)
NOTE = ("#fdf7e3", GOLD)
INTERFACE = ("#ffffff", GREEN)

X0, X1 = 6.0, 70.0          # tier boxes
N0, N1 = 73.5, 99.0         # notes column
LABEL_X, DETAIL_X = X0 + 4, X0 + 25


def box(ax, x0, y0, x1, y1, colors, radius=1.2, lw=1.8, z=2):
    face, edge = colors
    ax.add_patch(
        FancyBboxPatch(
            (x0, y0), x1 - x0, y1 - y0,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=face, edgecolor=edge, linewidth=lw, zorder=z,
        )
    )


def text(ax, x, y, s, size=8.5, weight="normal", color="#202124", ha="left",
         style="normal", rotation=0, **kwargs):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha,
            va="center", style=style, rotation=rotation, zorder=5, **kwargs)


def arrow(ax, x0, y0, x1, y1, color="#3c4043", dashed=False, lw=1.7):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=15, color=color,
            linewidth=lw, linestyle="--" if dashed else "-", zorder=4,
            shrinkA=0, shrinkB=0,
        )
    )


def tier(ax, y0, y1, colors, name, folder, rows):
    """rows: (label, detail) | ("", detail) continuation | ("!", warning)."""
    box(ax, X0, y0, X1, y1, colors)
    edge = colors[1]
    text(ax, X0 + 3, y1 - 3.2, name, size=11.5, weight="bold", color=edge)
    text(ax, X1 - 3, y1 - 3.2, folder, size=9.5, weight="bold", color=edge, ha="right")
    ax.plot([X0 + 3, X1 - 3], [y1 - 5.4, y1 - 5.4], color=edge, lw=0.9, alpha=0.45, zorder=3)

    y = y1 - 8.2
    for label, detail in rows:
        if label == "!":
            text(ax, LABEL_X, y, detail, size=8.2, color="#d93025", style="italic")
            y -= 3.1
        elif label == "":
            text(ax, DETAIL_X, y, detail, size=8.3, color="#3c4043")
            y -= 2.8
        else:
            text(ax, LABEL_X, y, label, size=8.7, weight="bold")
            text(ax, DETAIL_X, y, detail, size=8.3, color="#3c4043")
            y -= 3.2


def note(ax, y_top, title, lines, subtitle=None, code_from=None):
    step = 2.15
    head = 3.0 + (2.2 if subtitle else 0)
    y_bottom = y_top - head - step * len(lines) - 1.6
    box(ax, N0, y_bottom, N1, y_top, NOTE, radius=1.0, lw=1.5)
    text(ax, N0 + 2, y_top - 2.8, title, size=9.5, weight="bold", color=GOLD)
    if subtitle:
        text(ax, N0 + 2, y_top - 5.0, subtitle, size=7.4, weight="bold", color=GOLD)
    y = y_top - head - 1.4
    for i, line in enumerate(lines):
        mono = code_from is not None and i >= code_from
        text(ax, N0 + 2, y, line, size=7.1 if mono else 7.8, color="#3c4043",
             **({"family": "monospace"} if mono else {}))
        y -= step
    return y_bottom


def main():
    fig, ax = plt.subplots(figsize=(13.5, 15.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    text(ax, 50, 97.5, "Library Management System", size=19, weight="bold", ha="center")
    text(ax, 50, 94.6, "3-Tier Architecture   |   Python 3   |   IT457 Lab 4",
         size=10.5, color=GREY, ha="center")

    # ---------------- actor ----------------
    box(ax, 28, 90.0, 48, 93.5, ("#ffffff", GREY), radius=0.8, lw=1.4)
    text(ax, 38, 91.75, "USER", size=9.5, weight="bold", ha="center", color="#3c4043")
    arrow(ax, 38, 90.0, 38, 88.0, color=GREY)
    text(ax, 39.5, 89.0, "terminal  or  browser", size=7.8, color=GREY)

    # ---------------- presentation ----------------
    tier(ax, 71.0, 88.0, PRESENTATION, "PRESENTATION TIER", "/presentation", [
        ("cli.py", "LibraryCLI  -  menu, prompts, table output"),
        ("web_app.py", "Flask routes + templates  -  the same job over HTTP"),
        ("!", "both only collect input and display output   -   NO rules, NO SQL"),
    ])

    arrow(ax, 20, 71.0, 20, 66.0, color=BLUE)
    text(ax, 21.5, 69.8, "calls  service.add_book(...)", size=7.9, color=BLUE)
    arrow(ax, 58, 66.0, 58, 71.0, color=GREEN)
    text(ax, 56.5, 67.6, "returns Book  /  raises LibraryError", size=7.9,
         color=GREEN, ha="right")

    # ---------------- business ----------------
    tier(ax, 33.0, 66.0, BUSINESS, "BUSINESS TIER", "/business", [
        ("book_service.py", "BookService  -  every use case, orchestration"),
        ("validators.py", "title / author non-empty   -   ISBN 10 or 13 digits"),
        ("", "year not in the future   -   quantity never negative"),
        ("book_service.py", "cannot check out when quantity == 0"),
        ("models.py", "Book  -  the domain object"),
        ("errors.py", "ValidationError, BookNotFoundError, OutOfStockError"),
    ])

    box(ax, X0 + 3, 34.2, X1 - 3, 39.4, INTERFACE, radius=0.8, lw=1.8, z=3)
    text(ax, X0 + 5, 37.7, "repository.py   ->   BookRepository   (abstract interface)",
         size=8.8, weight="bold", color=GREEN)
    text(ax, X0 + 5, 35.6, "add   get_all   get_by_id   find_by_isbn   search   update   delete",
         size=7.7, color=GREY)

    arrow(ax, 20, 33.0, 20, 27.0, color=GREEN)
    text(ax, 21.5, 31.4, "calls the interface  repo.get_by_id(3)", size=7.9, color=GREEN)
    arrow(ax, 58, 27.0, 58, 33.0, color=ORANGE)
    text(ax, 56.5, 28.6, "returns  Book  or  None", size=7.9, color=ORANGE, ha="right")

    # ---------------- data ----------------
    tier(ax, 11.0, 27.0, DATA, "DATA TIER", "/data", [
        ("sqlite_repository.py", "SQLiteBookRepository     implements the interface"),
        ("in_memory_repository.py", "InMemoryBookRepository   implements the interface"),
        ("!", "NO validation   -   NO formatting   -   no idea who is asking"),
    ])

    # ---------------- storage ----------------
    box(ax, 8, 2.8, 33, 8.4, STORAGE, radius=0.8, lw=1.5)
    text(ax, 20.5, 6.4, "library.db", size=9, weight="bold", ha="center", color="#3c4043")
    text(ax, 20.5, 4.3, "SQLite file on disk", size=7.8, ha="center", color=GREY)
    box(ax, 43, 2.8, 68, 8.4, STORAGE, radius=0.8, lw=1.5)
    text(ax, 55.5, 6.4, "Python list", size=9, weight="bold", ha="center", color="#3c4043")
    text(ax, 55.5, 4.3, "in RAM, lost on exit", size=7.8, ha="center", color=GREY)
    arrow(ax, 20.5, 11.0, 20.5, 8.4, color=GREY, lw=1.4)
    arrow(ax, 55.5, 11.0, 55.5, 8.4, color=GREY, lw=1.4)

    # ------- dependency inversion: data implements the business interface -------
    ax.plot([2.8, 2.8], [19.0, 36.8], color=GREEN, lw=1.7, ls="--", zorder=4)
    ax.plot([X0, 2.8], [19.0, 19.0], color=GREEN, lw=1.7, ls="--", zorder=4)
    arrow(ax, 2.8, 36.8, X0 + 3, 36.8, color=GREEN, dashed=True)
    text(ax, 1.6, 28.0, "implements", size=8, weight="bold", color=GREEN,
         ha="center", rotation=90)

    # ---------------- notes ----------------
    note(ax, 88.0, "LAYER RULES", [
        "Each tier talks only to the",
        "tier directly below it.",
        "",
        "Presentation holds no rules",
        "and never touches the data.",
        "",
        "Business depends on the",
        "interface, not on a store.",
        "",
        "Data holds no rules and no",
        "display logic.",
    ])

    note(ax, 59.0, "main.py", [
        "The only file that names a",
        "concrete repository:",
        "",
        "repo = SQLiteBookRepository()",
        "svc  = BookService(repo)",
    ], subtitle="COMPOSITION ROOT", code_from=3)
    arrow(ax, N0, 47.0, X1 + 0.6, 47.0, color=GOLD, dashed=True, lw=1.4)
    text(ax, 71.9, 49.2, "injects", size=7.6, weight="bold", color=GOLD,
         ha="center", rotation=90)

    note(ax, 38.0, "SWAP TEST", [
        "Both repositories satisfy the",
        "same interface, so swapping",
        "them changes one line in",
        "main.py and nothing at all",
        "in /business.",
        "",
        "swap_test.py runs one",
        "scenario against both and",
        "compares the transcripts.",
    ])

    text(ax, 50, 0.6,
         "Dependency direction:   presentation  ->  business  ->  BookRepository  <-  data       "
         "(the data tier depends on the business tier, never the reverse)",
         size=8.2, ha="center", color=GREY, style="italic")

    fig.savefig("architecture.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("Wrote architecture.png")


if __name__ == "__main__":
    main()
