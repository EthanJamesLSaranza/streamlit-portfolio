"""
Ethan James L. Saranza | Autobiography & Portfolio
CSIT 349 · Section G01

Run with:  python -m streamlit run app.py
Keep me.jpg and the .streamlit/config.toml folder next to this file.
"""

import base64
import csv
import io
import mimetypes
import time
from datetime import datetime
from html import escape as esc
from pathlib import Path

import streamlit as st

try:  # pandas powers the chart and table; the rest of the app works without it
    import pandas as pd

    # A blocked install can import without raising, so confirm the real API exists.
    HAS_PANDAS = hasattr(pd, "DataFrame")
except Exception:
    pd = None
    HAS_PANDAS = False

st.set_page_config(
    page_title="Ethan James L. Saranza | Portfolio",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CONFIG: all of your content lives here
# ============================================================
NAME = "Ethan James L. Saranza"
FIRST = "Ethan James"
LAST = "L. Saranza"
INITIALS = "ES"
PROGRAM = "BS Information Technology · 4th Year"
SCHOOL = "Cebu Institute of Technology - University"
SCHOOL_SHORT = "CIT-U"
SECTION = "CSIT 349 · Section G01"
TAGLINE = "Using technology to improve and innovate lives."
EMAIL = "ethansaranza17@gmail.com"

# Paste your profile links between the quotes. Empty links stay hidden.
FACEBOOK_URL = "https://www.facebook.com/ethan.saranza.9/"
INSTAGRAM_URL = "https://www.instagram.com/eth_6n/"
GITHUB_URL = "https://github.com/EthanJamesLSaranza"

BIO = (
    "I'm from Cebu City and I am a 4th year BSIT student currently studying at CIT-U. "
    "I chose IT because of my love for technology and the ways it can improve and innovate lives."
)

CAREER_INTERESTS = ["Cybersecurity", "Network engineering", "IT support", "Web development"]
HOBBIES = ["Gym & working out", "Basketball", "Pickleball", "Video games", "Movies & TV series"]

# (certificate, earned?)  Use False for a certificate you are still working on.
CERTS = [
    ("AWS Cloud Foundations", True),
    ("TryHackMe Cybersecurity Fundamentals", True),
    ("SoloLearn Intro to HTML", True),
]

FAQ = {
    "Where are you from?": (
        "I was born and raised here in Cebu City. I had a fairly normal childhood, "
        "and my family is caring and compassionate."
    ),
    "Why IT?": (
        "I chose IT because of my love for technology and the ways it can improve "
        "and innovate lives."
    ),
    "Where did you study?": (
        "Elementary to junior high at St. Thomas Aquinas Montessori School in Bulacao, "
        "then senior high (STEM) at Asian College of Technology in Bulacao. "
        "Now I'm a 4th year BSIT student at CIT-U."
    ),
    "What do you do for fun?": (
        "I love to work out and hit the gym, play basketball and pickleball, "
        "play video games, and watch movies or TV series."
    ),
    "What are you into right now?": (
        "I'm very intrigued by cybersecurity and would love to further my knowledge "
        "about it. I also earned my AWS Cloud Foundations certificate."
    ),
}

# (icon, title, text)
MILESTONES = [
    ("🎙️", "Senior high: STEM, debate, and student council",
     "I took STEM at Asian College of Technology, joined the debate club, and served as "
     "secretary to the Internal Vice President of the student council."),
    ("🌱", "Starting BSIT from zero",
     "In my first year of BSIT I had basically zero coding experience, so I had to learn everything from scratch."),
    ("🖥️", "My first web page",
     "My first web page was an introduction all about myself."),
    ("🔐", "Falling for cybersecurity",
     "I'm very intrigued by cybersecurity and would love to further my knowledge about it."),
    ("🛒", "Working at a hobby shop",
     "I worked part-time at a hobby shop in Kinasang-an. It improved my Excel skills and my sales talk."),
    ("🚌", "Building ByahengCebu",
     "For my Systems Integration class I built ByahengCebu, an app that helps co-ops manage and track drivers and white buses."),
    ("☁️", "Earning the AWS certificate",
     "I earned the AWS Cloud Foundations certificate."),
]

# (skill, level 0-100, category)
SKILLS = [
    ("HTML & CSS", 87, "Web"),
    ("React & Tailwind", 85, "Web"),
    ("Python", 83, "Programming"),
    ("Networking", 82, "IT"),
    ("Cybersecurity basics", 85, "IT"),
    ("Cloud (AWS basics)", 89, "IT"),
    ("Communication", 95, "Soft"),
    ("Teamwork", 90, "Soft"),
]
CATEGORY_LABELS = {"Soft": "Soft skills", "IT": "IT & Security"}

PROJECTS = [
    {
        "title": "ByahengCebu",
        "summary": (
            "A transport management system I built for my Systems Integration class. "
            "It helps cooperatives manage and track their drivers and white buses."
        ),
        "role": "Full-stack developer",
        "tools": ["Spring Boot", "React", "Supabase"],
        "outcome": "Built end to end, frontend and backend, for Systems Integration.",
        "link": None,
    },
    {
        "title": "CSIT340 Portfolio Lab",
        "summary": (
            "A personal portfolio website built in React and styled with Tailwind CSS, "
            "organized into 15 reusable components."
        ),
        "role": "Developer",
        "tools": ["React", "Tailwind CSS"],
        "outcome": "Submitted as Lab 2 for CSIT340.",
        "link": "https://github.com/EthanJamesLSaranza/CSIT340-Lab2-Saranza",
    },
    {
        "title": "Autobiography & Portfolio App",
        "summary": (
            "The site you're looking at: a Streamlit app with a profile sidebar, animated "
            "sections, skill charts, an interactive Q&A, and a contact form, all written in Python."
        ),
        "role": "Designer & developer",
        "tools": ["Python", "Streamlit", "CSS"],
        "outcome": "Built for CSIT 349 (Applied AI).",
        "link": None,
    },
]

MOODS = {  # name: (accent, accent 2, soft tint)
    "Olive grove": ("#6B7040", "#E3B04B", "#DFE2BC"),
    "Golden hour": ("#A8650F", "#6B7040", "#F4E0B2"),
    "Window sky": ("#3F73A5", "#E3B04B", "#D6E6F4"),
}

REACTIONS = [
    "Ouch. I'll keep working on it.",
    "Noted, I'll keep improving.",
    "Fair enough!",
    "Glad you liked it!",
    "That made my day!",
]

SOCIALS = [("Facebook", FACEBOOK_URL), ("Instagram", INSTAGRAM_URL), ("GitHub", GITHUB_URL)]
ACTIVE_SOCIALS = [(label, url) for label, url in SOCIALS if url]


# ============================================================
# HELPERS
# ============================================================
def render(markup: str):
    """Send HTML to the page. Lines are joined so Markdown never treats them as code."""
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def chips(items, cls="chip"):
    return "".join(f'<span class="{cls}">{esc(i)}</span>' for i in items)


APP_DIR = Path(__file__).parent
PHOTO_PATH = next(
    (p for p in (APP_DIR / f"me.{ext}" for ext in ("jpg", "jpeg", "png", "webp")) if p.exists()),
    None,
)


@st.cache_data(show_spinner=False)
def photo_uri(path: str, mtime: float) -> str:
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


PHOTO = photo_uri(str(PHOTO_PATH), PHOTO_PATH.stat().st_mtime) if PHOTO_PATH else None


def photo_html(cls="arch"):
    if PHOTO:
        return f'<div class="{cls}"><img src="{PHOTO}" alt="{esc(NAME)}"></div>'
    return f'<div class="{cls}"><span class="initials">{INITIALS}</span></div>'


def story_markdown() -> str:
    lines = [f"# {NAME}", f"*{PROGRAM} · {SCHOOL}*", "", f"> {TAGLINE}", "", BIO, ""]
    lines.append("## Questions")
    for q, a in FAQ.items():
        lines += [f"**{q}**", a, ""]
    lines.append("## Milestones")
    for _, title, text in MILESTONES:
        lines.append(f"- **{title}.** {text}")
    lines += ["", "## Skills"]
    lines += [f"- {n}: {lvl}/100 ({c})" for n, lvl, c in SKILLS]
    lines += ["", "## Projects"]
    for p in PROJECTS:
        lines.append(f"- **{p['title']}** ({p['role']}; {', '.join(p['tools'])}). {p['summary']} {p['outcome']}")
    lines += ["", f"Contact: {EMAIL}"]
    return "\n".join(lines)


def messages_csv() -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["name", "email", "reply_via", "topic", "rating", "interests", "message"]
    )
    writer.writeheader()
    writer.writerows(st.session_state.messages)
    return buf.getvalue().encode("utf-8")


def type_out(text: str):
    """Typewriter effect without st.write_stream, which needs pandas."""
    slot = st.empty()
    shown = ""
    for word in text.split(" "):
        shown += word + " "
        slot.markdown(shown)
        time.sleep(0.03)


# ---------- session state ----------
for key, default in {"messages": [], "hellos": 0, "welcomed": False, "last_q": None}.items():
    st.session_state.setdefault(key, default)

# ============================================================
# SIDEBAR: profile card and settings
# ============================================================
with st.sidebar:
    render(
        f"""
        <div class="side-card">
          {photo_html("arch round")}
          <div class="side-name">{esc(NAME)}</div>
          <div class="side-meta">{esc(PROGRAM)}</div>
          <div class="side-meta">{esc(SECTION)}</div>
        </div>
        """
    )
    st.caption("MAKE IT YOURS")
    mood = st.selectbox("🎨 Mood", list(MOODS), help="Swaps the accent colors of the whole site.")
    animate = st.toggle("✨ Animations", value=True)
    show_certs = st.toggle("🎓 Show certificates", value=True)
    st.divider()
    for label, url in ACTIVE_SOCIALS:
        st.link_button(label, url, width="stretch")
    st.download_button(
        "⬇️ Download my story (.md)",
        data=story_markdown(),
        file_name="ethan_saranza_story.md",
        mime="text/markdown",
        width="stretch",
    )

ACCENT, ACCENT2, SOFT = MOODS[mood]

# ============================================================
# STYLES
# ============================================================
render(
    f"""<style>:root {{ --accent: {ACCENT}; --accent2: {ACCENT2}; --soft: {SOFT}; }}</style>"""
)

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=DM+Sans:wght@400;500;700&display=swap');
:root{--cream:#F3ECD9;--paper:#FBF7EC;--ink:#26211B;--serif:'Fraunces',Georgia,'Times New Roman',serif;--sans:'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
html,body,.stApp,button,input,textarea{font-family:var(--sans);}
.stApp{color:var(--ink);background-color:var(--cream);background-image:radial-gradient(rgba(38,33,27,.09) 1px,transparent 1px),radial-gradient(circle at 88% -8%,var(--soft),transparent 46%);background-size:22px 22px,100% 100%;}
[data-testid="stHeader"]{background:transparent;}
footer{visibility:hidden;}
.block-container{max-width:1180px;padding-top:2.4rem;padding-bottom:3rem;}
h1,h2,h3,h4{font-family:var(--serif)!important;letter-spacing:-.01em;color:var(--ink);}

@keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}
@keyframes float{0%,100%{transform:translateY(0) rotate(var(--r,0deg))}50%{transform:translateY(-10px) rotate(var(--r,0deg))}}
@keyframes morph{0%,100%{border-radius:42% 58% 55% 45%/48% 42% 58% 52%}50%{border-radius:58% 42% 40% 60%/55% 58% 42% 45%}}
@keyframes underline{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes scroll{to{transform:translateX(-50%)}}

[data-testid="stSidebar"]{background:var(--paper);border-right:2px solid var(--ink);}
.side-card{text-align:center;padding:.6rem 0 1rem;}
.side-name{font-family:var(--serif);font-weight:800;font-size:1.35rem;line-height:1.15;margin-top:.9rem;}
.side-meta{font-size:.85rem;opacity:.75;margin-top:.2rem;}

.arch{position:relative;width:100%;aspect-ratio:4/5;border-radius:999px 999px 28px 28px;overflow:hidden;border:2px solid var(--ink);background:var(--soft);box-shadow:8px 8px 0 var(--ink);display:flex;align-items:center;justify-content:center;}
.arch img{width:100%;height:100%;object-fit:cover;object-position:50% 40%;}
.arch.round{width:150px;aspect-ratio:1;margin:0 auto;border-radius:50%;box-shadow:4px 4px 0 var(--ink);}
.initials{font-family:var(--serif);font-size:3.4rem;font-weight:800;color:var(--accent);}

.hero{display:grid;grid-template-columns:1.25fr 1fr;gap:3rem;align-items:center;margin:.4rem 0 1.6rem;padding:0 1.6rem;}
.eyebrow{display:inline-block;font-weight:700;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:.38rem .9rem;border-radius:999px;animation:rise .7s ease both;}
.display{font-family:var(--serif);font-weight:800;font-size:clamp(2.6rem,6vw,4.7rem);line-height:.98;letter-spacing:-.03em;margin:1.1rem 0 .7rem;animation:rise .8s .1s ease both;}
.display .hl{position:relative;display:inline-block;z-index:0;color:var(--accent);}
.display .hl::after{content:"";position:absolute;left:0;bottom:.05em;width:100%;height:.22em;background:var(--accent2);z-index:-1;border-radius:4px;transform-origin:left;animation:underline 1s .6s ease both;}
.lead{font-size:1.28rem;font-weight:700;margin:.2rem 0 .8rem;animation:rise .8s .2s ease both;}
.sub{max-width:34rem;line-height:1.7;opacity:.88;animation:rise .8s .3s ease both;}
.chips{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.1rem;animation:rise .8s .4s ease both;}
.chip{display:inline-block;border:2px solid var(--ink);border-radius:999px;padding:.28rem .85rem;font-size:.85rem;font-weight:700;background:var(--paper);margin:.15rem .2rem .15rem 0;}
.chip.fill{background:var(--accent);color:var(--paper);}
.hero-photo{position:relative;width:100%;max-width:380px;margin:0 auto;animation:rise .9s .15s ease both;}
.blob{position:absolute;inset:-7% -12% -5% 12%;background:var(--accent2);opacity:.6;border-radius:42% 58% 55% 45%/48% 42% 58% 52%;z-index:0;animation:morph 9s ease-in-out infinite;}
.hero-photo .arch{z-index:1;}
.sticker{position:absolute;z-index:2;background:var(--paper);border:2px solid var(--ink);border-radius:14px;padding:.4rem .8rem;font-weight:700;font-size:.85rem;box-shadow:4px 4px 0 var(--ink);animation:float 5s ease-in-out infinite;transform:rotate(var(--r,0deg));}
.s1{top:9%;left:-16%;--r:-6deg;}
.s2{bottom:17%;right:-14%;--r:5deg;animation-delay:-1.6s;}
.s3{bottom:-3%;left:2%;--r:-3deg;animation-delay:-3.2s;}

.marquee{overflow:hidden;border-block:2px solid var(--ink);background:var(--accent);color:var(--paper);margin:1.6rem -1rem 2rem;transform:rotate(-1.2deg);}
.track{display:flex;width:max-content;animation:scroll 34s linear infinite;}
.track span{padding:.72rem 1.4rem;font-family:var(--serif);font-weight:700;font-size:1.15rem;white-space:nowrap;}

.card{background:var(--paper);border:2px solid var(--ink);border-radius:20px;padding:1.3rem 1.45rem;margin-bottom:1.2rem;box-shadow:6px 6px 0 var(--ink);transition:transform .2s ease,box-shadow .2s ease;animation:rise .6s ease both;}
.card:hover{transform:translate(-3px,-3px);box-shadow:9px 9px 0 var(--ink);}
.card h3{margin:.25rem 0 .3rem;font-size:1.5rem;}
.card p{margin:.4rem 0;line-height:1.6;}
.card .num{font-family:var(--serif);font-size:.85rem;font-weight:800;letter-spacing:.1em;color:var(--accent);}
.card .role{opacity:.72;font-weight:500;}
.card .outcome{font-weight:700;color:var(--accent);margin-top:.7rem;}
.tag{display:inline-block;margin:.15rem .3rem .15rem 0;padding:.15rem .65rem;border:1.5px solid var(--ink);border-radius:8px;font-size:.78rem;font-weight:700;background:var(--soft);}

[data-testid="stMetric"]{background:var(--paper);border:2px solid var(--ink);border-radius:18px;padding:1rem 1.2rem;box-shadow:5px 5px 0 var(--ink);}
[data-testid="stMetricValue"]{font-family:var(--serif);font-weight:800;color:var(--accent);}
[data-testid="stMetricLabel"] p{font-weight:700;}

[data-baseweb="tab-list"]{gap:.55rem;margin-bottom:1rem;}
button[data-baseweb="tab"]{border:2px solid var(--ink)!important;border-radius:999px!important;padding:.4rem 1.2rem!important;background:var(--paper)!important;height:auto!important;}
button[data-baseweb="tab"] p{font-weight:700;font-size:1rem;}
button[data-baseweb="tab"][aria-selected="true"]{background:var(--accent)!important;}
button[data-baseweb="tab"][aria-selected="true"] p{color:var(--paper)!important;}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important;}

[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stBaseButton-primaryFormSubmit"],[data-testid="stBaseLinkButton-secondary"],[data-testid="stBaseLinkButton-primary"]{border:2px solid var(--ink)!important;border-radius:999px!important;font-weight:700!important;box-shadow:3px 3px 0 var(--ink);transition:transform .15s ease,box-shadow .15s ease;}
[data-testid="stBaseButton-secondary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseLinkButton-secondary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{transform:translate(-1px,-1px);box-shadow:5px 5px 0 var(--ink);}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--accent)!important;color:var(--paper)!important;}
[data-testid="stForm"]{background:var(--paper);border:2px solid var(--ink);border-radius:20px;box-shadow:6px 6px 0 var(--ink);padding:1.3rem;}
[data-testid="stChatMessage"]{background:var(--paper);border:2px solid var(--ink);border-radius:18px;box-shadow:4px 4px 0 var(--ink);}

.skill{margin:.6rem 0;}
.skill .top{display:flex;justify-content:space-between;font-weight:700;font-size:.95rem;margin-bottom:.25rem;}
.skill .bar{height:15px;border:2px solid var(--ink);border-radius:999px;background:var(--paper);overflow:hidden;}
.skill .fill{height:100%;width:calc(var(--v)*1%);background:repeating-linear-gradient(45deg,rgba(255,255,255,.22) 0 8px,transparent 8px 16px),var(--accent);transform-origin:left;animation:grow 1.1s var(--d,0s) cubic-bezier(.2,.8,.2,1) both;}
.rings{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:1.1rem;}
.ring{display:flex;flex-direction:column;align-items:center;gap:.55rem;text-align:center;animation:rise .6s var(--d,0s) ease both;}
.dial{width:108px;height:108px;border-radius:50%;border:2px solid var(--ink);background:conic-gradient(var(--accent) calc(var(--v)*1%),rgba(38,33,27,.12) 0);display:grid;place-items:center;}
.dial b{width:78px;height:78px;border-radius:50%;border:2px solid var(--ink);background:var(--paper);display:grid;place-items:center;font-family:var(--serif);font-size:1.45rem;}
.ring small{font-weight:700;}

.timeline{position:relative;margin:.6rem 0 0 1.4rem;padding-left:2rem;border-left:3px dashed var(--ink);}
.tl-item{position:relative;margin-bottom:1.5rem;animation:rise .6s var(--d,0s) ease both;}
.tl-item .dot{position:absolute;left:-3.55rem;top:-.15rem;width:2.5rem;height:2.5rem;border-radius:50%;background:var(--paper);border:2px solid var(--ink);display:grid;place-items:center;font-size:1.15rem;box-shadow:3px 3px 0 var(--ink);}
.tl-item h4{margin:0 0 .25rem;font-size:1.2rem;}
.tl-item p{margin:0;line-height:1.6;opacity:.88;}

.section-title{font-family:var(--serif);font-weight:800;font-size:2rem;margin:.2rem 0 .8rem;}
.footer{text-align:center;margin-top:2.6rem;padding-top:1.1rem;border-top:2px dashed var(--ink);font-size:.9rem;}

@media (max-width:820px){.hero{grid-template-columns:1fr;gap:2rem;padding:0 .6rem;}.s1{left:-4%;}.s2{right:-4%;}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>
"""
render(BASE_CSS)
if not animate:
    render("<style>*{animation:none!important;transition:none!important;}</style>")

if not st.session_state.welcomed:
    st.toast("Welcome! Explore the tabs below.", icon="👋")
    st.session_state.welcomed = True


# ============================================================
# DIALOG
# ============================================================
@st.dialog("Project details", width="large")
def project_dialog(p):
    st.subheader(p["title"])
    c1, c2 = st.columns(2)
    c1.metric("My role", p["role"])
    c2.metric("Tools", len(p["tools"]))
    st.write(p["summary"])
    render(chips(p["tools"], "tag"))
    st.success(f"**Outcome:** {p['outcome']}")
    if p.get("link"):
        st.link_button("Open project ↗", p["link"])


# ============================================================
# TABS
# ============================================================
tab_home, tab_story, tab_skills, tab_work, tab_contact = st.tabs(
    ["🏠 Home", "📖 Story", "🛠️ Skills", "💼 Work", "✉️ Contact"]
)

# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
with tab_home:
    render(
        f"""
        <div class="hero">
          <div>
            <span class="eyebrow">{esc(SECTION)}</span>
            <h1 class="display">{esc(FIRST)}<br><span class="hl">{esc(LAST)}</span></h1>
            <div class="lead">{esc(TAGLINE)}</div>
            <p class="sub">{esc(BIO)}</p>
            <div class="chips">
              <span class="chip fill">BS Information Technology</span>
              <span class="chip">4th Year</span>
              <span class="chip">{esc(SCHOOL_SHORT)}</span>
              <span class="chip">Cebu City</span>
            </div>
          </div>
          <div class="hero-photo">
            <div class="blob"></div>
            {photo_html("arch")}
            <div class="sticker s1">📍 Cebu City</div>
            <div class="sticker s2">🔐 Into cybersecurity</div>
            <div class="sticker s3">🎓 {esc(SCHOOL_SHORT)} · 4th year</div>
          </div>
        </div>
        """
    )

    b1, b2, b3, _ = st.columns([1, 1, 1, 2.2])
    with b1:
        st.link_button("✉️ Email me", f"mailto:{EMAIL}", type="primary")
    with b2:
        if st.button("👋 Say hi"):
            st.session_state.hellos += 1
            st.toast("Thanks for stopping by!", icon="🎉")
            st.balloons()
    with b3:
        with st.popover("⚡ Quick facts"):
            st.markdown(
                f"- **From:** Cebu City\n- **Studying:** {PROGRAM}\n"
                f"- **School:** {SCHOOL}\n- **Focus:** {', '.join(CAREER_INTERESTS[:2])}"
            )

    ticker = "  ✦  ".join(CAREER_INTERESTS + HOBBIES + ["Cebu City"])
    render(
        f"""
        <div class="marquee"><div class="track">
          <span>{esc(ticker)}  ✦ </span><span>{esc(ticker)}  ✦ </span>
        </div></div>
        """
    )

    earned = sum(1 for _, done in CERTS if done)
    avg = round(sum(s[1] for s in SKILLS) / len(SKILLS))
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Year level", "4th")
    m2.metric("Certificates", earned)
    m3.metric("Projects", len(PROJECTS))
    m4.metric("Average skill", f"{avg}/100")
    m5.metric("Hellos this session", st.session_state.hellos)

    st.write("")
    left, right = st.columns([1.45, 1], gap="large")
    with left:
        render('<div class="section-title">Ask me anything</div>')
        question = st.pills(
            "Pick a question",
            list(FAQ),
            selection_mode="single",
            default=list(FAQ)[0],
            label_visibility="collapsed",
        )
        if question:
            with st.chat_message("assistant", avatar=str(PHOTO_PATH) if PHOTO_PATH else "🧑‍💻"):
                if st.session_state.last_q != question:
                    type_out(FAQ[question])
                    st.session_state.last_q = question
                else:
                    st.write(FAQ[question])
        else:
            st.info("Pick a question above and I'll answer it.")
    with right:
        render('<div class="section-title">What I\'m aiming for</div>')
        render(f'<div class="card">{chips(CAREER_INTERESTS, "chip fill")}</div>')
        if show_certs:
            cert_html = "".join(
                f'<span class="chip">{"✅" if done else "⏳"} {esc(name)}</span>' for name, done in CERTS
            )
            render(f'<div class="card"><b>Certificates</b><br>{cert_html}</div>')

# ------------------------------------------------------------
# STORY
# ------------------------------------------------------------
with tab_story:
    render('<div class="section-title">The story so far</div>')

    g1, g2, g3 = st.columns(3, gap="large")
    with g1:
        render(
            """
            <div class="card"><div class="num">BACKGROUND</div><h3>Cebu City, born and raised</h3>
            <p>I had a fairly normal childhood, and my family is caring and compassionate.</p></div>
            """
        )
    with g2:
        render(
            f"""
            <div class="card"><div class="num">EDUCATION</div><h3>{esc(SCHOOL_SHORT)}, BSIT</h3>
            <p><b>Now:</b> {esc(SCHOOL)}, 4th year<br>
            <b>Senior high:</b> Asian College of Technology, Bulacao (STEM)<br>
            <b>Elementary to junior high:</b> St. Thomas Aquinas Montessori School, Bulacao</p></div>
            """
        )
    with g3:
        render(
            f"""
            <div class="card"><div class="num">INTERESTS</div><h3>Off the keyboard</h3>
            <p>{chips(HOBBIES)}</p></div>
            """
        )

    t_left, t_right = st.columns([1.35, 1], gap="large")
    with t_left:
        render('<div class="section-title">Milestones</div>')
        items = "".join(
            f'<div class="tl-item" style="--d:{i * 0.09:.2f}s"><span class="dot">{icon}</span>'
            f"<h4>{esc(title)}</h4><p>{esc(text)}</p></div>"
            for i, (icon, title, text) in enumerate(MILESTONES)
        )
        render(f'<div class="timeline">{items}</div>')
    with t_right:
        render('<div class="section-title">Find the overlap</div>')
        st.caption("Pick the things you enjoy too.")
        shared = st.multiselect("Which of these do you do as well?", HOBBIES)
        if shared:
            st.success(f"We have {len(shared)} thing(s) in common. Let's play sometime!")
        with st.expander("🛒 Experience", expanded=True):
            st.write(
                "Part-time at a hobby shop in Kinasang-an. It improved my Excel skills "
                "and my sales talk."
            )
        with st.expander("🎙️ Activities"):
            st.write(
                "- Debate club\n- Secretary to the Internal Vice President of the student council"
            )

# ------------------------------------------------------------
# SKILLS
# ------------------------------------------------------------
with tab_skills:
    render('<div class="section-title">Skills, in numbers</div>')
    cats = sorted({s[2] for s in SKILLS})

    f1, f2, f3 = st.columns([2, 1.2, 1.2], gap="large")
    with f1:
        picked = st.pills(
            "Categories", cats, selection_mode="multi", default=cats,
            format_func=lambda c: CATEGORY_LABELS.get(c, c),
        )
    with f2:
        min_level = st.slider("Minimum level", 0, 100, 0, step=5)
    with f3:
        sort_by = st.segmented_control("Sort by", ["Level", "A to Z"], default="Level") or "Level"

    rows = [s for s in SKILLS if (not picked or s[2] in picked) and s[1] >= min_level]
    rows.sort(key=(lambda s: -s[1]) if sort_by == "Level" else (lambda s: s[0]))

    if not rows:
        st.info("No skills match those filters. Lower the minimum level or pick another category.")
    else:
        s_left, s_right = st.columns([1.3, 1], gap="large")
        with s_left:
            bars = "".join(
                f'<div class="skill"><div class="top"><span>{esc(n)}</span><span>{lvl}%</span></div>'
                f'<div class="bar"><div class="fill" style="--v:{lvl};--d:{i * 0.08:.2f}s"></div></div></div>'
                for i, (n, lvl, _) in enumerate(rows)
            )
            render(f'<div class="card">{bars}</div>')
        with s_right:
            groups = {}
            for n, lvl, c in rows:
                groups.setdefault(c, []).append(lvl)
            rings = "".join(
                f'<div class="ring" style="--d:{i * 0.12:.2f}s"><div class="dial" style="--v:{round(sum(v) / len(v))}">'
                f"<b>{round(sum(v) / len(v))}</b></div><small>{esc(CATEGORY_LABELS.get(c, c))}</small></div>"
                for i, (c, v) in enumerate(groups.items())
            )
            render(f'<div class="card"><b>Average by category</b><br><br><div class="rings">{rings}</div></div>')
            top = max(rows, key=lambda s: s[1])
            st.metric("Top skill", top[0], f"{top[1]}/100", delta_color="off")

        sub_chart, sub_table, sub_compare = st.tabs(["📊 Chart", "🗂️ Table", "⚔️ Compare two"])
        with sub_chart:
            if HAS_PANDAS:
                df = pd.DataFrame(rows, columns=["Skill", "Level", "Category"])
                st.bar_chart(df, x="Skill", y="Level", color=ACCENT, horizontal=True)
            else:
                st.info("The chart needs pandas. The skill bars above show the same numbers.")
        with sub_table:
            if HAS_PANDAS:
                df = pd.DataFrame(rows, columns=["Skill", "Level", "Category"])
                st.dataframe(
                    df,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "Level": st.column_config.ProgressColumn(
                            "Level", min_value=0, max_value=100, format="%d"
                        )
                    },
                )
            else:
                st.markdown("\n".join(f"- **{n}**: {lvl}/100 ({c})" for n, lvl, c in rows))
        with sub_compare:
            names = [s[0] for s in rows]
            c1, c2 = st.columns(2)
            a = c1.selectbox("Skill A", names, index=0)
            b = c2.selectbox("Skill B", names, index=min(1, len(names) - 1))
            la = next(s[1] for s in rows if s[0] == a)
            lb = next(s[1] for s in rows if s[0] == b)
            k1, k2 = st.columns(2)
            k1.metric(a, f"{la}/100", f"{la - lb:+d} vs {b}")
            k2.metric(b, f"{lb}/100", f"{lb - la:+d} vs {a}")

# ------------------------------------------------------------
# WORK
# ------------------------------------------------------------
with tab_work:
    render('<div class="section-title">Selected work</div>')
    all_tools = sorted({t for p in PROJECTS for t in p["tools"]})
    pick = st.pills("Filter by tool", all_tools, selection_mode="single")
    shown = [(i, p) for i, p in enumerate(PROJECTS, start=1) if not pick or pick in p["tools"]]

    def project_card(idx, p):
        render(
            f"""
            <div class="card"><div class="num">PROJECT {idx:02d}</div>
            <h3>{esc(p["title"])}</h3><div class="role">{esc(p["role"])}</div>
            <p>{esc(p["summary"])}</p><div>{chips(p["tools"], "tag")}</div>
            <div class="outcome">🏁 {esc(p["outcome"])}</div></div>
            """
        )
        if st.button("View details", key=f"proj_{idx}"):
            project_dialog(p)

    if not shown:
        st.info("No projects use that tool yet.")
    else:
        first_idx, first = shown[0]
        project_card(first_idx, first)
        rest = shown[1:]
        for start in range(0, len(rest), 2):
            cols = st.columns(2, gap="large")
            for col, (idx, p) in zip(cols, rest[start:start + 2]):
                with col:
                    project_card(idx, p)

# ------------------------------------------------------------
# CONTACT
# ------------------------------------------------------------
with tab_contact:
    render('<div class="section-title">Say hello</div>')
    c_left, c_right = st.columns([1, 1.25], gap="large")
    with c_left:
        render(
            """
            <div class="card"><div class="num">GET IN TOUCH</div><h3>Questions, feedback, or a hello?</h3>
            <p>Send a note with the form, or copy my email below.</p></div>
            """
        )
        st.code(EMAIL, language=None)
        for label, url in ACTIVE_SOCIALS:
            st.link_button(label, url, width="stretch")
        st.caption("Quick vibe check: how did this site feel?")
        vibe = st.feedback("faces", key="vibe")
        if vibe is not None:
            st.caption(REACTIONS[vibe])

    with c_right:
        with st.form("contact", clear_on_submit=True):
            f1, f2 = st.columns(2)
            name = f1.text_input("Your name")
            email = f2.text_input("Your email")
            topic = st.selectbox("Topic", ["Collaboration", "Opportunity", "Feedback", "Just saying hi"])
            reply_via = st.radio("Best way to reply", ["Email", "Facebook", "Instagram"], horizontal=True)
            rating = st.slider("How would you rate this portfolio?", 1, 5, 4)
            interests = st.multiselect("What caught your eye?", ["Story", "Skills", "Projects", "Design"])
            message = st.text_area("Message", height=120)
            agree = st.checkbox("I agree that the site owner may read this message")
            sent = st.form_submit_button("Send message 🚀", type="primary")

        if sent:
            if not name.strip() or "@" not in email or not message.strip() or not agree:
                st.error("Please add your name, a valid email, a message, and tick the box.")
            else:
                st.session_state.messages.append(
                    {
                        "name": name.strip(),
                        "email": email.strip(),
                        "reply_via": reply_via,
                        "topic": topic,
                        "rating": rating,
                        "interests": ", ".join(interests),
                        "message": message.strip(),
                    }
                )
                st.toast("Message sent!", icon="✅")
                st.balloons()
                st.success(f"Thanks, {name.strip()}! I'll reply by {reply_via.lower()} soon.")

    st.write("")
    with st.expander(f"📬 Inbox for this session ({len(st.session_state.messages)})"):
        if not st.session_state.messages:
            st.caption("Messages sent from the form appear here until you close the tab.")
        else:
            for m in st.session_state.messages:
                st.markdown(f"**{m['name']}** · {m['topic']} · {'⭐' * m['rating']}  \n{m['message']}")
            st.download_button(
                "Download messages (CSV)", data=messages_csv(), file_name="messages.csv", mime="text/csv"
            )

# ============================================================
# FOOTER
# ============================================================
render(
    f"""
    <div class="footer">© {datetime.now().year} {esc(NAME)} · {esc(SECTION)} · Made in Cebu City with Streamlit 🌿</div>
    """
)
