"""
Menu system for mini arcade core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from mini_arcade_core.backend import Backend
from mini_arcade_core.backend.events import Event, EventType
from mini_arcade_core.backend.keys import Key
from mini_arcade_core.backend.types import Color
from mini_arcade_core.engine.commands import Command, QuitCommand
from mini_arcade_core.runtime.input_frame import InputFrame
from mini_arcade_core.scenes.sim_scene import (
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins import (
    BaseQueuedRenderSystem,
    InputIntentSystem,
)


@dataclass(frozen=True)
class MenuItem:
    """
    Represents a single item in a menu.

    :ivar label (str): The text label of the menu item.
    :ivar on_select (BaseCommand): The action to perform when the item is selected.
    """

    id: str
    label: str
    command_factory: Callable[[], Command]
    label_fn: Optional[Callable[[object], str]] = None

    def resolved_label(self, ctx: object) -> str:
        """
        Get the resolved label for this menu item.

        :param ctx: The current ctx instance.
        :type ctx: object

        :return: The resolved label string.
        :rtype: str
        """
        return self.label_fn(ctx) if self.label_fn else self.label


# Justification: Data container for styling options needs
# some attributes.
# pylint: disable=too-many-instance-attributes
@dataclass
class MenuStyle:
    """
    Styling options for the Menu.

    :ivar normal (Color): Color for unselected items.
    :ivar selected (Color): Color for the selected item.
    :ivar line_height (int): Vertical spacing between items.
    :ivar title_color (Color): Color for the title text.
    :ivar title_spacing (int): Vertical space between title and first item.
    :ivar title_margin_bottom (int): Additional margin below the title.
    :ivar background_color (Color | None): Solid background color for the menu.
    :ivar overlay_color (Color | None): Full-screen overlay color.
    :ivar panel_color (Color | None): Color for the panel behind content.
    :ivar panel_padding_x (int): Horizontal padding inside the panel.
    :ivar panel_padding_y (int): Vertical padding inside the panel.
    :ivar button_enabled (bool): Whether to render items as buttons.
    :ivar button_fill (Color): Fill color for buttons.
    :ivar button_border (Color): Border color for buttons.
    :ivar button_selected_border (Color): Border color for the selected button.
    :ivar button_width (int | None): Fixed width for buttons, or None for auto-fit.
    :ivar button_height (int): Fixed height for buttons.
    :ivar button_gap (int): Vertical gap between buttons.
    :ivar button_padding_x (int): Horizontal padding inside buttons.
    :ivar hint (str | None): Optional hint text to display at the bottom.
    :ivar hint_color (Color): Color for the hint text.
    :ivar hint_margin_bottom (int): Additional margin below the hint text.
    :ivar title_font_size (int): Font size for the title text.
    :ivar hint_font_size (int): Font size for the hint text.
    :ivar item_font_size (int): Font size for the menu items.
    """

    normal: Color = (220, 220, 220)
    selected: Color = (255, 255, 0)

    # Layout
    line_height: int = 28
    title_color: Color = (255, 255, 255)
    title_spacing: int = 18
    title_margin_bottom: int = 20

    # Scene background (solid)
    background_color: Color | None = None  # e.g. BACKGROUND

    # Optional full-screen overlay (dim)
    overlay_color: Color | None = None  # e.g. (0,0,0,0.5) for pause

    # Panel behind content (optional)
    panel_color: Color | None = None
    panel_padding_x: int = 24
    panel_padding_y: int = 18

    # Button rendering (optional)
    button_enabled: bool = False
    button_fill: Color = (30, 30, 30, 1.0)
    button_border: Color = (120, 120, 120, 1.0)
    button_selected_border: Color = (255, 255, 0, 1.0)
    button_width: int | None = (
        None  # if None -> auto-fit to longest label + padding
    )
    button_height: int = 40
    button_gap: int = 20
    button_padding_x: int = 20  # used for auto-fit + text centering

    # Hint footer (optional)
    hint: str | None = None
    hint_color: Color = (200, 200, 200)
    hint_margin_bottom: int = 50

    # Font sizes (not used directly here, but for reference)
    title_font_size = 44
    hint_font_size = 14
    item_font_size = 24


class Menu:
    """A simple text-based menu system."""

    # TODO: Solve too-many-arguments warning later
    # Justification: Multiple attributes for menu state
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        items: Sequence[MenuItem],
        *,
        viewport: tuple[int, int] | None = None,
        title: str | None = None,
        style: MenuStyle | None = None,
        on_select: Optional[Callable[[MenuItem], None]] = None,
    ):
        """
        :param items: Sequence of MenuItem instances to display.
        :type items: Sequence[MenuItem]

        :param viewport: Viewport size for the menu's layout and centering.
        :type viewport: tuple[int, int] | None

        :param title: Optional title text for the menu.
        :type title: str | None

        :param style: Optional MenuStyle for customizing appearance.
        :type style: MenuStyle | None

        :param on_select: Optional callback when an item is selected.
        :type on_select: Optional[Callable[[MenuItem], None]]
        """
        self.items = list(items)
        self.viewport = viewport
        self.title = title
        self.style = style or MenuStyle()
        self.selected_index = 0
        self._on_select = on_select
        self._max_content_w_seen = 0
        self._max_button_w_seen = 0
        self.stable_width = True

    # pylint: enable=too-many-arguments

    def set_items(self, items: Sequence[MenuItem]):
        """Set the menu items.
        :param items: Sequence of new MenuItem instances.
        :type items: Sequence[MenuItem]
        """
        self.items = list(items)

    def set_selected_index(self, index: int):
        """Set the selected index of the menu.
        :param index: New selected index.
        :type index: int
        """
        if 0 <= index < len(self.items):
            self.selected_index = index

    def set_labels(self, labels: Sequence[str]):
        """Set the labels of the menu items.
        :param labels: Sequence of new labels for the menu items.
        :type labels: Sequence[str]
        """
        for index, label in enumerate(labels):
            if index < len(self.items):
                item = self.items[index]
                self.items[index] = MenuItem(
                    id=item.id,
                    label=label,
                    command_factory=item.command_factory,
                    label_fn=item.label_fn,
                )

    def move_up(self):
        """Move the selection up by one item, wrapping around if necessary."""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)

    def move_down(self):
        """Move the selection down by one item, wrapping around if necessary."""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)

    def select(self):
        """Select the currently highlighted item, invoking its action."""
        if not self.items:
            return
        item = self.items[self.selected_index]
        if self._on_select is not None:
            self._on_select(item)

    def handle_event(
        self,
        event: Event,
        *,
        up_key: int,
        down_key: int,
        select_key: int,
    ) -> bool:
        """
        Handle an input event to navigate the menu.

        :param event: The input event to handle.
        :type event: Event

        :param up_key: Key code for moving selection up.
        type up_key: int

        :param down_key: Key code for moving selection down.
        :type down_key: int

        :param select_key: Key code for selecting the current item.
        :type select_key: int
        """
        if event.type != EventType.KEYDOWN or event.key is None:
            return False

        if event.key == up_key:
            self.move_up()
            return True
        if event.key == down_key:
            self.move_down()
            return True
        if event.key == select_key:
            self.select()
            return True

        return False

    # TODO: Delegate drawing to a renderer class later
    def draw(self, surface: Backend):
        """
        Draw the menu onto the given backend surface.

        :param surface: The backend surface to draw on.
        :type surface: Backend
        """
        if self.viewport is None:
            raise ValueError(
                "Menu requires viewport=(width, height) for centering/layout"
            )

        vw, vh = self.viewport

        # 0) Solid background (for main menus)
        if self.style.background_color is not None:
            surface.render.draw_rect(
                0, 0, vw, vh, color=self.style.background_color
            )

        # 1) Overlay (for pause, etc.)
        if self.style.overlay_color is not None:
            surface.render.draw_rect(
                0, 0, vw, vh, color=self.style.overlay_color
            )
        # 2) Compute menu content bounds (panel area)
        content_w, content_h, title_h = self._measure_content(surface)

        pad_x, pad_y = self.style.panel_padding_x, self.style.panel_padding_y
        panel_w = content_w + pad_x * 2
        panel_h = content_h + pad_y * 2

        x0 = (vw - panel_w) // 2
        y0 = (vh - panel_h) // 2

        # Optional vertical offset if you add it later:
        # y0 += self.style.center_offset_y

        # 3) Panel (optional)
        if self.style.panel_color is not None:
            surface.render.draw_rect(
                x0, y0, panel_w, panel_h, color=self.style.panel_color
            )

        # 4) Draw title + items
        cursor_y = y0 + pad_y
        x_center = x0 + (panel_w // 2)

        if self.title:
            self._draw_text_center_x(
                surface,
                x_center,
                cursor_y,
                self.title,
                color=self.style.title_color,
                font_size=self.style.title_font_size,
            )
            cursor_y += (
                title_h
                + self.style.title_spacing
                + self.style.title_margin_bottom
            )

        if self.style.button_enabled:
            self._draw_buttons(surface, x_center, cursor_y)
        else:
            self._draw_text_items(surface, x_center, cursor_y)

        # 5) Hint footer (optional)
        if self.style.hint:
            self._draw_text_center_x(
                surface,
                vw // 2,
                vh - self.style.hint_margin_bottom,
                self.style.hint,
                color=self.style.hint_color,
                font_size=self.style.hint_font_size,
            )

    def _draw_text_items(self, surface: Backend, x_center: int, cursor_y: int):
        for i, item in enumerate(self.items):
            color = (
                self.style.selected
                if i == self.selected_index
                else self.style.normal
            )
            self._draw_text_center_x(
                surface,
                x_center,
                cursor_y + i * self.style.line_height,
                item.label,
                color=color,
                font_size=self.style.item_font_size,
            )

    # TODO: Solve too-many-locals warning later
    # Justification: Local variables for layout calculations
    # pylint: disable=too-many-locals
    def _draw_buttons(self, surface: Backend, x_center: int, cursor_y: int):
        # Determine button width: fixed or auto-fit
        if self.style.button_width is not None:
            bw = self.style.button_width
        else:
            max_label_w = 0
            for it in self.items:
                w, _ = surface.text.measure(
                    it.label, font_size=self.style.item_font_size
                )
                max_label_w = max(max_label_w, w)
            bw = max_label_w + self.style.button_padding_x * 2

            # ✅ Sticky button width (never shrink)
            if self.stable_width:
                self._max_button_w_seen = max(self._max_button_w_seen, bw)
                bw = self._max_button_w_seen

        bh = self.style.button_height
        gap = self.style.button_gap

        # We treat cursor_y as “top of first button”
        for i, item in enumerate(self.items):
            y = cursor_y + i * (bh + gap)
            x = x_center - bw // 2

            selected = i == self.selected_index
            border = (
                self.style.button_selected_border
                if selected
                else self.style.button_border
            )

            # Border rect
            surface.render.draw_rect(
                x - 4, y - 4, bw + 8, bh + 8, color=border
            )
            # Fill rect
            surface.render.draw_rect(
                x, y, bw, bh, color=self.style.button_fill
            )

            # Label color
            text_color = self.style.selected if selected else self.style.normal
            tw, th = surface.text.measure(
                item.label, font_size=self.style.item_font_size
            )
            tx = x + (bw - tw) // 2
            ty = y + (bh - th) // 2
            surface.text.draw(
                tx,
                ty,
                item.label,
                color=text_color,
                font_size=self.style.item_font_size,
            )

    # pylint: enable=too-many-locals

    def _measure_content(self, surface: Backend) -> tuple[int, int, int]:
        # If button mode: content height differs (button_height + gaps)
        max_w = 0
        title_h = 0

        # Title
        if self.title:
            tw, th = surface.text.measure(
                self.title, font_size=self.style.title_font_size
            )
            max_w = max(max_w, tw)
            title_h = th

        if not self.items:
            content_h = title_h if self.title else 0
            # Apply stable width even for empty items
            if self.stable_width:
                self._max_content_w_seen = max(self._max_content_w_seen, max_w)
                max_w = self._max_content_w_seen
            return max_w, content_h, title_h

        if self.style.button_enabled:
            # Width: fixed or auto-fit by longest label
            if self.style.button_width is not None:
                items_w = self.style.button_width
            else:
                max_label_w = 0
                for it in self.items:
                    w, _ = surface.text.measure(
                        it.label, font_size=self.style.item_font_size
                    )
                    max_label_w = max(max_label_w, w)
                items_w = max_label_w + self.style.button_padding_x * 2

            max_w = max(max_w, items_w)

            bh = self.style.button_height
            gap = self.style.button_gap
            items_h = len(self.items) * bh + (len(self.items) - 1) * gap
        else:
            for it in self.items:
                w, _ = surface.text.measure(
                    it.label, font_size=self.style.item_font_size
                )
                max_w = max(max_w, w)
            items_h = len(self.items) * self.style.line_height

        content_h = items_h
        if self.title:
            content_h += (
                title_h
                + self.style.title_spacing
                + self.style.title_margin_bottom
            )

        # Sticky width (never shrink)
        if self.stable_width:
            self._max_content_w_seen = max(self._max_content_w_seen, max_w)
            max_w = self._max_content_w_seen

        return max_w, content_h, title_h

    # TODO: Solve too-many-arguments warning later
    # Justification: Many arguments for text drawing utility
    # pylint: disable=too-many-arguments
    @staticmethod
    def _draw_text_center_x(
        surface: Backend,
        x_center: int,
        y: int,
        text: str,
        *,
        color: Color,
        font_size: int | None = None,
    ):
        w, _ = surface.text.measure(text, font_size=font_size)
        surface.text.draw(
            x_center - (w // 2), y, text, color=color, font_size=font_size
        )

    # pylint: enable=too-many-arguments

    def set_viewport(self, viewport: tuple[int, int]):
        """
        Set the viewport size for the menu.

        :param viewport: New viewport size.
        :type viewport: tuple[int, int]
        """
        if self.viewport is None:
            self.viewport = viewport
            return

        old_w, old_h = self.viewport
        new_w, new_h = viewport
        self.viewport = viewport

        # If the viewport changed (especially shrinking), allow layout to shrink too.
        if (new_w < old_w) or (new_h < old_h):
            self._max_content_w_seen = 0
            self._max_button_w_seen = 0


# pylint: enable=too-many-instance-attributes


@dataclass
class MenuWorld(BaseWorld):
    """
    Data model for menu scenes.

    :ivar selected (int): Currently selected menu item index.
    :ivar move_cooldown (float): Cooldown time between menu moves.
    :ivar _cooldown_timer (float): Internal timer for move cooldown.
    """

    entities: list = field(default_factory=list)
    selected: int = 0
    move_cooldown: float = 0.12
    _cooldown_timer: float = 0.0

    def step_timer(self, dt: float):
        """
        Step the internal cooldown timer.

        :param dt: Delta time since last update.
        :type dt: float
        """
        if self._cooldown_timer > 0:
            self._cooldown_timer = max(0.0, self._cooldown_timer - dt)

    def can_move(self) -> bool:
        """
        Check if the menu can move selection (cooldown elapsed).

        :return: True if movement is allowed, False otherwise.
        :rtype: bool
        """
        return self._cooldown_timer <= 0.0

    def consume_move(self):
        """Consume a move action and reset the cooldown timer."""
        self._cooldown_timer = self.move_cooldown


@dataclass(frozen=True)
class MenuIntent(BaseIntent):
    """
    Represents the user's intent in the menu for the current tick.

    :ivar move_up (bool): Whether the user intends to move up.
    :ivar move_down (bool): Whether the user intends to move down.
    :ivar select (bool): Whether the user intends to select the current item.
    :ivar quit (bool): Whether the user intends to quit the menu.
    """

    move_up: bool = False
    move_down: bool = False
    select: bool = False
    quit: bool = False


# TODO: Solve too-many-instance-attributes warning later
# Justification: Context for menu tick needs multiple attributes.
# pylint: disable=too-many-instance-attributes
@dataclass
class MenuTickContext(BaseTickContext[MenuWorld, MenuIntent]):
    """
    Context for a single tick of the menu scene.

    :ivar input_frame (InputFrame): The current input frame.
    :ivar dt (float): Delta time since last tick.
    :ivar menu (Menu): The Menu instance.
    :ivar model (MenuWorld): The MenuWorld instance.
    :ivar commands (CommandQueue): The command queue for pushing commands.
    :ivar intent (MenuIntent | None): The current menu intent.
    :ivar quit_cmd_factory (callable | None): Factory for quit command.
    :ivar packet (RenderPacket | None): The resulting render packet.
    """

    menu: "Menu" | None = None
    quit_cmd_factory: callable | None = None


# pylint: enable=too-many-instance-attributes


@dataclass
class MenuInputSystem(InputIntentSystem):
    """Converts InputFrame -> MenuIntent."""

    name: str = "menu_input"

    def build_intent(self, ctx: MenuTickContext):
        pressed = ctx.input_frame.keys_pressed
        return MenuIntent(
            move_up=Key.UP in pressed,
            move_down=Key.DOWN in pressed,
            select=(Key.ENTER in pressed) or (Key.SPACE in pressed),
            quit=Key.ESCAPE in pressed,
        )


@dataclass
class MenuNavigationSystem:
    """Menu navigation system."""

    name: str = "menu_nav"
    order: int = 20

    def step(self, ctx: MenuTickContext):
        """Update menu selection based on intent."""
        intent = ctx.intent
        if intent is None:
            return

        ctx.world.step_timer(ctx.dt)

        if not ctx.world.can_move():
            return

        if intent.move_up:
            ctx.menu.move_up()
            ctx.world.selected = ctx.menu.selected_index
            ctx.world.consume_move()
            return

        if intent.move_down:
            ctx.menu.move_down()
            ctx.world.selected = ctx.menu.selected_index
            ctx.world.consume_move()


@dataclass
class MenuActionSystem:
    """Menu action execution system."""

    name: str = "menu_actions"
    order: int = 30

    def step(self, ctx: MenuTickContext):
        """Execute actions based on menu intent."""
        intent = ctx.intent
        if intent is None:
            return

        if intent.select and ctx.menu.items:
            item = ctx.menu.items[ctx.menu.selected_index]
            ctx.commands.push(item.command_factory())

        if intent.quit and ctx.quit_cmd_factory is not None:
            cmd = ctx.quit_cmd_factory()
            if cmd is not None:
                ctx.commands.push(cmd)


@dataclass
class MenuRenderSystem(BaseQueuedRenderSystem[MenuTickContext]):
    """Menu rendering system."""

    name: str = "menu_render"
    merge_existing_draw_ops: bool = False

    def emit(self, ctx: MenuTickContext, rq):
        rq.custom(op=lambda backend: ctx.menu.draw(backend), layer="ui", z=100)


class BaseMenuScene(SimScene[MenuTickContext, MenuWorld]):
    """
    Base scene class for menu-based scenes.

    :ivar world (MenuWorld): The data model for the menu scene.
    """

    menu: Menu

    def on_enter(self):
        self.world = MenuWorld()
        self.menu = Menu(
            self._build_display_items(),
            viewport=self.menu_viewport(),
            title=self.menu_title,
            style=self.menu_style(),
        )
        self.menu.selected_index = self.world.selected
        self.systems.extend(
            [
                MenuInputSystem(),
                MenuNavigationSystem(),
                MenuActionSystem(),
                MenuRenderSystem(),
            ]
        )

    def _get_tick_context(
        self, input_frame: InputFrame, dt: float
    ) -> MenuTickContext:
        self.menu.set_viewport(self.menu_viewport())
        self.menu.set_items(self._build_display_items())
        self.menu.set_selected_index(self.world.selected)

        return MenuTickContext(
            input_frame=input_frame,
            dt=dt,
            world=self.world,
            commands=self.context.command_queue,
            menu=self.menu,
            quit_cmd_factory=self.quit_command,
        )

    @property
    def menu_title(self) -> str | None:
        """
        Get the title of the menu.

        :return: The menu title string, or None for no title.
        :rtype: str | None
        """
        return None

    def menu_style(self) -> MenuStyle:
        """
        Get the style configuration for the menu.

        :return: The MenuStyle instance for styling the menu.
        :rtype: MenuStyle
        """
        return MenuStyle()

    def menu_items(self) -> list[MenuItem]:
        """
        Get the list of menu items for the menu.

        :return: List of MenuItem instances for the menu.
        :rtype: list[MenuItem]
        """
        raise NotImplementedError

    def quit_command(self):
        """
        Get the command to execute when quitting the menu.

        :return: The command to execute on quit.
        :rtype: Command
        """
        # default behavior: quit game
        return QuitCommand()

    def menu_viewport(self) -> tuple[int, int]:
        """
        Get the viewport size for the menu.

        :return: The viewport size tuple (width, height).
        :rtype: tuple[int, int]
        """
        # default: virtual space (fits your UI layout)
        return self.context.services.window.get_virtual_size()

    def _build_display_items(self) -> list[MenuItem]:
        """
        Resolve dynamic labels (label_fn(ctx)) into the label field the Menu draws.
        Keeps command_factory intact.
        """
        src = self.menu_items()
        out: list[MenuItem] = []
        for it in src:
            out.append(
                MenuItem(
                    id=it.id,
                    label=it.resolved_label(self.context),
                    command_factory=it.command_factory,
                    label_fn=it.label_fn,
                )
            )
        return out
