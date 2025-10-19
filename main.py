from fasthtml.common import *
from monsterui.all import *

hdrs = Theme.violet.headers()

app, rt = fast_app(hdrs=hdrs, live=True)

@rt
def index():
    posts = [open(f"posts/{o}").read() for o in os.listdir("posts")]
    return posts

serve()
