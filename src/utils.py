from millify import millify


def print_with_banner(func):
    print("\033[H\033[J", end="")
    print(
        r"""
 ____  ___ ____   ____ ___    __  __    _    _   _    _    ____ _____ ____
|  _ \|_ _/ ___| / ___/ _ \  |  \/  |  / \  | \ | |  / \  / ___| ____|  _ \
| | | || |\___ \| |  | | | | | |\/| | / _ \ |  \| | / _ \| |  _|  _| | |_) |
| |_| || | ___) | |__| |_| | | |  | |/ ___ \| |\  |/ ___ \ |_| | |___|  _ <
|____/|___|____/ \____\___/  |_|  |_/_/   \_\_| \_/_/   \_\____|_____|_| \_\
"""
    )
    return func()


def format_views(views: str) -> str:
    num, _ = views.split()
    return f"{millify(int(num.replace(',', '')))}"
