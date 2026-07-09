'''
----------------------------------------------------------------------------------------------------------------------
                                                TruNorth Navbar
----------------------------------------------------------------------------------------------------------------------
Reusable top navigation bar for the TruNorth Timesheet dashboard.
Logo on the left, vertical separator, and configurable page links with active/inactive styling.
----------------------------------------------------------------------------------------------------------------------
'''
# import libraries
from dataclasses import dataclass

import dash_mantine_components as dmc


# nav page model
@dataclass(frozen=True)
class NavPage:
    label: str
    href: str


# navbar component
class Navbar:
    INACTIVE_COLOR = "gray"
    ACTIVE_COLOR = "dark"
    SEPARATOR_COLOR = "gray.3"

    def __init__(
        self,
        logo_src: str,
        pages: list[NavPage],
        active_path: str = "/",
        logo_height: int = 48,
    ) -> None:
        self.logo_src = logo_src
        self.pages = pages
        self.active_path = active_path
        self.logo_height = logo_height

    def _is_active(self, href: str) -> bool:
        return self.active_path == href

    def _nav_item(self, page: NavPage) -> dmc.Anchor:
        is_active = self._is_active(page.href)

        return dmc.Anchor(
            page.label,
            href=page.href,
            underline="never",
            c=self.ACTIVE_COLOR if is_active else self.INACTIVE_COLOR,
            fw=600 if is_active else 400,
            size="md",
        )

    def _separator(self) -> dmc.Divider:
        return dmc.Divider(
            orientation="vertical",
            size="sm",
            color=self.SEPARATOR_COLOR,
            h=self.logo_height,
        )

    def layout(self) -> dmc.Box:
        return dmc.Box(
            [
                dmc.Image(
                    src=self.logo_src,
                    h=self.logo_height,
                    w="auto",
                    maw=280,
                    fit="contain",
                    alt="TruNorth logo",
                    style={"flexShrink": 0},
                ),
                self._separator(),
                dmc.Group(
                    [self._nav_item(page) for page in self.pages],
                    gap="lg",
                    wrap="nowrap",
                    style={"flexShrink": 0},
                ),
            ],
            py="md",
            px="md",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "alignItems": "center",
                "gap": "1rem",
                "borderBottom": "1px solid var(--mantine-color-gray-3)",
            },
        )
