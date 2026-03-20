import PyPDF2
import re
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════
#   RESUME RANKER PRO  |  Multi-Candidate ATS Analyzer
# ══════════════════════════════════════════════════════════

COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "blue":   "\033[94m",
    "white":  "\033[97m",
    "gray":   "\033[90m",
    "bg_dark":"\033[48;5;235m",
    "gold":   "\033[38;5;220m",
    "silver": "\033[38;5;250m",
    "bronze": "\033[38;5;130m",
}

def c(color, text):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

# ─────────────────────────────────────────────
# SKILL TAXONOMY  (weighted by market demand)
# ─────────────────────────────────────────────
SKILL_WEIGHTS = {
    # Core Engineering
    "python": 3, "java": 3, "c++": 3, "go": 3, "rust": 3,
    "javascript": 2, "typescript": 2, "sql": 3,

    # AI / ML
    "machine learning": 4, "deep learning": 4, "nlp": 3,
    "tensorflow": 3, "pytorch": 3, "scikit": 2, "llm": 3,
    "transformers": 3, "computer vision": 3,

    # Web & APIs
    "react": 2, "django": 2, "flask": 2, "fastapi": 2,
    "node": 2, "graphql": 2, "rest": 2, "api": 2, "apis": 2,

    # Data
    "data structures": 3, "algorithms": 3, "pandas": 2,
    "spark": 3, "hadoop": 2, "kafka": 2, "airflow": 2,
    "postgresql": 2, "mysql": 2, "mongodb": 2, "redis": 2,

    # Infrastructure
    "docker": 2, "kubernetes": 3, "aws": 3, "gcp": 2,
    "azure": 2, "terraform": 2, "ci/cd": 2, "devops": 2,

    # Soft Skills
    "git": 1, "agile": 1, "scrum": 1, "leadership": 1,
    "communication": 1, "problem solving": 1, "teamwork": 1,
}

SKILL_CATEGORIES = {
    "AI/ML":         ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "llm", "transformers", "computer vision", "scikit"],
    "Backend":       ["python", "java", "go", "rust", "django", "flask", "fastapi", "node", "c++"],
    "Frontend":      ["javascript", "typescript", "react", "graphql"],
    "Data":          ["sql", "pandas", "spark", "hadoop", "kafka", "airflow", "postgresql", "mysql", "mongodb", "redis"],
    "Cloud/DevOps":  ["docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci/cd", "devops"],
    "Fundamentals":  ["data structures", "algorithms", "rest", "api", "apis", "git"],
    "Soft Skills":   ["agile", "scrum", "communication", "leadership", "problem solving", "teamwork"],
}

RESUME_SECTIONS = ["experience", "education", "skills", "projects",
                   "certifications", "summary", "achievements", "publications"]

# ─────────────────────────────────────────────
# PDF EXTRACTION
# ─────────────────────────────────────────────
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text, num_pages
    except FileNotFoundError:
        return None, 0
    except Exception as e:
        print(c("red", f"  [ERROR] {file_path}: {e}"))
        return None, 0

# ─────────────────────────────────────────────
# TEXT PROCESSING
# ─────────────────────────────────────────────
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#\/]', ' ', text)
    return text

def extract_email(text):
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group() if match else "—"

def extract_phone(text):
    match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
    return match.group() if match else "—"

def detect_sections(resume_text):
    resume_lower = resume_text.lower()
    return [s.title() for s in RESUME_SECTIONS if s in resume_lower]

def estimate_experience_years(text):
    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|present|current)', text.lower())
    total = 0
    current_year = datetime.now().year
    for start, end in matches:
        try:
            s = int(start)
            e = current_year if end in ("present", "current") else int(end)
            if 1990 <= s <= current_year and s <= e:
                total += (e - s)
        except:
            pass
    return min(total, 30)

# ─────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────
def extract_jd_keywords(jd_text):
    jd_clean = clean_text(jd_text)
    keywords = {}
    for skill, weight in SKILL_WEIGHTS.items():
        if skill in jd_clean:
            keywords[skill] = weight
    for word in jd_clean.split():
        if len(word) > 3 and word not in keywords:
            keywords[word] = 1
    return keywords

def score_by_category(jd_keywords, resume_clean):
    cat_scores = {}
    for cat, skills in SKILL_CATEGORIES.items():
        relevant = [s for s in skills if s in jd_keywords]
        if not relevant:
            continue
        matched = sum(1 for s in relevant if s in resume_clean)
        cat_scores[cat] = round((matched / len(relevant)) * 100)
    return cat_scores

def calculate_score(jd_text, resume_text):
    jd_keywords = extract_jd_keywords(jd_text)
    resume_clean = clean_text(resume_text)

    total_weight = sum(jd_keywords.values())
    matched_weight = 0
    matched, missing = [], []

    for kw, weight in jd_keywords.items():
        if kw in resume_clean:
            matched_weight += weight
            matched.append((kw, weight))
        else:
            missing.append((kw, weight))

    score = round((matched_weight / total_weight) * 100, 1) if total_weight else 0
    return score, matched, missing, jd_keywords

def get_tier(score):
    if score >= 70: return "A", "green",  "Strong Fit"
    if score >= 40: return "B", "yellow", "Moderate Fit"
    return              "C", "red",    "Not Fit"

# ─────────────────────────────────────────────
# ANALYZE ONE RESUME
# ─────────────────────────────────────────────
def analyze_resume(resume_path, jd_text):
    resume_text, num_pages = extract_text_from_pdf(resume_path)
    if not resume_text or not resume_text.strip():
        return None

    score, matched, missing, jd_keywords = calculate_score(jd_text, resume_text)
    tier, tier_color, tier_label = get_tier(score)
    cat_scores = score_by_category(jd_keywords, clean_text(resume_text))
    sections = detect_sections(resume_text)
    exp_years = estimate_experience_years(resume_text)
    word_count = len(resume_text.split())

    top_strengths = sorted(matched, key=lambda x: -x[1])[:3]
    top_gaps      = sorted(missing, key=lambda x: -x[1])[:3]

    name = os.path.splitext(os.path.basename(resume_path))[0].replace("_", " ").title()

    return {
        "path":         resume_path,
        "name":         name,
        "score":        score,
        "tier":         tier,
        "tier_color":   tier_color,
        "tier_label":   tier_label,
        "strengths":    top_strengths,
        "gaps":         top_gaps,
        "cat_scores":   cat_scores,
        "sections":     sections,
        "exp_years":    exp_years,
        "word_count":   word_count,
        "pages":        num_pages,
        "email":        extract_email(resume_text),
        "phone":        extract_phone(resume_text),
        "matched_count": len(matched),
        "missing_count": len(missing),
    }

# ─────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────
def bar(pct, width=20, filled="█", empty="░"):
    filled_len = int(width * pct / 100)
    return filled * filled_len + empty * (width - filled_len)

def score_color(score):
    if score >= 85: return "gold"
    if score >= 70: return "green"
    if score >= 55: return "cyan"
    if score >= 40: return "yellow"
    return "red"

def rank_medal(rank):
    return [c("gold", "🥇"), c("silver", "🥈"), c("bronze", "🥉")][rank] if rank < 3 else f"  {rank+1}."

# ─────────────────────────────────────────────
# PRINT DASHBOARD
# ─────────────────────────────────────────────
def print_dashboard(results, jd_text):
    W = 78
    print()
    print(c("cyan", "╔" + "═"*W + "╗"))
    print(c("cyan", "║") + c("bold", c("white", "  ██████╗ ███████╗███████╗██╗   ██╗███╗   ███╗███████╗  ")) + c("cyan", "       ║"))
    print(c("cyan", "║") + c("white", "         RESUME RANKER PRO  ·  Multi-Candidate ATS Engine         ") + c("cyan", "║"))
    print(c("cyan", "╚" + "═"*W + "╝"))
    print()

    # ── Summary Bar ──
    total = len(results)
    elite = sum(1 for r in results if r["score"] >= 85)
    strong = sum(1 for r in results if 70 <= r["score"] < 85)
    avg_score = round(sum(r["score"] for r in results) / total, 1) if total else 0

    print(c("bold", c("white", f"  Analyzed {total} candidates  ·  Avg Score: {avg_score}%  ·  Elite: {elite}  ·  Strong: {strong}")))
    print(c("gray", "  " + "─"*60))
    print()

    # ── RANKING TABLE ──
    print(c("bold", c("white", "  LEADERBOARD")))
    print(c("gray", "  " + "┄"*70))
    print(c("gray", f"  {'Rank':<5} {'Candidate':<22} {'Score':>7}  {'Progress Bar':<22} {'Tier':<14} {'Exp':>5}"))
    print(c("gray", "  " + "─"*70))

    for i, r in enumerate(results):
        medal = rank_medal(i)
        sc = r["score"]
        clr = score_color(sc)
        prog = bar(sc, 18)
        tier_str = c(r["tier_color"], f"[{r['tier']}] {r['tier_label']}")
        exp_str = f"{r['exp_years']}y" if r['exp_years'] > 0 else "—"
        print(f"  {medal:<6} {c('bold', r['name']):<30} {c(clr, f'{sc}%'):>10}  {c(clr, prog):<30} {tier_str:<30} {c('gray', exp_str):>8}")

    print(c("gray", "  " + "─"*70))
    print()

    # ── DETAILED CARDS ──
    print(c("bold", c("white", "  CANDIDATE PROFILES")))
    print()

    for i, r in enumerate(results):
        rank_label = ["#1 TOP PICK", "#2", "#3"][i] if i < 3 else f"#{i+1}"
        clr = score_color(r["score"])

        print(c("gray", "  ┌" + "─"*72 + "┐"))
        header = f"  {rank_label}  {r['name'].upper()}"
        print(c("gray", "  │") + c("bold", c(clr, f"  {rank_label}  ")) + c("bold", c("white", r["name"])) + c("gray", " " * max(1, 72 - len(f"  {rank_label}  {r['name']}") - 1) + "│"))
        print(c("gray", "  │") + c("gray", f"  {r['email']}  ·  {r['phone']}  ·  {r['pages']}p resume  ·  {r['word_count']} words") + c("gray", " " * max(1, 72 - len(f"  {r['email']}  ·  {r['phone']}  ·  {r['pages']}p resume  ·  {r['word_count']} words") - 1) + "│"))
        print(c("gray", "  ├" + "─"*72 + "┤"))

        # Score row
        sc = r["score"]
        prog = bar(sc, 30)
        score_line = f"  Score: {sc}%  {c(clr, prog)}  {c(r['tier_color'], r['tier_label'])}"
        print(c("gray", "  │") + f"  {c('bold', c(clr, str(sc)+'%'))}  {c(clr, bar(sc, 28))}  {c(r['tier_color'], r['tier_label'])}" + c("gray", "  │"))

        # Category breakdown
        if r["cat_scores"]:
            print(c("gray", "  │") + c("dim", c("white", "  Category Breakdown:")) + c("gray", " " * 51 + "│"))
            cats = list(r["cat_scores"].items())
            for j in range(0, len(cats), 2):
                left_cat, left_sc = cats[j]
                right = f"  {cats[j+1][0]:<14} {bar(cats[j+1][1], 10)} {cats[j+1][1]}%" if j+1 < len(cats) else ""
                lc = score_color(left_sc)
                lline = f"  {left_cat:<14} {c(lc, bar(left_sc, 10))} {c(lc, str(left_sc)+'%')}"
                padding = " " * max(1, 72 - len(f"  {left_cat:<14}            {left_sc}%  {cats[j+1][0] if j+1 < len(cats) else ''}            {cats[j+1][1] if j+1 < len(cats) else ''}%") )
                if j+1 < len(cats):
                    rc, rsc = cats[j+1][0], cats[j+1][1]
                    rcol = score_color(rsc)
                    print(c("gray", "  │") + lline + f"    {rc:<14} {c(rcol, bar(rsc, 10))} {c(rcol, str(rsc)+'%')}" + c("gray", "  │"))
                else:
                    print(c("gray", "  │") + lline + c("gray", "  │"))

        # Strengths
        if r["strengths"]:
            strength_tags = "  ".join([c("green", f"✓ {kw}") for kw, _ in r["strengths"]])
            print(c("gray", "  │") + c("dim", c("white", "  Top Strengths: ")) + strength_tags + c("gray", "  │"))

        # Gaps
        if r["gaps"]:
            gap_tags = "  ".join([c("red", f"✗ {kw}") for kw, _ in r["gaps"]])
            print(c("gray", "  │") + c("dim", c("white", "  Key Gaps:      ")) + gap_tags + c("gray", "  │"))

        # Sections
        if r["sections"]:
            sec_str = "  ".join([c("blue", s) for s in r["sections"]])
            print(c("gray", "  │") + c("dim", c("white", "  Sections:      ")) + sec_str + c("gray", "  │"))

        print(c("gray", "  └" + "─"*72 + "┘"))
        print()

    # ── HIRING RECOMMENDATION ──
    if results:
        top = results[0]
        print(c("cyan", "  ╔" + "═"*50 + "╗"))
        print(c("cyan", "  ║") + c("bold", c("gold", "  ★ HIRING RECOMMENDATION                          ")) + c("cyan", "║"))
        print(c("cyan", "  ║") + c("white", f"  Proceed with: {top['name']:<34}") + c("cyan", "║"))
        print(c("cyan", "  ║") + c("white", f"  Score: {top['score']}%  ·  {top['tier_label']:<37}") + c("cyan", "║"))
        if top["gaps"]:
            gap_list = ", ".join([kw for kw, _ in top["gaps"][:3]])
            print(c("cyan", "  ║") + c("gray", f"  Address gaps in: {gap_list:<34}") + c("cyan", "║"))
        print(c("cyan", "  ╚" + "═"*50 + "╝"))

    print()
    print(c("gray", f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
    print()


# ══════════════════════════════════════════════════════════
#   MAIN
# ══════════════════════════════════════════════════════════
JD = """
Looking for a candidate with Python, SQL, React, APIs, Data Structures,
problem solving skills, REST APIs, Docker, Git, and good communication.
Experience with Agile methodology is a plus. Machine learning knowledge
and AWS cloud experience are highly valued.
"""

# Add your resume file paths here
RESUMES = [
    "resume.pdf",
    "resume1.pdf",
    "resume2.pdf",
    "resume3.pdf",
]

if __name__ == "__main__":
    print(c("gray", "\n  Scanning resumes..."))
    results = []
    for path in RESUMES:
        result = analyze_resume(path, JD)
        if result:
            results.append(result)
            print(c("green", f"  ✓ {path}") + c("gray", f"  →  {result['score']}%"))
        else:
            print(c("yellow", f"  ⚠ Skipped: {path} (not found or empty)"))

    if not results:
        print(c("red", "\n  No valid resumes found. Check file paths.\n"))
    else:
        results.sort(key=lambda x: -x["score"])
        print_dashboard(results, JD)

        # Export CSV
        csv_path = "ranking_report.csv"
        with open(csv_path, "w") as f:
            f.write("Rank,Name,Score,Tier,Experience_Years,Matched_Skills,Missing_Skills,Sections,Pages\n")
            for i, r in enumerate(results, 1):
                f.write(f"{i},{r['name']},{r['score']},{r['tier_label']},{r['exp_years']},"
                        f"{r['matched_count']},{r['missing_count']},\"{' | '.join(r['sections'])}\",{r['pages']}\n")
        print(c("cyan", f"  Report saved → {csv_path}\n"))