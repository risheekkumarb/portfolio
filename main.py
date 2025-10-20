from fasthtml.common import *
from monsterui.all import *
from datetime import datetime
import yaml, os

hdrs = Theme.violet.headers(mode='light', font='Inter')

app, rt = fast_app(hdrs=hdrs, live=True)

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

def navbar(active_page):
    return NavBar(A("Home",href='/'),
                  A("Blog",href='/blog'),
                  A("Work",href='/work'),
                  A("About",href='/about'),
                  brand=H3(active_page.capitalize()))

@rt
def blog():
    post_metas = [get_post(f"posts/{o}")[0] for o in os.listdir("posts") if o.endswith(".md")]
    post_metas = _sorted_metas(post_metas)
    post_metas = [BlogCard(o) for o in post_metas]
    return Container(
        navbar('blog'), 
        DivCentered(
            H4("Welcome to my blog!"),
            cls='space-y-2'
        ),
        Grid(*post_metas, cols_max=1, cls=('space-y-4', 'mt-4')),
        cls=(ContainerT.lg, 'space-y-8', 'mt-4'))

@rt
def about():
    return Container(
        navbar('about'),
        render_md(open('public/risheek_about.md').read()),
        cls=(ContainerT.lg, 'space-y-4', 'mt-4'))

@rt
def work():
    return Container(
        navbar('work'),
        H2("My Work"),
        P("Some of my work will be listed here."),
        cls=(ContainerT.lg, 'space-y-4', 'mt-4'))

def NavButton(text, href='#'):
    return Div(
        '[ ',
        A(Strong(text, style='color: blue; text-decoration: underline;'), href=href),
        ' ]')

def SocialLink(icon, href):
    return A(DivHStacked(UkIcon(icon, height=16), Strong(icon)), href=href)

def ProfilePage(img_src, img_alt='profile image', nav_items=None):
    if nav_items is None: nav_items = [('home', '#'), ('blog', '/blog'), ('work', '/work'), ('about', '/about')]
    return Div(
        DivFullySpaced(
            Img(src=img_src, alt=img_alt, style='width:200px; height:200px; object-fit:cover'),
            Div(*[NavButton(text, href) for text, href in nav_items], cls='space-y-4'),
            cls='gap-8 flex-col md:flex-row items-center justify-center'))

@rt
def index():
    social = [
    ('linkedin', 'https://www.linkedin.com/in/risheekkumar-baskaran-748115120/'),
    ('twitter', 'https://x.com/BRisheek'),
    ('github', 'https://github.com/risheekkumarb')]
    social_links = [SocialLink(icon, href) for icon, href in social]
    profile = ProfilePage('public/risheek_image.png')
    return Container(
        Div(
            H2('Risheek kumar B'),
            H3('full stack machine learning'),
            Divider(cls='border-t-2 mt-2')),
        profile,
        Divider(cls='border-t-2'),
        DivHStacked(*social_links, cls='justify-center gap-6 mt-4'),
        cls=(ContainerT.lg, 'space-y-6 mt-12'),
        style='max-width:400px')

## Article Pages
def ex_articles(meta, content):
    return Article(
        ArticleTitle(meta.title), 
        Subtitle("By: " + meta.author),
        render_md(content),
        cls = 'mb-4'
    )

@app.get('/{slug}')
def post(slug: str):
    meta, content = get_post('posts/' + slug +'.md')
    return Container(
        Div(navbar('Reading Blog'),
        Button('[ back ]', onclick='history.back()', cls=ButtonT.ghost, style='color: blue; text-decoration: underline;')),
        ex_articles(meta, content),
        cls=(ContainerT.lg, 'space-y-8', 'mt-4'))

serve()