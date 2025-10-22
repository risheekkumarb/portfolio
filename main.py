from fasthtml.common import *
from monsterui.all import *
from datetime import datetime
import yaml, os, numpy as np
from google import genai

os.environ['GEMINI_API_KEY'] = "AIzaSyAAEXri8NjAcyBZA8G2IrpCRUeEMcJt2C0"

hdrs = Theme.violet.headers(mode='light', font='Roboto')

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
db = database("database/main.db")

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
    im = Img(src=image_path, cls='hidden md:block')
    return Card(
        DivLAligned(A(im, href=posts.to(fname=meta.slug)),
            Div(H3(meta.title), 
            P(meta.description, cls=TextPresets.muted_sm),
            P(meta.author),
            DivLAligned(
                UkIcon("calendar", height=16),
                P(format_date(meta.date)),
                cls=(TextPresets.muted_sm, 'gap-2')),
            DivFullySpaced(DivLAligned(map(Label, meta.categories),
                           cls='gap-4 mt-2'),
            A(Button("Read More", cls=ButtonT.primary), href=posts.to(fname=meta.slug))),
            cls='w-full')),
        cls=(CardT.hover, 'rounded-lg', 'space-x-4'))

def navbar(active_page):
    return NavBar(
        A("Home",href='/'),
        A("Blog",href=blog.to()),
        A("Work",href=work.to()),
        A("About",href=about.to()),
        brand=H3(active_page.capitalize()))

def get_emb(text, model='text-embedding-004'):
    response = client.models.embed_content(model=model, contents=text)
    return np.array(response.embeddings[0].values)

def cos_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@rt
def search(query: str):
    topic_emb = db.t.topic_emb
    q_emb = get_emb(query)
    results = []
    
    for row in topic_emb():
        stored_emb = np.frombuffer(row['embedding'])
        similarity = cos_sim(q_emb, stored_emb)
        results.append((row['filename'].replace(".md", ""), row['post_heading'], similarity))

    # Sort by similarity (highest first)
    results.sort(key=lambda x: x[2], reverse=True)  # Changed from x[1] to x[2]

    return Ul(*[Li(A(heading, cls=(TextPresets.muted_sm), style='color:blue;text-decoration:underline;', href=posts.to(fname=filename))) 
                for filename, heading, _ in results[:2]])

@rt
def blog():
    search_results_id = "search-results"
    
    search_form = Form(
        DivLAligned(
            Input(id='query', placeholder='Enter your search term...', 
                hx_get='/search', hx_target=f'#{search_results_id}', 
                hx_swap='innerHTML', hx_indicator='#search-spinner'),
            Loading(id='search-spinner', cls=(LoadingT.spinner, LoadingT.sm, 'htmx-indicator')),
            Button('Search', cls=(ButtonT.primary, ButtonT.sm)),
        ),
        Div(id=search_results_id), 
    )    
    post_metas = [get_post(f"posts/{o}")[0] for o in os.listdir("posts") if o.endswith(".md")]
    post_metas = _sorted_metas(post_metas)
    post_metas = [BlogCard(o) for o in post_metas]
    return Container(
        navbar('blog'),
        DivCentered(
            H4("Welcome to my blog!"),
            cls='space-y-2'
        ),
        search_form,
        Grid(*post_metas, cols_max=1, cls=('space-y-4', 'mt-4')),
        cls=(ContainerT.lg, 'space-y-8', 'mt-4'))

## Article Pages
def ex_articles(meta, content):
    return Article(
        ArticleTitle(meta.title), 
        Subtitle("By: " + meta.author),
        render_md(content),
        cls = 'mb-4'
    )

@rt
def posts(fname: str):
    meta, content = get_post('posts/' + fname + '.md')
    return Container(
        Div(navbar('Reading Blog'),
        Button('[ back ]', onclick='history.back()', cls=ButtonT.ghost, style='color: blue; text-decoration: underline;')),
        ex_articles(meta, content),
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
    if nav_items is None: nav_items = [('home', '#'), ('blog', blog.to()), ('work', work.to()), ('about', about.to())]
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
        # os.environ['GEMINI_API_KEY'],
        # Div('Some interting projects', cls=TextPresets.muted_sm),
        cls=(ContainerT.lg, 'space-y-6 mt-12'),
        style='max-width:400px')

serve()