import streamlit as st
import sqlite3
import hashlib
import json
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math
import re

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UltraCoach AI",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0a0c0f;
    --surface: #111418;
    --surface2: #1a1f26;
    --border: #252b35;
    --accent: #e8ff47;
    --accent2: #ff6b35;
    --accent3: #00d4aa;
    --text: #e8edf5;
    --muted: #6b7a8d;
    --danger: #ff4444;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg);
}

/* Remove Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1200px !important; }

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(232,255,71,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.04em;
    color: var(--accent);
    line-height: 1;
    margin: 0;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    border-left: 3px solid var(--accent);
}
.card-danger {
    border-left: 3px solid var(--danger);
}
.card-green {
    border-left: 3px solid var(--accent3);
}

/* Metric badges */
.metric-badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    color: var(--accent);
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
}

/* Priority badges */
.badge-a { background: #ff4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-b { background: #ff6b35; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-c { background: #4a9eff; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

/* Training day blocks */
.day-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    position: relative;
}
.day-block.rest { opacity: 0.5; }
.day-block.long { border-left: 3px solid var(--accent); }
.day-block.gym { border-left: 3px solid var(--accent2); }
.day-block.done { border-left: 3px solid var(--accent3); opacity: 0.7; }
.day-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
}
.day-workout {
    font-size: 0.95rem;
    font-weight: 500;
    margin-top: 0.2rem;
}

/* Streamlit element overrides */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #0a0c0f !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #d4eb3a !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 0.3rem !important;
    gap: 0.2rem !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #0a0c0f !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Dividers */
hr { border-color: var(--border) !important; }

/* Dataframes */
.stDataFrame { background: var(--surface) !important; }

/* Success/Error/Info messages */
.stSuccess { background: rgba(0,212,170,0.1) !important; border: 1px solid var(--accent3) !important; }
.stError { background: rgba(255,68,68,0.1) !important; border: 1px solid var(--danger) !important; }
.stInfo { background: rgba(74,158,255,0.1) !important; border: 1px solid #4a9eff !important; }

/* Section headers */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.05em;
    color: var(--accent);
    margin-bottom: 1rem;
}
.section-sub {
    color: var(--muted);
    font-size: 0.85rem;
    margin-top: -0.8rem;
    margin-bottom: 1rem;
}

/* Login card */
.login-wrap {
    max-width: 420px;
    margin: 4rem auto;
}
.login-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4rem;
    color: var(--accent);
    text-align: center;
    letter-spacing: 0.08em;
}
.login-tagline {
    text-align: center;
    color: var(--muted);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ─── DATABASE ──────────────────────────────────────────────────────────────────
import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultracoach.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'athlete',
        nome TEXT,
        idade INTEGER,
        altura REAL,
        peso_inicial REAL,
        km_semanais REAL DEFAULT 40,
        pace_medio REAL DEFAULT 6.0,
        dias_corrida TEXT DEFAULT '[]',
        dias_reforco TEXT DEFAULT '[]',
        dia_longo TEXT DEFAULT 'Sunday',
        fc_maxima INTEGER DEFAULT 180
    );

    CREATE TABLE IF NOT EXISTS objetivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nome TEXT,
        data TEXT,
        prioridade TEXT,
        distancia REAL,
        altimetria REAL,
        tempo_alvo TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS metricas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        data TEXT,
        hrv REAL,
        rhr REAL,
        sleep_score REAL,
        body_battery REAL,
        nivel_energia INTEGER,
        peso_atual REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS plano (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        data TEXT,
        descricao TEXT,
        distancia_alvo REAL,
        pace_alvo REAL,
        tipo TEXT DEFAULT 'run',
        status TEXT DEFAULT 'Pendente',
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS galeria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        tipo TEXT,
        url TEXT,
        data TEXT
    );
    """)
    # Create default admin
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, nome) VALUES (?, ?, 'admin', 'Administrador')", ("admin", pw))
    conn.commit()
    conn.close()


def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def login_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_pw(password)))
    row = c.fetchone()
    conn.close()
    return row

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_user(user_id, **kwargs):
    conn = get_conn()
    c = conn.cursor()
    for k, v in kwargs.items():
        c.execute(f"UPDATE users SET {k}=? WHERE id=?", (v, user_id))
    conn.commit()
    conn.close()

def get_all_athletes():
    conn = get_conn()
    df = pd.read_sql("SELECT id, username, nome, idade, km_semanais FROM users WHERE role='athlete'", conn)
    conn.close()
    return df

def create_athlete(username, password, nome):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role, nome) VALUES (?, ?, 'athlete', ?)",
                  (username, hash_pw(password), nome))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Objetivos
def get_objetivos(user_id):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM objetivos WHERE user_id=? ORDER BY data", conn, params=(user_id,))
    conn.close()
    return df

def add_objetivo(user_id, nome, data, prioridade, distancia, altimetria, tempo_alvo):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO objetivos (user_id, nome, data, prioridade, distancia, altimetria, tempo_alvo) VALUES (?,?,?,?,?,?,?)",
              (user_id, nome, data, prioridade, distancia, altimetria, tempo_alvo))
    conn.commit()
    conn.close()

def delete_objetivo(obj_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM objetivos WHERE id=?", (obj_id,))
    conn.commit()
    conn.close()

# Métricas
def add_metrica(user_id, data, hrv, rhr, sleep_score, body_battery, nivel_energia, peso_atual):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO metricas (user_id, data, hrv, rhr, sleep_score, body_battery, nivel_energia, peso_atual) VALUES (?,?,?,?,?,?,?,?)",
              (user_id, data, hrv, rhr, sleep_score, body_battery, nivel_energia, peso_atual))
    conn.commit()
    conn.close()

def get_metricas(user_id, days=30):
    conn = get_conn()
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    df = pd.read_sql("SELECT * FROM metricas WHERE user_id=? AND data>=? ORDER BY data", conn, params=(user_id, cutoff))
    conn.close()
    return df

# Plano
def get_plano(user_id, start=None, end=None):
    conn = get_conn()
    if start and end:
        df = pd.read_sql("SELECT * FROM plano WHERE user_id=? AND data BETWEEN ? AND ? ORDER BY data",
                         conn, params=(user_id, start, end))
    else:
        df = pd.read_sql("SELECT * FROM plano WHERE user_id=? ORDER BY data", conn, params=(user_id,))
    conn.close()
    return df

def insert_treino(user_id, data, descricao, distancia_alvo, pace_alvo, tipo):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO plano (user_id, data, descricao, distancia_alvo, pace_alvo, tipo) VALUES (?,?,?,?,?,?)",
              (user_id, data, descricao, distancia_alvo, pace_alvo, tipo))
    conn.commit()
    conn.close()

def clear_plano(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM plano WHERE user_id=? AND status='Pendente'", (user_id,))
    conn.commit()
    conn.close()

def mark_treino_done(plano_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE plano SET status='Concluído' WHERE id=?", (plano_id,))
    conn.commit()
    conn.close()

def mark_treino_missed(plano_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE plano SET status='Falhado' WHERE id=?", (plano_id,))
    conn.commit()
    conn.close()

# Galeria
def get_galeria():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM galeria ORDER BY data DESC", conn)
    conn.close()
    return df

def add_galeria(titulo, tipo, url):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO galeria (titulo, tipo, url, data) VALUES (?,?,?,?)",
              (titulo, tipo, url, date.today().isoformat()))
    conn.commit()
    conn.close()

def delete_galeria(g_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM galeria WHERE id=?", (g_id,))
    conn.commit()
    conn.close()


# ─── TREINO ENGINE ─────────────────────────────────────────────────────────────
DIAS_PT = {"Monday":"Segunda","Tuesday":"Terça","Wednesday":"Quarta",
           "Thursday":"Quinta","Friday":"Sexta","Saturday":"Sábado","Sunday":"Domingo"}
DIAS_EN = list(DIAS_PT.keys())

def gerar_plano(user_id):
    """Core training plan generator."""
    clear_plano(user_id)
    user = get_user(user_id)
    if not user: return False, "Utilizador não encontrado."

    # Unpack user
    (uid, username, pw, role, nome, idade, altura, peso_inicial,
     km_semanais, pace_medio, dias_corrida_json, dias_reforco_json,
     dia_longo, fc_maxima) = user[:15]

    dias_corrida = json.loads(dias_corrida_json or "[]")
    dias_reforco = json.loads(dias_reforco_json or "[]")
    km_base = km_semanais or 40
    pace = pace_medio or 6.0

    # Get Prova A
    objs = get_objetivos(user_id)
    prova_a = objs[objs["prioridade"] == "A"]
    if prova_a.empty:
        return False, "Define primeiro um Objetivo Prioridade A."

    prova_a = prova_a.iloc[0]
    data_prova = datetime.strptime(prova_a["data"], "%Y-%m-%d").date()
    altimetria = prova_a["altimetria"] or 0

    hoje = date.today()
    if data_prova <= hoje:
        return False, "A data da Prova A já passou."

    semanas_totais = max(1, (data_prova - hoje).days // 7)
    semanas_pico = max(1, semanas_totais - 3)  # 3 weeks taper before race
    tem_rampas = altimetria > 1500

    # Build week schedule template
    dias_validos = dias_corrida if dias_corrida else ["Saturday", "Sunday"]

    semana_atual = hoje
    for semana in range(semanas_totais):
        data_inicio = hoje + timedelta(weeks=semana)

        # Volume progression: ramp up to peak, then taper
        if semana < semanas_pico:
            fator = 1 + (semana / semanas_pico) * 0.5  # up to 50% increase
            # Apply 10% rule per week
            fator = min(fator, 1 + semana * 0.08)
        else:
            # Taper: reduce 20% per week in final 3 weeks
            semanas_taper = semana - semanas_pico
            fator = 0.8 - semanas_taper * 0.15

        km_semana = max(15, km_base * fator)

        # Distribute km across running days
        n_dias = max(1, len(dias_validos))
        km_por_dia = km_semana / n_dias

        for offset in range(7):
            dia = data_inicio + timedelta(days=offset)
            if dia >= data_prova: break
            nome_dia = DIAS_EN[dia.weekday()]

            is_long = (nome_dia == dia_longo)
            is_reforco = (nome_dia in dias_reforco) and not is_long
            is_corrida = (nome_dia in dias_validos) or is_long

            if is_long:
                km_dia = km_semana * 0.35  # 35% of weekly on long run
                desc = f"🏃 TREINO LONGO — {km_dia:.1f}km"
                if tem_rampas:
                    desc += " | Incluir subidas longas (rampas/trilho com D+)"
                desc += f" | Pace: {pace+0.5:.1f} min/km"
                insert_treino(user_id, dia.isoformat(), desc, km_dia, pace+0.5, "long")

            elif is_corrida and nome_dia in dias_validos:
                km_dia = km_por_dia * 0.65  # shorter on non-long days
                if semana % 4 == 2 and tem_rampas:
                    desc = f"⛰️ RAMPAS/ESCADAS — {km_dia:.1f}km | Foco em D+, subidas específicas | Pace esforço"
                    tipo = "hills"
                elif semana % 3 == 1:
                    desc = f"⚡ INTERVALOS — {km_dia:.1f}km | Aquecimento + séries a ritmo de corrida | Pace: {pace-1:.1f} min/km"
                    tipo = "intervals"
                else:
                    desc = f"🔄 RECUPERAÇÃO ATIVA — {km_dia:.1f}km | Pace leve: {pace+1.5:.1f} min/km"
                    tipo = "easy"
                insert_treino(user_id, dia.isoformat(), desc, km_dia, pace, tipo)

            if is_reforco:
                desc = "💪 REFORÇO MUSCULAR — Pernas + Core | Agachamentos, lunges, step-ups, calf raises, prancha | 3×15 reps"
                insert_treino(user_id, dia.isoformat(), desc, 0, 0, "gym")

    return True, f"✅ Plano gerado com {semanas_totais} semanas até à Prova A!"


def ajustar_semana(user_id):
    """Redistribute this week's missed training."""
    hoje = date.today()
    fim_semana = hoje + timedelta(days=(6 - hoje.weekday()))
    conn = get_conn()
    c = conn.cursor()
    # Find missed/pending from past 3 days
    c.execute("""UPDATE plano SET status='Ajustado'
                 WHERE user_id=? AND data BETWEEN ? AND ? AND status='Pendente'""",
              (user_id, (hoje - timedelta(days=3)).isoformat(), hoje.isoformat()))
    conn.commit()
    conn.close()
    return "⚠️ Semana ajustada. Treinos em falta marcados como ajustados para evitar sobretreino. Foca nos próximos dias!"


# ─── HELPERS ───────────────────────────────────────────────────────────────────
def youtube_embed(url):
    vid_id = None
    patterns = [r"v=([a-zA-Z0-9_-]+)", r"youtu\.be/([a-zA-Z0-9_-]+)", r"embed/([a-zA-Z0-9_-]+)"]
    for p in patterns:
        m = re.search(p, url)
        if m: vid_id = m.group(1); break
    if vid_id:
        return f'<iframe width="100%" height="220" src="https://www.youtube.com/embed/{vid_id}" frameborder="0" allowfullscreen style="border-radius:10px;"></iframe>'
    return None

def calc_imc(peso, altura):
    if altura and peso: return round(peso / (altura/100)**2, 1)
    return None

def pace_display(pace_dec):
    mins = int(pace_dec)
    secs = int((pace_dec - mins) * 60)
    return f"{mins}:{secs:02d} min/km"


# ─── UI COMPONENTS ─────────────────────────────────────────────────────────────
def render_header(user_name, role):
    badge = "🛡️ ADMIN" if role == "admin" else "🏃 ATLETA"
    st.markdown(f"""
    <div class="hero-header">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <div class="hero-title">ULTRACOACH AI</div>
                <div class="hero-sub">🏔️ Treinador Autónomo de Ultra Trail</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:var(--accent);">{user_name}</div>
                <div style="font-size:0.78rem;color:var(--muted);background:var(--surface2);padding:3px 10px;border-radius:20px;border:1px solid var(--border);display:inline-block;">{badge}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── ATHLETE TABS ──────────────────────────────────────────────────────────────
def tab_biometria(user):
    (uid, username, pw, role, nome, idade, altura, peso_inicial,
     km_semanais, pace_medio, _, __, dia_longo, fc_maxima) = user[:15]

    st.markdown('<div class="section-title">👤 Biometria</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Os teus dados físicos base</div>', unsafe_allow_html=True)

    imc = calc_imc(peso_inicial, altura)
    if imc:
        cat = "Baixo Peso" if imc < 18.5 else ("Normal" if imc < 25 else ("Excesso" if imc < 30 else "Obesidade"))
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown(f'<div class="metric-badge"><div class="metric-val">{altura or "--"}</div><div class="metric-label">Altura (cm)</div></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="metric-badge"><div class="metric-val">{peso_inicial or "--"}</div><div class="metric-label">Peso (kg)</div></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="metric-badge"><div class="metric-val">{imc}</div><div class="metric-label">IMC</div></div>', unsafe_allow_html=True)
        with col4: st.markdown(f'<div class="metric-badge"><div class="metric-val">{fc_maxima or "--"}</div><div class="metric-label">FC Máx.</div></div>', unsafe_allow_html=True)
        st.caption(f"Categoria IMC: **{cat}**")
        st.markdown("---")

    with st.expander("✏️ Editar Dados Biométricos", expanded=not bool(altura)):
        with st.form("bio_form"):
            c1, c2 = st.columns(2)
            nome_n = c1.text_input("Nome", value=nome or "")
            idade_n = c2.number_input("Idade", 15, 80, value=int(idade) if idade else 30)
            altura_n = c1.number_input("Altura (cm)", 140, 220, value=int(altura) if altura else 170)
            peso_n = c2.number_input("Peso Inicial (kg)", 40.0, 150.0, value=float(peso_inicial) if peso_inicial else 70.0, step=0.1)
            fc_n = c1.number_input("FC Máxima (bpm)", 140, 220, value=int(fc_maxima) if fc_maxima else 180)
            if st.form_submit_button("💾 Guardar"):
                update_user(uid, nome=nome_n, idade=idade_n, altura=altura_n, peso_inicial=peso_n, fc_maxima=fc_n)
                st.success("Dados guardados!"); st.rerun()


def tab_config(user):
    (uid, username, pw, role, nome, idade, altura, peso_inicial,
     km_semanais, pace_medio, dias_corrida_json, dias_reforco_json,
     dia_longo, fc_maxima) = user[:15]

    dias_corrida = json.loads(dias_corrida_json or "[]")
    dias_reforco = json.loads(dias_reforco_json or "[]")

    st.markdown('<div class="section-title">⚙️ Configuração de Treino</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Define o teu volume, ritmo e disponibilidade semanal</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    km_n = c1.number_input("Volume Semanal (km)", 10, 200, value=int(km_semanais or 40))
    pace_min = int(pace_medio or 6)
    pace_sec = int(((pace_medio or 6.0) - pace_min) * 60)
    pm_min = c2.number_input("Pace Médio (min)", 3, 10, value=pace_min)
    pm_sec = c3.number_input("Pace Médio (seg)", 0, 59, value=pace_sec, step=5)
    pace_n = pm_min + pm_sec / 60

    dias_opts = DIAS_EN
    dias_labels = [DIAS_PT[d] for d in dias_opts]
    dc_idx = [dias_opts.index(d) for d in dias_corrida if d in dias_opts]
    dr_idx = [dias_opts.index(d) for d in dias_reforco if d in dias_opts]

    dias_sel = st.multiselect("Dias de Corrida", options=dias_opts, default=dias_corrida,
                               format_func=lambda x: DIAS_PT[x])
    dias_gym = st.multiselect("Dias de Reforço Muscular (Gym/Pernas)", options=dias_opts, default=dias_reforco,
                               format_func=lambda x: DIAS_PT[x])
    dia_longo_n = st.selectbox("Dia do Treino Longo (âncora)", options=dias_opts,
                                index=dias_opts.index(dia_longo) if dia_longo in dias_opts else 6,
                                format_func=lambda x: DIAS_PT[x])

    if st.button("💾 Guardar Configuração"):
        update_user(uid, km_semanais=km_n, pace_medio=round(pace_n,4),
                    dias_corrida=json.dumps(dias_sel),
                    dias_reforco=json.dumps(dias_gym),
                    dia_longo=dia_longo_n)
        st.success("Configuração guardada!"); st.rerun()

    # Visual week preview
    st.markdown("---")
    st.markdown("**Pré-visualização da Semana Tipo**")
    cols = st.columns(7)
    for i, (en, pt) in enumerate(DIAS_PT.items()):
        with cols[i]:
            is_long = en == dia_longo_n
            is_run = en in dias_sel
            is_gym = en in dias_gym
            icons = ""
            if is_long: icons += "🏃"
            elif is_run: icons += "👟"
            if is_gym: icons += "💪"
            if not icons: icons = "😴"
            color = "var(--accent)" if is_long else ("var(--accent2)" if is_gym and not is_run else ("var(--accent3)" if is_run else "var(--muted)"))
            st.markdown(f"""<div style="text-align:center;padding:0.8rem 0.3rem;background:var(--surface);
                border:1px solid var(--border);border-radius:8px;border-top:3px solid {color};">
                <div style="font-size:0.7rem;color:var(--muted);text-transform:uppercase;">{pt[:3]}</div>
                <div style="font-size:1.5rem;margin:0.3rem 0;">{icons}</div>
            </div>""", unsafe_allow_html=True)


def tab_objetivos(user_id):
    st.markdown('<div class="section-title">🎯 Objetivos & Provas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">A → Prova Principal | B → Preparação | C → Teste</div>', unsafe_allow_html=True)

    with st.expander("➕ Adicionar Novo Objetivo", expanded=True):
        with st.form("obj_form"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome da Prova / Desafio")
            data = c2.date_input("Data", min_value=date.today())
            c1, c2, c3 = st.columns(3)
            prio = c1.selectbox("Prioridade", ["A","B","C"])
            dist = c2.number_input("Distância (km)", 5.0, 300.0, 42.0, step=0.5)
            alt = c3.number_input("Altimetria D+ (m)", 0, 20000, 0, step=100)
            tempo = st.text_input("Tempo Alvo (ex: 5h30m)", "")

            if st.form_submit_button("🎯 Registar Objetivo"):
                if nome:
                    add_objetivo(user_id, nome, data.isoformat(), prio, dist, alt, tempo)
                    st.success(f"Objetivo '{nome}' adicionado!"); st.rerun()
                else:
                    st.error("Dá um nome ao objetivo.")

    objs = get_objetivos(user_id)
    if not objs.empty:
        st.markdown("**Histórico de Objetivos**")
        for _, row in objs.iterrows():
            badge_class = f"badge-{row['prioridade'].lower()}"
            d = datetime.strptime(row["data"], "%Y-%m-%d").date()
            days_left = (d - date.today()).days
            status_str = f"🔜 Em {days_left} dias" if days_left > 0 else "✅ Concluído"
            st.markdown(f"""
            <div class="card card-accent" style="margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
                    <div>
                        <span class="{badge_class}">{row['prioridade']}</span>
                        <strong style="margin-left:0.5rem;">{row['nome']}</strong>
                        <span style="color:var(--muted);font-size:0.85rem;margin-left:0.5rem;">{row['data']} · {row['distancia']}km · D+{row['altimetria']}m</span>
                    </div>
                    <div style="color:var(--muted);font-size:0.85rem;">{status_str}</div>
                </div>
                {'<div style="color:var(--accent3);font-size:0.82rem;margin-top:0.3rem;">⏱️ Alvo: ' + row['tempo_alvo'] + '</div>' if row['tempo_alvo'] else ''}
            </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_obj_{row['id']}", help="Apagar"):
                delete_objetivo(row["id"]); st.rerun()
    else:
        st.info("Ainda não tens objetivos registados. Adiciona o teu primeiro acima!")


def tab_registo(user_id):
    st.markdown('<div class="section-title">📝 Registo Diário</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Métricas Garmin e estado físico do dia</div>', unsafe_allow_html=True)

    with st.form("metrica_form"):
        data_reg = st.date_input("Data", value=date.today())
        c1, c2, c3 = st.columns(3)
        hrv = c1.number_input("HRV (ms)", 0, 200, 60)
        rhr = c2.number_input("RHR (bpm)", 30, 100, 52)
        sleep = c3.number_input("Sleep Score", 0, 100, 75)
        c1, c2, c3 = st.columns(3)
        bb = c1.number_input("Body Battery", 0, 100, 70)
        energia = c2.slider("Nível de Energia", 1, 10, 7)
        peso = c3.number_input("Peso Atual (kg)", 40.0, 150.0, 70.0, step=0.1)
        if st.form_submit_button("💾 Registar Métricas"):
            add_metrica(user_id, data_reg.isoformat(), hrv, rhr, sleep, bb, energia, peso)
            st.success("Métricas registadas!"); st.rerun()

    # Charts
    st.markdown("---")
    df = get_metricas(user_id, days=14)
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["data"], y=df["hrv"], name="HRV",
                                      line=dict(color="#e8ff47", width=2.5), fill="tozeroy",
                                      fillcolor="rgba(232,255,71,0.08)"))
            fig.update_layout(title="📈 HRV — 14 dias", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5", family="DM Sans"),
                              xaxis=dict(gridcolor="#252b35", tickangle=-30),
                              yaxis=dict(gridcolor="#252b35"), height=280,
                              margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df["data"], y=df["body_battery"], name="Body Battery",
                                       line=dict(color="#00d4aa", width=2.5), fill="tozeroy",
                                       fillcolor="rgba(0,212,170,0.08)"))
            fig2.update_layout(title="🔋 Body Battery — 14 dias", paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5", family="DM Sans"),
                               xaxis=dict(gridcolor="#252b35", tickangle=-30),
                               yaxis=dict(gridcolor="#252b35", range=[0,100]), height=280,
                               margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Mini summary
        last = df.iloc[-1]
        readiness = (last["hrv"] / 80 * 0.4 + last["body_battery"] / 100 * 0.4 + last["sleep_score"] / 100 * 0.2) * 100
        readiness = min(100, max(0, readiness))
        color = "#00d4aa" if readiness > 70 else ("#e8ff47" if readiness > 50 else "#ff4444")
        emoji = "🟢" if readiness > 70 else ("🟡" if readiness > 50 else "🔴")
        st.markdown(f"""<div class="card" style="border-left:3px solid {color};margin-top:0.5rem;">
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="font-size:2.5rem;">{emoji}</div>
                <div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:{color};">
                        Prontidão: {readiness:.0f}%
                    </div>
                    <div style="color:var(--muted);font-size:0.85rem;">
                        {'✅ Pronto para treino de alta intensidade!' if readiness > 70 else ('⚠️ Treino leve recomendado.' if readiness > 50 else '🛑 Recuperação prioritária hoje.')}
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Começa a registar métricas para veres os teus gráficos de performance aqui.")


def tab_calendario(user_id):
    st.markdown('<div class="section-title">📅 Calendário Inteligente</div>', unsafe_allow_html=True)

    # Get Prova A
    objs = get_objetivos(user_id)
    prova_a = objs[objs["prioridade"] == "A"]

    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        if st.button("🤖 Gerar Plano", use_container_width=True):
            ok, msg = gerar_plano(user_id)
            if ok: st.success(msg)
            else: st.error(msg)
            st.rerun()
    with c2:
        if st.button("⚠️ Não Fiz / Ajustar Semana", use_container_width=True):
            msg = ajustar_semana(user_id)
            st.warning(msg)
    with c3:
        if st.button("🗑️ Limpar Plano", use_container_width=True):
            clear_plano(user_id)
            st.info("Plano limpo."); st.rerun()

    if not prova_a.empty:
        data_prova = prova_a.iloc[0]["data"]
        st.markdown(f"<div style='color:var(--accent);font-size:0.85rem;margin:0.5rem 0;'>🏁 Prova A: <strong>{prova_a.iloc[0]['nome']}</strong> — {data_prova}</div>", unsafe_allow_html=True)

    # Display plan
    plano = get_plano(user_id, date.today().isoformat(),
                      (date.today() + timedelta(days=84)).isoformat())

    if plano.empty:
        st.markdown('<div class="card" style="text-align:center;padding:3rem;">'
                    '<div style="font-size:3rem;">🏗️</div>'
                    '<div style="color:var(--muted);margin-top:1rem;">Nenhum plano gerado. Clica em "Gerar Plano" para começar.</div>'
                    '</div>', unsafe_allow_html=True)
        return

    # Group by week
    plano["data_dt"] = pd.to_datetime(plano["data"])
    plano["semana"] = plano["data_dt"].dt.isocalendar().week
    plano["ano"] = plano["data_dt"].dt.isocalendar().year

    semanas = plano.groupby(["ano","semana"])
    for (ano, sem), grupo in semanas:
        data_ini = grupo["data_dt"].min().strftime("%d/%m")
        data_fim = grupo["data_dt"].max().strftime("%d/%m")
        km_total = grupo["distancia_alvo"].sum()
        n_treinos = len(grupo[grupo["tipo"] != "gym"])

        with st.expander(f"📆 Semana {data_ini} – {data_fim}  |  {km_total:.0f}km  |  {n_treinos} sessões"):
            for _, row in grupo.sort_values("data").iterrows():
                d = pd.to_datetime(row["data"]).date()
                dia_nome = DIAS_PT[DIAS_EN[d.weekday()]]
                status = row["status"]
                border = "var(--accent3)" if status == "Concluído" else ("var(--danger)" if status == "Falhado" else ("var(--accent)" if row["tipo"] == "long" else ("var(--accent2)" if row["tipo"] == "gym" else "var(--border)")))
                opacity = "0.6" if status in ["Concluído","Falhado","Ajustado"] else "1"
                km_str = f" · {row['distancia_alvo']:.1f}km" if row["distancia_alvo"] > 0 else ""

                st.markdown(f"""<div class="day-block" style="border-left:3px solid {border};opacity:{opacity};margin-bottom:0.4rem;">
                    <div class="day-label">{dia_nome} {d.strftime('%d/%m')} &nbsp;<span style="color:{border};">●</span> {status}</div>
                    <div class="day-workout">{row['descricao']}{km_str}</div>
                </div>""", unsafe_allow_html=True)

                if status == "Pendente":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Concluído", key=f"done_{row['id']}", use_container_width=True):
                            mark_treino_done(row["id"]); st.rerun()
                    with col2:
                        if st.button("❌ Falhado", key=f"miss_{row['id']}", use_container_width=True):
                            mark_treino_missed(row["id"]); st.rerun()


def tab_galeria(user_id=None):
    st.markdown('<div class="section-title">📚 Galeria de Conhecimento</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Vídeos e artigos seleccionados pelo teu treinador</div>', unsafe_allow_html=True)

    galeria = get_galeria()
    if galeria.empty:
        st.info("A galeria está vazia. O admin ainda não adicionou conteúdo.")
        return

    videos = galeria[galeria["tipo"] == "Vídeo"]
    artigos = galeria[galeria["tipo"] == "Artigo"]

    if not videos.empty:
        st.markdown("### 🎬 Vídeos")
        cols = st.columns(2)
        for i, (_, row) in enumerate(videos.iterrows()):
            with cols[i % 2]:
                embed = youtube_embed(row["url"])
                if embed:
                    st.markdown(embed, unsafe_allow_html=True)
                st.markdown(f"**{row['titulo']}**")
                st.caption(row["data"])
                st.markdown("---")

    if not artigos.empty:
        st.markdown("### 📰 Artigos & Recursos")
        for _, row in artigos.iterrows():
            st.markdown(f"""<div class="card card-green">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                    <div>
                        <div style="font-weight:600;">{row['titulo']}</div>
                        <div style="color:var(--muted);font-size:0.82rem;">{row['data']}</div>
                    </div>
                    <a href="{row['url']}" target="_blank" style="background:var(--accent3);color:#0a0c0f;padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.85rem;">Ver →</a>
                </div>
            </div>""", unsafe_allow_html=True)


# ─── ADMIN INTERFACE ───────────────────────────────────────────────────────────
def admin_interface():
    st.markdown('<div class="section-title">🛡️ Painel de Administração</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["👥 Utilizadores", "🖼️ Galeria", "👁️ Vista Espelho"])

    with tab1:
        st.markdown("**Criar Novo Atleta**")
        with st.form("create_athlete"):
            c1, c2, c3 = st.columns(3)
            uname = c1.text_input("Username")
            pw = c2.text_input("Password", type="password")
            nome = c3.text_input("Nome")
            if st.form_submit_button("➕ Criar Atleta"):
                if uname and pw and nome:
                    ok = create_athlete(uname, pw, nome)
                    if ok: st.success(f"Atleta '{nome}' criado!")
                    else: st.error("Username já existe.")
                else: st.error("Preenche todos os campos.")

        st.markdown("---")
        st.markdown("**Atletas Registados**")
        athletes = get_all_athletes()
        if not athletes.empty:
            st.dataframe(athletes, use_container_width=True,
                         column_config={"id": "ID", "username": "Username", "nome": "Nome",
                                        "idade": "Idade", "km_semanais": "Vol. Semanal (km)"})
        else:
            st.info("Nenhum atleta registado ainda.")

    with tab2:
        st.markdown("**Adicionar Conteúdo à Galeria**")
        with st.form("galeria_form"):
            titulo = st.text_input("Título")
            tipo = st.selectbox("Tipo", ["Vídeo","Artigo"])
            url = st.text_input("URL (YouTube ou Link)")
            if st.form_submit_button("➕ Adicionar"):
                if titulo and url:
                    add_galeria(titulo, tipo, url)
                    st.success("Conteúdo adicionado!"); st.rerun()

        galeria = get_galeria()
        if not galeria.empty:
            st.markdown("**Conteúdo Atual**")
            for _, row in galeria.iterrows():
                c1, c2 = st.columns([5,1])
                with c1:
                    st.markdown(f"**{row['titulo']}** `{row['tipo']}` — {row['data']}")
                    st.caption(row["url"])
                with c2:
                    if st.button("🗑️", key=f"del_g_{row['id']}"):
                        delete_galeria(row["id"]); st.rerun()

    with tab3:
        athletes = get_all_athletes()
        if athletes.empty:
            st.info("Sem atletas para visualizar.")
        else:
            sel_id = st.selectbox("Selecionar Atleta", athletes["id"].tolist(),
                                   format_func=lambda x: athletes[athletes["id"]==x]["nome"].values[0])
            st.markdown(f"**Modo Espelho: {athletes[athletes['id']==sel_id]['nome'].values[0]}**")
            mirror_user = get_user(sel_id)
            if mirror_user:
                t1, t2, t3, t4 = st.tabs(["📝 Registo", "🎯 Objetivos", "📅 Calendário", "👤 Biometria"])
                with t1: tab_registo(sel_id)
                with t2: tab_objetivos(sel_id)
                with t3: tab_calendario(sel_id)
                with t4: tab_biometria(mirror_user)


# ─── LOGIN ─────────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">ULTRACOACH</div>
        <div class="login-tagline">🏔️ O teu treinador autónomo de ultra trail</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="card" style="padding:2rem;">', unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Introduz o teu username")
        password = st.text_input("🔒 Password", type="password", placeholder="Introduz a tua password")
        if st.button("Entrar →", use_container_width=True):
            user = login_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.user_role = user[3]
                st.session_state.user_name = user[4] or user[1]
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Admin por defeito: `admin` / `admin123`")


# ─── MAIN APP ──────────────────────────────────────────────────────────────────
def main():
    init_db()

    if "user_id" not in st.session_state:
        login_page()
        return

    user_id = st.session_state.user_id
    role = st.session_state.user_role
    user_name = st.session_state.user_name

    render_header(user_name, role)

    # Logout
    col1, col2 = st.columns([10,1])
    with col2:
        if st.button("Sair", key="logout"):
            for k in ["user_id","user_role","user_name"]:
                st.session_state.pop(k, None)
            st.rerun()

    if role == "admin":
        admin_interface()
    else:
        user = get_user(user_id)
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "👤 Biometria", "⚙️ Treino", "🎯 Objetivos",
            "📝 Diário", "📅 Calendário", "📚 Galeria"
        ])
        with tab1: tab_biometria(user)
        with tab2: tab_config(user)
        with tab3: tab_objetivos(user_id)
        with tab4: tab_registo(user_id)
        with tab5: tab_calendario(user_id)
        with tab6: tab_galeria(user_id)

if __name__ == "__main__":
    main()
