from rich import box
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bar_pkg.bar import Bar
from data.ingredients import list_ingredients, Ingredient, Drink
from display import live_display, rich_console
from display.rich_console import console
from interface import commands
from interface.commands import items_to_commands, command_to_item, input_loop
from utility import utils, logger, clock


def startup_screen():
    """Display and handle the initial screen when the game is started, showing title card and save files."""
    saves_table = Table(expand=True, box=box.SIMPLE, style=console.get_style("dimmed"), show_header=False)
    saves_table.add_column(justify="center")
    saves_table.add_row()

    screen_width, screen_height = console.size
    # Effective screen size due to panel borders
    screen_width -= 6
    screen_height -= 4

    max_saves_width = 50
    saves_width = max_saves_width if screen_width // 2 > max_saves_width else screen_width // 2
    title_width = screen_width - saves_width

    title_card = "~*~ Terminal Tavern ~*~"
    title_card_sizes = [(17, 70), (11, 47), (10, 42), (11, 20)]
    for size in title_card_sizes:
        height, width = size
        if screen_height >= height and title_width >= width:
            padding = ""
            for i in range((screen_height - height) // 2):
                padding += "\n"
            title_card = padding + rich_console.title_cards.get(f"{height}x{width}")
            title_width = width + 4
            break

    saves_panel = Panel(title="[tequila]Load Game", box=box.SQUARE_DOUBLE_HEAD, renderable=saves_table,
                        border_style=console.get_style("panel"))
    startup_layout = Layout(name="startup_layout")
    startup_layout["startup_layout"].split_row(Layout(name="info_layout", renderable=title_card, size=title_width),
                                               Layout(name="saves_layout", renderable=saves_panel))

    file_names = utils.list_saves()
    if len(file_names) > 0:
        for i, file_name in enumerate(file_names):
            saves_table.add_row(f"{i + 1}. {file_name[:-7]}")  # Removes .pickle
            saves_table.add_row()
    else:
        saves_table.add_row("[dimmed]No existing saves found")
        saves_table.add_row()
        saves_table.add_row("[dimmed]Enter 'new' to begin!")

    console.print(startup_layout)
    logger.log("Startup screen drawn.")

    prompt = "'Load \\[#]' or 'new'"
    startup_cmd, args = input_loop(prompt, ["new", "load"])
    if startup_cmd == "new":
        # Name input and checking handled by input loop
        new_bar = Bar(args[0])
        utils.save_bar(new_bar)
        utils.load_bar(utils.list_saves().index(f"{new_bar.bar_stats.bar_name}.pickle"))
    elif startup_cmd == "load":
        utils.load_bar(int(args[0]) - 1)


def dashboard(bar):
    """Display and handle the dashboard screen of the given bar, showing the menu and stats."""
    # <editor-fold desc="Layout"
    bar_name_panel = Panel(renderable=f"Welcome to [underline]{bar.bar_stats.bar_name}!")
    balance_panel = Panel(renderable=f"Balance: [money]${str(bar.bar_stats.balance)}[/money]  "
                                     f"Reputation: Lvl {bar.bar_stats.rep_level}")
    menu_panel = Panel(title="~*~ Menu ~*~", renderable="render failed",
                       border_style=console.get_style("bar_menu"))

    dash_layout = Layout(name="dash_layout")
    dash_layout.split_column(Layout(name="dash_header", size=3), Layout(name="dash"))
    dash_layout["dash_header"].split_row(Layout(name="bar_name", renderable=bar_name_panel),
                                         Layout(name="balance", renderable=balance_panel))

    menu_tables = bar.menu.table_menu(expanded=False)[0]
    if len(menu_tables) > 1:
        dash_layout["dash"].split_column(Layout(name="dash_body"),
                                         Layout(name="footer", size=1, renderable=live_display.live_prompt))
        dash_layout["dash_body"].split_row(Layout(name="menu_layout", renderable=menu_panel), Layout())

        live_display.live_cycle_tables(tables=menu_tables, panel=menu_panel, layout=dash_layout, sec=5)

    else:
        menu_panel.renderable = menu_tables[0]
        dash_layout["dash"].split_row(Layout(name="menu_layout", renderable=menu_panel),
                                      Layout())
        console.print(dash_layout)
        logger.log("Dashboard drawn.")
    # </editor-fold>

    prompt = "'Shop' or view the 'menu'"
    inpt = input_loop(prompt, ["shop", "menu", "open"], bar=bar)
    primary_cmd, args = inpt
    if primary_cmd == "shop":
        bar.set_screen("SHOP")
    elif primary_cmd == "menu":
        bar.set_screen("BAR_MENU")
    elif primary_cmd == "open":
        bar.set_screen("PLAY")


def menu_screen(bar):
    """Display and handle the bar menu screen, where menu items can be viewed, added, removed, and marked up."""
    prompt = "Category/item name, 'add \\[type]', 'remove \\[item]', 'markup \\[item]', 'markdown \\[item]', or go back"

    global type_displaying
    type_displaying = None

    bar.set_screen("BAR_MENU")
    while bar.get_screen() == "BAR_MENU":
        menu_tables, menu_list = bar.menu.table_menu(display_type=type_displaying, expanded=True)
        bar_menu_panel = Panel(title=f"~*~ {bar.bar_stats.bar_name} Menu ~*~", renderable="render failed",
                               border_style=console.get_style("bar_menu"))
        bar_menu_layout = Layout(name="bar_menu_layout", renderable=bar_menu_panel)

        if len(menu_tables) > 1:
            bar_menu_layout["bar_menu_layout"].split_column(Layout(name="menu", renderable=bar_menu_panel),
                                                            Layout(name="footer", size=1,
                                                                   renderable=live_display.live_prompt))
            live_display.live_cycle_tables(tables=menu_tables, panel=bar_menu_panel, layout=bar_menu_layout, sec=5)
        else:
            bar_menu_panel.renderable = menu_tables[0]
            console.print(bar_menu_layout)

        menu_commands = {"add", "remove", "markup", "markdown", "back", "menu"}
        # When viewing a section, don't add menu items as primary commands
        if type_displaying is None:
            logger.log("Bar menu screen drawn - viewing All")
            menu_commands = menu_commands.union(items_to_commands(menu_list, plural_types=True))
        else:
            menu_commands = menu_commands.union(
                items_to_commands(bar.menu.get_section(type_displaying()), plural_types=True))
            logger.log("Bar menu screen drawn - viewing " + type_displaying().format_type())

        typ = None if type_displaying is None else type_displaying
        primary_cmd, args = input_loop(prompt, menu_commands, ingredient=typ, bar=bar)

        if primary_cmd == "back":
            if type_displaying is None:  # At the full menu screen
                bar.set_screen("MAIN")
            else:  # Viewing beer menu, etc.
                type_displaying = None
        elif primary_cmd == "menu":
            bar.set_screen("MAIN")
        elif primary_cmd in ["add", "remove", "markup", "markdown"]:
            pass  # Handled by input loop
        elif primary_cmd in ["cocktails", "beers", "ciders", "wines", "meads"]:
            item = command_to_item(primary_cmd, menu_list, plural=True)
            type_displaying = item
        else:
            section = bar.menu.full_menu() if type_displaying is None else bar.menu.get_section(type_displaying())
            if primary_cmd in [menu_item.name.lower() for menu_item in section]:
                item = command_to_item(primary_cmd, menu_list)
                bar.menu.overview(item)
            else:
                console.print("[error]No allowed command recognized.")


def shop_screen(bar, current_selection: type or Ingredient = Ingredient, msg=None):
    """Opens the shop screen and executes an input loop.
    Sub-categories and ingredient items falling under the current selection are displayed and set as commands.
    The user can view and buy products in their available quantities.

        Args:
          :param bar: Active bar object.
          :param current_selection: The current category or product being displayed.
          :param msg: One-time specific prompt, such as confirming a successful purchase.
        """

    def shop_layout():
        panel_settings = {
            "renderable": "render failed",
            "box": box.DOUBLE_EDGE,
            "border_style": console.get_style("shop")
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

        global header_text
        header_table = Table(**table_settings)
        header_table.show_header = True

        header_table.add_column("Current balance:", justify="center", width=21)
        header_table.add_column("Viewing:", justify="center", width=console.width - 40)

        header_panel.renderable = header_table
        header_panel.renderable.justify = "center"

        return shop_layout, header_table, shop_panel, inv_panel

    def set_header():
        if current_selection == Ingredient:
            text = "[dimmed]All"
        else:  # Show pluralized category name in its proper style
            header_style = obj.get_style()
            if showing_flavored:
                text = Text(f"Flavored {obj.format_type(plural=True)}", style=header_style)
            else:
                text = Text(f"{obj.format_type(plural=True)}", style=header_style)
        return text

    def render_purchase_tables():
        inv_volume = 0
        inv_table = Table(box=None,
                          padding=(5, 0, 0, 0),
                          **table_settings)
        inv_table.add_column(justify="center")
        if current_selection in bar.stock.inventory:
            inv_volume = bar.stock.inventory.get(current_selection)
        inv_table.add_row(Text(f"{inv_volume}oz", style))
        vol_table = Table(
            **table_settings)
        vol_table.add_column("Volume", justify="center")
        vol_table.add_column("Price", justify="center")
        vol_table.add_column("Per oz", justify="center")
        vol_table.show_header = True

        for volume, price in current_selection.volumes.items():
            vol_table.add_row()  # Table's leading parameter breaks end_section. Add space between rows manually
            vol_table.add_row(f"[{style}]{volume}oz[/{style}]",
                              Text("${:.2f}".format(price), style=console.get_style("money")),
                              Text("${:.2f}".format(price / volume)), style=console.get_style("money"))
        shop_panel.renderable = vol_table
        inv_panel.renderable = inv_table

    def print_live_layout():
        layout["shop_screen"].split_column(Layout(name="footed_shop_screen"),
                                           Layout(name="footer", size=1,
                                                  renderable=live_display.live_prompt))
        layout["footed_shop_screen"].split_row(Layout(name="bar", renderable=inv_panel),
                                               Layout(name="shop", renderable=shop_panel))

        live_display.live_cycle_tables(tables=shop_tables, panel=shop_panel, layout=layout, sec=5)

    bar.set_screen("SHOP")
    showing_flavored = False

    while bar.get_screen() == "SHOP":

        global prompt
        table_settings = {
            "title_style": "underline",
            "show_header": False,
            "expand": True
        }
        layout, header_table, shop_panel, inv_panel = shop_layout()

        # <editor-fold desc="Populating shop panels">

        shop_commands = {"back", "shop"}
        shop_list = []

        # Type selected, not currently selecting an ingredient
        if isinstance(current_selection, type):
            if msg:
                prompt = msg
            else:
                prompt = "Type a category to view"

            obj = current_selection()
            header_text = set_header()
            table_settings["box"] = box.MARKDOWN

            shop_tables, shop_list = bar.stock.table_ing_category(table_settings, current_selection, showing_flavored,
                                                                  shop=True)
            inv_table, inv_list = bar.stock.table_ing_category(table_settings, current_selection, showing_flavored)
            inv_table = inv_table[0]

            items = list_ingredients(shop_list, current_selection, no_inheritance=True)
            if items:  # If there are ingredients in this category
                if not msg:
                    prompt = "Type a category or product to view"

            for command in items_to_commands(shop_list, plural_types=True):
                shop_commands.add(command)

            inv_panel.renderable = inv_table

        # Specific ingredient currently selected, show volumes
        elif isinstance(current_selection, Ingredient):
            shop_commands.add("buy")
            prompt = "Buy \\[volume], or go back"
            style = current_selection.get_style()
            header_text = current_selection.description()

            render_purchase_tables()

        else:
            console.print("[error]Current category is not category or ingredient")

        # 60 just appears to be the sweet spot here regardless of window size
        layout["shop_header"].size = 6 + utils.numb_lines(header_text, header_table.columns[1].width + 60)
        header_table.add_row(Text(f"${bar.bar_stats.balance}", console.get_style("money")), header_text)

        # </editor-fold>

        # Print layout
        if isinstance(current_selection, type):
            logger.log(f"Shop screen drawn; viewing {header_text}")
            if len(shop_tables) > 1:
                print_live_layout()
            else:
                shop_panel.renderable = shop_tables[0]
                console.print(layout)
        else:
            logger.log("Shop screen drawn; viewing " + current_selection.name)
            console.print(layout)

        # <editor-fold desc="Input">

        #  Don't do mid-word matches for Alcohol vs Non-Alcohol so "alco"+ doesn't return both commands
        force_beginning = True if current_selection == Drink else False

        primary_cmd, args = input_loop(prompt=prompt, commands=shop_commands, force_beginning=force_beginning,
                                       ingredient=current_selection, bar=bar, skip="shop")

        if msg:
            msg = None

        if primary_cmd == "buy":
            # Buy has been executed in input loop
            msg = (f"Bought {args[0]}oz of {current_selection.format_name()}. "
                   f"Current stock: {bar.stock.inventory[current_selection]}oz")
            logger.log(msg)
            shop_screen(bar=bar, current_selection=type(current_selection),
                        msg=msg)  # Go back from the ingredient screen
            return
        elif primary_cmd == "back":
            if current_selection == Ingredient:
                bar.set_screen("MAIN")
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
            if len(args) > 0:
                commands.check_shop(args=args, bar=bar, ingredient=None)
            else:
                bar.set_screen("MAIN")
                return
        elif primary_cmd == "flavored":
            showing_flavored = True
        elif command_to_item(cmd=primary_cmd, lst=shop_list, plural=True):
            current_selection = command_to_item(primary_cmd, shop_list, plural=True)
        else:
            console.print("[error]Command not handled")

        # </editor-fold>


def play_screen(bar, start_game_minutes):
    clock_panel = Panel(renderable="no clock")
    occupancy_panel = Panel(renderable=f"Customers: {len(bar.occupancy.current_customers())}",
                            border_style=console.get_style("customer"))
    balance_panel = Panel(renderable=f"Balance: [money]${"{:.2f}".format(bar.bar_stats.balance)}",
                          border_style=console.get_style("money"))
    log_panel = bar.occupancy.event_log_panel()
    customers_panel = Panel(title=f"Customers ({len(bar.occupancy.current_customers())})",
                            renderable=bar.occupancy.print_customers(), style=console.get_style("customer"))

    play_layout = Layout(name="play_layout")
    play_layout.split_column(Layout(name="top_bar", size=3),
                             Layout(name="body", renderable=log_panel))
    play_layout["top_bar"].split_row(Layout(name="clock", renderable=clock_panel),
                                     Layout(name="occupancy", renderable=occupancy_panel, size=17),
                                     Layout(name="balance", renderable=balance_panel, size=22))

    play_layout["body"].split_row(Layout(name="event_log", renderable=log_panel),
                                  Layout(name="right_side"))
    play_layout["right_side"].split_column(Layout(name="customers", renderable=customers_panel, size=8),
                                           Layout(name="customer_panel"))

    running = True
    while running:
        time_paused = clock.run_clock(bar=bar, start_game_mins=start_game_minutes, clock_panel=clock_panel,
                                      layout=play_layout)

        customer_names = [cstmr.name.lower() for cstmr in bar.occupancy.current_customers()]
        commands = customer_names

        primary_cmd, args = input_loop(prompt="Type a customer name for details", commands=commands)
        if primary_cmd in customer_names:
            bar.occupancy.customer_displayed = bar.occupancy.get_customer(primary_cmd)

        start_game_minutes = time_paused
