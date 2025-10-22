from fastcore.utils import *
from fastlite import *
from datetime import datetime
import yaml, os, numpy as np
from google import genai

# os.environ['GEMINI_API_KEY'] = "AIzaSyAAEXri8NjAcyBZA8G2IrpCRUeEMcJt2C0"

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

db = database("main.db")
class topic_emb:
    id: int
    filename: str
    post_heading: str
    embedding: bytes
    last_modified: str

topic_emb = db.create(topic_emb, pk='id')

def get_emb(text, model='text-embedding-004'):
    # if not client: client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    response = client.models.embed_content(model=model, contents=text)
    return np.array(response.embeddings[0].values)

def load_posts_to_db():
    posts_dir = Path('../posts')
    for md_file in posts_dir.glob('*.md'):
        content = md_file.read_text()
        parts = content.split('---\n')
        meta = yaml.safe_load(parts[1])
        title = meta['title']
        # Check if title exists
        existing = topic_emb(where='post_heading = ?', where_args=[title])
        if existing:
            print(f"⊘ Skipped: {title} (already exists)")
            continue
        # Generate embedding
        embedding = get_emb(title)
        
        # Insert into database
        topic_emb.insert({
            'filename': str(md_file.name),
            'post_heading': title,
            'embedding': embedding.tobytes(),
            'last_modified': datetime.now().isoformat(sep=' ', timespec='seconds')
        })
        print(f"✓ Loaded: {title}")

load_posts_to_db()
