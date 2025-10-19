from fasthtml.common import *
from monsterui.all import *
from datetime import datetime
import yaml, os

hdrs = Theme.violet.headers()

app, rt = fast_app(hdrs=hdrs, live=True)

## Article Pages
def ex_articles(meta, content):
    return Article(
        ArticleTitle(meta.title), 
        Subtitle("By: " + meta.author),
        render_md(content)
    )

## Main Page
def format_date(date):
    date_obj = datetime.fromisoformat(date)
    return date_obj.strftime("%B %d, %Y")

def get_post(fname):
    _, meta, post = open(fname).read().split('---\n')
    return dict2obj(yaml.safe_load(meta)), post

def _sorted_metas(post_metas):
    return sorted(post_metas, key=lambda p: p['date'], reverse=True)

def BlogCard(meta):
    image_path = meta.get('image', 'https://picsum.photos/300/150?random=13')
    im = Img(src=image_path, style="width=100px", cls='hidden md:block')
    return Card(
        DivLAligned(A(im, href=f"/{meta.slug}"),
            Div(H3(meta.title), 
            P(meta.description, cls=TextPresets.muted_sm),
            P(meta.author),
            DivLAligned(
                UkIcon("calendar", height=16),
                P(format_date(meta.date)),
                cls=(TextPresets.muted_sm, 'gap-2')),
            DivFullySpaced(DivLAligned(map(Label, meta.categories),
                           cls='gap-4 mt-2'),
            A(Button("Read More", cls=ButtonT.primary), href=f"/{meta.slug}")),
            cls='w-full')),
        cls=(CardT.hover, 'rounded-lg', 'space-x-4'))

@rt
def blog():
    post_metas = [get_post(f"posts/{o}")[0] for o in os.listdir("posts") if o.endswith(".md")]
    post_metas = _sorted_metas(post_metas)
    post_metas = [BlogCard(o) for o in post_metas]
    return Container(
        DivCentered(
            H2("My Blog"),
            P("Welcome to my blog!"),
            cls='space-y-2'
        ),
        Grid(*post_metas, cols_max=1, cls=('space-y-4', 'mt-4')),
        cls=(ContainerT.lg, 'space-y-8', 'mt-4'))

@rt
def about():
    return Container(
        H2("About Me"),
        P("This is a sample blog built with FastHTML and MonsterUI."),
        cls=(ContainerT.lg, 'space-y-4', 'mt-4'))

@rt
def index():
    return Container(
        H2("Welcome"),
        DivVStacked(
            A("Blog", href="/blog"),
            A("About", href="/about"),
            cls='gap-4'),
        cls=(ContainerT.lg, 'space-y-4', 'mt-4'))

@app.get('/{slug}')
def post(slug: str):
    meta, content = get_post('posts/' + slug +'.md')
    return Container(
        ex_articles(meta, content),
        cls=(ContainerT.lg, 'space-y-8', 'mt-4'))

serve()