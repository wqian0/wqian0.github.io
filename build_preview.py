# Local preview builder: emulates the minimal-light Jekyll render so we can
# eyeball the page without a Ruby/Jekyll toolchain. GitHub Pages does the real build.
import re, yaml, markdown, pathlib

root = pathlib.Path(r"C:\Users\billy\Documents\claude\academic_page")
cfg = yaml.safe_load((root / "_config.yml").read_text(encoding="utf-8"))
pubs = yaml.safe_load((root / "_data" / "publications.yml").read_text(encoding="utf-8"))["main"]

def md(text):
    return markdown.markdown(text, extensions=["extra"])

def strip_front_matter(t):
    return re.sub(r"^---.*?---\s*", "", t, count=1, flags=re.S)

# --- index.md, splitting out the two include directives ---
index_raw = strip_front_matter((root / "index.md").read_text(encoding="utf-8"))
index_raw = index_raw.replace("{% include_relative _includes/publications.md %}", "@@PUBS@@")
index_raw = index_raw.replace("{% include_relative _includes/services.md %}", "@@SERVICES@@")

# --- publications block (mirrors _includes/publications.md liquid loop) ---
def pub_html(link):
    btns = []
    if link.get("pdf"):
        btns.append(f'<a href="{link["pdf"]}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">PDF</a>')
    if link.get("code"):
        btns.append(f'<a href="{link["code"]}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">Code</a>')
    if link.get("page"):
        btns.append(f'<a href="{link["page"]}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">Project Page</a>')
    if link.get("bibtex"):
        btns.append(f'<a href="{link["bibtex"]}" class="btn btn-sm z-depth-0" role="button" target="_blank" style="font-size:12px;">BibTex</a>')
    img = ""
    if link.get("image"):
        img = f'<img src="{link["image"]}" class="teaser img-fluid z-depth-1" style="width=100;height=40%">'
        if link.get("conference_short"):
            img += f'<abbr class="badge">{link["conference_short"]}</abbr>'
    return f'''<li><div class="pub-row">
  <div class="col-sm-3 abbr" style="position: relative;padding-right: 15px;padding-left: 15px;">{img}</div>
  <div class="col-sm-9" style="position: relative;padding-right: 15px;padding-left: 20px;">
      <div class="title"><a href="{link.get('pdf','#')}">{link['title']}</a></div>
      <div class="author">{link['authors']}</div>
      <div class="periodical"><em>{link['conference']}</em></div>
    <div class="links">{' '.join(btns)}</div>
  </div></div></li><br>'''

pubs_block = ('<h2 id="publications" style="margin: 2px 0px -15px;">Publications</h2>\n'
              '<div class="publications"><ol class="bibliography">'
              + "".join(pub_html(p) for p in pubs) + '</ol></div>')

services_block = md(strip_front_matter((root / "_includes" / "services.md").read_text(encoding="utf-8")))

content = md(index_raw).replace("@@PUBS@@", pubs_block).replace("@@SERVICES@@", services_block)

# --- inline the compiled theme CSS, stripping remote @import font lines
#     (they block the sandboxed preview renderer; real site loads them fine) ---
css_dir = root / "html_source_file" / "assets" / "css"
def load_css(name):
    lines = (css_dir / name).read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lines if "@import" not in l)
inline_css = load_css("style.css") + "\n" + load_css("publications.css")

# --- header (mirrors _layouts/homepage.html) ---
css_base = "./html_source_file/assets/css"
social = []
if cfg.get("google_scholar"):
    social.append(f'<a style="margin: 0 5px 0 0" href="{cfg["google_scholar"]}"><i class="ai ai-google-scholar" style="font-size:1.2rem"></i></a>')
if cfg.get("cv_link"):
    social.append(f'<a style="margin: 0 5px 0 0" href="{cfg["cv_link"]}"><i class="ai ai-cv" style="font-size:1.3rem;"></i></a>')
if cfg.get("github_link"):
    social.append(f'<a style="margin: 0 5px 0 0" href="{cfg["github_link"]}"><i class="fab fa-github"></i></a>')
if cfg.get("linkedin"):
    social.append(f'<a style="margin: 0 5px 0 0" href="{cfg["linkedin"]}"><i class="fab fa-linkedin"></i></a>')
if cfg.get("twitter"):
    social.append(f'<a style="margin: 0 0 0 0" href="{cfg["twitter"]}"><i class="fab fa-x-twitter"></i></a>')

html = f'''<!DOCTYPE html>
<html lang="en-US"><head>
<title>{cfg["title"]} | {cfg["affiliation"]}</title>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="{cfg['favicon']}" type="image/png" />
<style>{inline_css}</style>
</head><body><div class="wrapper">
<header>
<a class="image avatar"><img src="{cfg['avatar']}" alt="avatar" /></a>
<h1>{cfg['title']}</h1>
<position style="font-size:1.10rem;">{cfg['position']}</position><br>
<a href="{cfg.get('affiliation_link','')}" rel="noopener"><autocolor>{cfg['affiliation']}</autocolor></a><br>
<email>{cfg['email']}</email>
<br><br>
<div class="social-icons">{''.join(social)}</div>
<br></header>
<section>
{content}
<br>
<p><small>Powered by Jekyll and <a href="https://github.com/yaoyao-liu/minimal-light" target="_blank" rel="noopener">Minimal Light</a> theme.</small></p>
</section><footer></footer></div></body></html>'''

(root / "preview.html").write_text(html, encoding="utf-8")
print("Wrote preview.html")
