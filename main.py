import warnings

import commands
import bar
import ingredients
from rich_console import console

warnings.filterwarnings("ignore", category=SyntaxWarning)

ingredients.load_ingredients_from_db()

bar_name = console.input("Name your bar: > ")
bar = bar.Bar(bar_name, 1000)

while True:
    bar.dashboard()

    prompt = "'Shop' or view the 'menu'"
    primary_cmd = None
    while primary_cmd is None:
        primary_cmd, args = commands.parse_input(prompt, commands.main_commands)
    bar.bar_cmd.onecmd(primary_cmd)


    def save_game(self, filename="save_game.json"):
        pass
