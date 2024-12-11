from rich.layout import Layout
from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import utils
from rich_console import console, Screen, styles
from commands import items_to_commands, input_loop, command_to_item
from ingredients import Ingredient, list_ingredients, Drink
from bar import Bar


def startup_screen():
    saves_table = Table(expand=True)
    saves_table.add_column("Saves", justify="center")

    header_panel = Panel(box=box.DOUBLE, height=3, renderable="Welcome to a game I still haven't named!")
    saves_panel = Panel(title="Load Game", box=box.SQUARE_DOUBLE_HEAD, renderable=saves_table)

    startup_layout = Layout(name="startup_layout")
    startup_layout.split_column(Layout(name="startup_header", renderable=header_panel, size=3),
                                Layout(name="startup_menu"))
    startup_layout["startup_menu"].split_row(Layout(name="info_layout"),
                                             Layout(name="saves_layout", renderable=saves_panel))

    file_names = utils.list_saves()
    if len(file_names) > 0:
        for i, file_name in enumerate(file_names):
            saves_table.add_row(f"{i + 1}. {file_name[:-7]}")  # Removes .pickle
    else:
        saves_table.add_row("[dimmed]No existing saves found")

    console.print(startup_layout)

    prompt = "'Load \\[num]' or 'new'"
    startup_cmd, args = input_loop(prompt, ["new", "load"])
    if startup_cmd == "new":
        # Name input and checking handled by input loop
        bar = Bar(args[0])
        utils.save_game(bar)
    elif startup_cmd == "load":
        bar = utils.load_game(int(args[0]) - 1)

    return bar


def dashboard(bar):
    # <editor-fold desc="Layout">

    bar_name_panel = Panel(renderable=f"Welcome to [underline]{bar.name}!")
    balance_panel = Panel(renderable=f"Balance: [money]${str(bar.balance)}")

    bar_layout = Layout(name="bar_layout")
    bar_layout.split_column(Layout(name="bar_header", size=3),
                            Layout(name="bar_body"))
    bar_layout["bar_header"].split_row(Layout(name="bar_name", renderable=bar_name_panel),
                                       Layout(name="balance", renderable=balance_panel))
    # </editor-fold>

    console.print(bar_layout)

    prompt = "'Shop' or view the 'menu'"
    primary_cmd, args = input_loop(prompt, ["shop", "menu"], bar=bar)
    if primary_cmd == "shop":
        bar.screen = Screen.SHOP
    elif primary_cmd == "menu":
        bar.screen = Screen.BAR_MENU


def shop_screen(bar, current_selection: type or Ingredient = Ingredient, msg=None):
    """Opens the shop screen and executes an input loop.
    Sub-categories and ingredient items falling under the current selection are displayed and set as commands.
    The user can view and buy products in their available quantities.

        Args:
          :param current_selection: The current category or product being displayed.
          :param msg: One-time specific prompt, such as confirming a successful purchase.
        """
    bar.screen = Screen.SHOP
    showing_flavored = False

    while bar.screen == Screen.SHOP:
        # <editor-fold desc="Layout">
        global prompt
        table_settings = {
            "title_style": "underline",
            "show_header": False,
            "expand": True
        }
        panel_settings = {
            "renderable": "render failed",
            "box": box.DOUBLE_EDGE,
            "border_style": styles.get("shop")
        }

        header_panel = Panel(**panel_settings, title=f"[money]Shop")
        shop_panel = Panel(**panel_settings, title=f"[money]Available for Purchase")
        inv_panel = Panel(**panel_settings, title=f"[panel]Bar Stock")

        shop_layout = Layout(name="shop_layout")
        shop_layout.split_column(
            Layout(name="shop_header", renderable=header_panel),  # Size is set later based on contents
            Layout(name="shop_screen")
        )
        shop_layout["shop_screen"].split_row(
            Layout(name="bar", renderable=inv_panel),
            Layout(name="shop", renderable=shop_panel)
        )

        # </editor-fold>

        # <editor-fold desc="Header">
        global header_text
        header_table = Table(**table_settings)
        header_table.show_header = True

        header_table.add_column("Current balance:", justify="center", width=21)
        header_table.add_column("Viewing:", justify="center", width=console.width - 40)

        header_panel.renderable = header_table
        header_panel.renderable.justify = "center"
        # </editor-fold>

        # <editor-fold desc="Populating shop panels">

        shop_commands = {"back", "shop", "buy"}

        # TODO: Sort shop list display
        shop_list = []

        # Type selected, not currently selecting an ingredient
        if isinstance(current_selection, type):
            if msg:
                prompt = msg
            else:
                prompt = "Type a category to view"

            obj = current_selection()

            # Header
            if current_selection == Ingredient:
                header_text = "[dimmed]All"
            else:  # Show pluralized category name in its proper style
                style = styles.get(obj.get_ing_style())
                if showing_flavored:
                    header_text = Text(f"Flavored {obj.format_type()}s", style=style)
                else:
                    header_text = Text(f"{obj.format_type()}s", style=style)

            table_settings["box"] = box.MARKDOWN

            shop_tables, shop_list = bar.stock.show_stock(table_settings, current_selection, showing_flavored,
                                                          shop=True)
            inv_table, inv_list = bar.stock.show_stock(table_settings, current_selection, showing_flavored)
            overflow_table = Table(**table_settings)
            overflow_2 = Table(**table_settings)

            # If there are overflow tables
            if isinstance(shop_tables, tuple):
                shop_table = shop_tables[0]
                shop_table.columns[0].footer = "continued..."
                overflow_table = shop_tables[1]
                if len(shop_tables) == 3:
                    overflow_2 = shop_tables[2]

            else:
                shop_table = shop_tables

            items = list_ingredients(shop_list, current_selection, type_specific=True)
            if items:  # If there are ingredients in this category
                if not msg:
                    prompt = "Type a category or product to view"

            shop_panel.renderable = shop_table
            inv_panel.renderable = inv_table

            for command in items_to_commands(shop_list):
                shop_commands.add(command)

        # Specific ingredient currently selected, show volumes
        elif isinstance(current_selection, Ingredient):
            shop_commands.add("buy")
            prompt = "Buy \\[volume], or go back"
            obj = current_selection
            style = obj.get_ing_style()
            header_text = obj.description()

            # <editor-fold desc="inv_table">
            inv_volume = 0
            inv_table = Table(box=None,
                              padding=(5, 0, 0, 0),
                              **table_settings)
            inv_table.add_column(justify="center")
            if obj in bar.stock.inventory:
                inv_volume = bar.stock.inventory.get(obj)
            inv_table.add_row(Text(f"{inv_volume}oz", style))
            # </editor-fold>

            # <editor-fold desc="vol_table">
            vol_table = Table(
                **table_settings)
            vol_table.add_column("Volume", justify="center")
            vol_table.add_column("Price", justify="center")
            vol_table.show_header = True

            for volume, price in obj.volumes.items():
                vol_table.add_row()  # Table's leading parameter breaks end_section. Add space between rows manually
                vol_table.add_row(f"[{style}]{volume}oz[/{style}]",
                                  Text("${:.2f}".format(price), style=styles.get("money")))
            # </editor-fold>
            shop_panel.renderable = vol_table
            inv_panel.renderable = inv_table
        else:
            console.print("[error]Current category is not category or ingredient")

        # 60 just appears to be the sweet spot here regardless of window size
        shop_layout["shop_header"].size = 8 if len(header_text) > header_table.columns[1].width + 60 else 7
        header_table.add_row(Text(f"${bar.balance}", styles.get("money")), header_text)

        # </editor-fold>

        console.print(shop_layout)

        if len(overflow_table.rows) != 0:
            console.input("Press 'enter' to continue to next page...")
            shop_panel.renderable = overflow_table
            console.print(shop_layout)
            if len(overflow_2.rows) != 0:
                console.input("Press 'enter' to continue to next page...")
                shop_panel.renderable = overflow_2
                console.print(shop_layout)

        # <editor-fold desc="Input">

        #  Don't do mid-word matches for Alcohol vs Non-Alcohol so "alco"+ doesn't return both commands
        force_beginning = True if current_selection == Drink else False

        primary_cmd, args = input_loop(prompt, shop_commands, force_beginning, current_selection, bar=bar)

        if primary_cmd == "buy":
            # Buy has been executed in input loop
            msg = (f"Bought {args[0]}oz of [{style}]{current_selection.name}[/{style}]. "
                   f"Current stock: {bar.stock.inventory[current_selection]}oz")
            shop_screen(bar=bar, current_selection=type(current_selection), msg=msg)  # Go back from the ingredient screen
            return
        elif primary_cmd == "back":
            if current_selection == Ingredient:
                bar.screen = Screen.MAIN
                return
            elif isinstance(current_selection, Ingredient):  # Ingredient selected, go back to category
                current_selection = type(current_selection)
            elif isinstance(current_selection, type):
                if showing_flavored:
                    showing_flavored = False
                else:
                    current_selection = current_selection.__base__  # Back to last category
            else:
                console.print("current_category is not category or ingredient")
        elif primary_cmd == "shop":  # exit the shop
            bar.screen = Screen.MAIN
            return
        elif primary_cmd == "flavored":
            showing_flavored = True
        elif command_to_item(primary_cmd, shop_list):
            current_selection = command_to_item(primary_cmd, shop_list)
        else:
            console.print("[error]Command not handled")

        # </editor-fold>


def menu_screen(bar):
    bar.screen = Screen.BAR_MENU
    global type_displaying
    type_displaying = None
    prompt = "'Back' to go back"

    while bar.screen == Screen.BAR_MENU:
        menu_table, menu_list = bar.menu.table_menu(display_type=type_displaying, expanded=True)
        bar_menu_panel = Panel(title=f"{bar.name} Menu", renderable=menu_table,
                               border_style=styles.get("bar_menu"))
        bar_menu_layout = Layout(name="bar_menu_layout", renderable=bar_menu_panel)

        console.print(bar_menu_layout)

        menu_commands = set()
        # When viewing a section, don't add menu items as primary commands
        if type_displaying is None:
            menu_commands = items_to_commands(menu_list)  # Categories
        menu_commands.add("add")
        menu_commands.add("remove")
        menu_commands.add("markup")
        menu_commands.add("markdown")
        menu_commands.add("back")
        menu_commands.add("menu")

        typ = None if type_displaying is None else type_displaying
        primary_cmd, args = input_loop(prompt, menu_commands, ingredient=typ, bar=bar)

        if primary_cmd == "back":
            if type_displaying is None:  # At the full menu screen
                bar.screen = Screen.MAIN
            else:  # Viewing beer menu, etc.
                type_displaying = None
        elif primary_cmd == "menu":
            bar.screen = Screen.MAIN
        elif primary_cmd == "add":
            # Add handled by input loop
            continue
        elif primary_cmd == "remove":
            bar.remove(args[0])
        elif primary_cmd == "markup":
            bar.markup(args[0])
        elif primary_cmd == "markdown":
            bar.markdown(args[0])
        elif primary_cmd in menu_commands:  # beer, cider, wine, etc.
            type_displaying = command_to_item(primary_cmd, menu_list)
        else:
            console.print("[error]No allowed command recognized.")
