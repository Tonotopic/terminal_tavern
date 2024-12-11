import commands
import bar
import ingredients
from rich_console import console

ingredients.load_ingredients_from_db()

bar_name = console.input("Name your bar: > ")
bar = bar.Bar(bar_name, 1000)

while True:
    bar.dashboard()

    prompt = "Type 'shop' to shop: > "
    inpt_cmd = commands.find_command(console.input(prompt).strip().lower(), commands.main_commands)
    bar.bar_cmd.onecmd(inpt_cmd)


    def save_game(self, filename="save_game.json"):
        pass
