from __future__ import annotations

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

import pytermgui as ptg

DESCRIPTION = f'r2s is a terminal user interface for ROS 2.'

def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter
    )
    return parser.parse_args(args=argv)

def _define_layout() -> ptg.Layout:
    """Defines the application layout.

    Layouts work based on "slots" within them. Each slot can be given dimensions for
    both width and height. Integer values are interpreted to mean a static width, float
    values will be used to "scale" the relevant terminal dimension, and giving nothing
    will allow PTG to calculate the corrent dimension.
    """

    layout = ptg.Layout()

    # A header slot with a height of 1
    layout.add_slot("Header", height=10)
    layout.add_break()

    # A body slot that will fill the entire width, and the height is remaining
    layout.add_slot("Body")

    # A slot in the same row as body, using the full non-occupied height and
    # 20% of the terminal's height.
    layout.add_slot("Body right", width=0.2)

    layout.add_break()

    # A footer with a static height of 1
    layout.add_slot("Footer", height=1)

    return layout

def main(*, argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    with ptg.WindowManager() as manager:
        manager.layout = _define_layout()

        header = ptg.Window(
            "[app.header] Welcome to PyTermGUI ",
            box="EMPTY",
        )

        manager.add(header)

        footer = ptg.Window(ptg.Button("Quit", lambda *_: manager.stop()), box="EMPTY")

        # Since the second slot, body was not assigned to, we need to manually assign
        # to "footer"
        manager.add(footer, assign="footer")

        manager.add(ptg.Window("My sidebar"), assign="body_right")
        manager.add(ptg.Window("My body window"), assign="body")


if __name__ == '__main__':
    import sys
    main(argv=sys.argv[1:])
