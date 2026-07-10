'''
----------------------------------------------------------------------------------------------------------------------
                                                TruNorth Footer
----------------------------------------------------------------------------------------------------------------------
Reusable footer for the TruNorth Timesheet dashboard.
Supports copyright, horizontal resource links, and a developer docs row on a light gray background.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
from dataclasses import dataclass
from urllib.parse import quote

import dash_mantine_components as dmc
from dash import html


# footer models
@dataclass(frozen=True)
class FooterLink:
    label: str
    href: str


# footer component
class Footer:
    BACKGROUND_COLOR = "gray.1"
    TEXT_COLOR = "dark"
    LINK_COLOR = "dark"

    def __init__(
        self,
        links: list[FooterLink],
        developer_docs: FooterLink,
        github_href: str,
        copyright_text: str,
    ) -> None:
        self.links = links
        self.developer_docs = developer_docs
        self.github_href = github_href
        self.copyright_text = copyright_text

    def _icon_size_px(self, size: str) -> int:
        return {"sm": 16, "md": 18, "lg": 20}.get(size, 18)

    def _github_icon(self, size: str = "md") -> html.Img:
        icon_px = self._icon_size_px(size)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{icon_px}" '
            f'height="{icon_px}" viewBox="0 0 24 24" fill="#212529">'
            '<path d="M12 2C6.477 2 2 6.484 2 12.021c0 4.428 2.865 8.184 '
            "6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703"
            "-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11"
            "-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 "
            "1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338"
            "-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688"
            "-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 "
            "9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 "
            "2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 "
            "1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309"
            ".678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58"
            '.688.482A10.019 10.019 0 0022 12.021C22 6.484 17.522 2 12 2z"/>'
            "</svg>"
        )

        return html.Img(
            src=f"data:image/svg+xml,{quote(svg)}",
            alt="GitHub",
            style={
                "width": f"{icon_px}px",
                "height": f"{icon_px}px",
                "display": "block",
            },
        )

    def _footer_link(
        self,
        link: FooterLink,
        size: str = "md",
        bold: bool = False,
    ) -> dmc.Anchor:
        return dmc.Anchor(
            link.label,
            href=link.href,
            underline="never",
            c=self.LINK_COLOR,
            size=size,
            fw=700 if bold else 400,
        )

    def _copyright_row(self) -> dmc.Text:
        return dmc.Text(
            self.copyright_text,
            c=self.TEXT_COLOR,
            size="sm",
            fs="italic",
            ta="center",
            w="100%",
        )

    def _resource_links_row(self) -> dmc.Group:
        return dmc.Group(
            [self._footer_link(link, bold=True) for link in self.links],
            gap="lg",
            justify="center",
            wrap="wrap",
            align="center",
            w="100%",
        )

    def _separator(self) -> dmc.Divider:
        return dmc.Divider(
            orientation="vertical",
            size="sm",
            color="gray.4",
            h=18,
        )

    def _developer_row(self) -> dmc.Group:
        return dmc.Group(
            [
                self._footer_link(self.developer_docs),
                self._separator(),
                dmc.Anchor(
                    self._github_icon(),
                    href=self.github_href,
                    underline="never",
                ),
            ],
            gap="sm",
            justify="flex-end",
            align="center",
            wrap="nowrap",
            w="100%",
        )

    def layout(self) -> dmc.Box:
        return dmc.Box(
            dmc.Container(
                [
                    self._copyright_row(),
                    self._resource_links_row(),
                    self._developer_row(),
                ],
                fluid=True,
                px="xl",
                py="xl",
                style={"display": "flex", "flexDirection": "column", "gap": "1rem"},
            ),
            bg=self.BACKGROUND_COLOR,
            c=self.TEXT_COLOR,
            style={"borderTop": "1px solid var(--mantine-color-gray-3)"},
        )
