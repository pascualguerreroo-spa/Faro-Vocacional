# -*- coding: utf-8 -*-
"""
Faro Vocacional - Demo funcional (Jump Chile 2026)

Los 3 tests (Intereses SJT RIASEC, Micro-DAT MST 2PL/3PL, BFI-10) se responden en pantalla y
alimentan un vector de 17 dimensiones que se compara por Similitud del Coseno contra los
programas REALES de la base SIES 2026 (.xlsx o .csv).

Uso:   pip install streamlit pandas numpy plotly openpyxl
       streamlit run app.py
Deja Oferta_Academica_2026_SIES_05_06_2026_WEB_E.xlsx (o .csv) junto a app.py,
o súbelo desde la barra lateral.
"""
import glob
import html
import inspect
import io
import math
import unicodedata

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# 1. CONSTANTES Y ESTILO
# ----------------------------------------------------------------------------
CYAN, BLUE, AMBER, GREEN, RED = "#12B5CB", "#1A73E8", "#FA903E", "#10B981", "#D93025"
DIMS = ["R", "I", "A", "S", "E", "C", "Gv", "Gkn", "Gf", "Gq", "Gc", "Gs",
        "O", "C_big5", "E_big5", "A_big5", "Estabilidad_Emocional"]
IDX = {d: i for i, d in enumerate(DIMS)}
APT = {"Gv": "Razonamiento Espacial", "Gkn": "Razonamiento Mecánico", "Gf": "Razonamiento Abstracto",
       "Gq": "Razonamiento Numérico", "Gc": "Razonamiento Verbal", "Gs": "Rapidez Perceptiva"}
CORTE_NIVEL2 = 0.43     # theta >= +0.43: tercio superior de N(0,1) -> desbloquea Nivel 2
LAM = 0.30              # peso de la "fuerza prestada" entre aptitudes (MIRT empírico)

CSS = """<style>
.stApp{background:#F8FAFC;font-family:Inter,sans-serif}
.hero-banner{background:linear-gradient(120deg,#0F172A,#1E3A8A);color:#fff;border-radius:14px;padding:1.5rem 1.75rem;margin-bottom:1rem}
.hero-banner h1{color:#fff;margin:.6rem 0 .2rem;font-size:2rem;padding:0}
.hero-banner p{color:#CBD5E1;margin:0}
.badge{background:#FA903E;color:#0F172A;font-weight:700;font-size:.75rem;padding:4px 12px;border-radius:99px}
.career-card{background:#fff;border-radius:12px;box-shadow:0 4px 12px rgba(15,23,42,.06);border-top:4px solid #1A73E8;padding:14px 16px;margin-bottom:12px}
.career-card b{display:block;font-size:.95rem;color:#111}
.career-card small{display:block;color:#575B5F;margin-top:2px}
.pill{display:inline-block;font-size:.72rem;padding:2px 9px;border-radius:99px;background:#E8F0FE;color:#0B57D0;margin:6px 6px 0 0}
.pc{background:#CFF5FA;color:#0E6B78}.pg{background:#D1FAE5;color:#065F46}.pn{background:#EEF1F5;color:#334155}
.af{display:flex;align-items:center;gap:8px;margin:8px 0;font-size:.8rem}
.af div{flex:1;height:8px;background:#E2E8F0;border-radius:4px}.af i{display:block;height:8px;background:#10B981;border-radius:4px}
.alert-box-red,.alert-box-orange,.alert-box-yellow{border-radius:12px;padding:12px 16px;margin-bottom:10px;font-size:.88rem}
.alert-box-red{background:#FDECEA;border:1px solid #F5C2BE;color:#8C1D18}
.alert-box-orange{background:#FFF1E3;border:1px solid #F9C99B;color:#7A3E0A}
.alert-box-yellow{background:#FFF9DB;border:1px solid #F1DE84;color:#6B5200}
</style>"""


def norm(s):
    """Minúsculas, sin tildes, espacios colapsados (para comparar textos y columnas)."""
    s = unicodedata.normalize("NFKD", str(s))
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).lower().split())


def phi(x):
    """Función de distribución normal estándar."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def clp(v):
    return "—" if pd.isna(v) else "$" + f"{v:,.0f}".replace(",", ".")


# ----------------------------------------------------------------------------
# 2. CARGA Y NORMALIZACIÓN DE LA BASE SIES 2026 (.xlsx / .csv)
# ----------------------------------------------------------------------------
# clave interna -> prefijo (normalizado) del encabezado oficial SIES
CANON = {"codigo": "codigo unico", "tipo_inst": "tipo institucion 1", "region": "region sede",
         "comuna": "comuna sede", "area": "area del conocimiento", "generica": "area carrera generica",
         "ies": "nombre ies", "sede": "nombre sede", "carrera": "nombre carrera", "modalidad": "modalidad",
         "jornada": "jornada", "plan": "tipo carrera", "semestres": "duracion estudios",
         "nivel": "nivel carrera", "demre": "demre", "acred": "acreditacion", "beca": "elegibilidad beca",
         "requisito": "requisito ingreso", "matricula": "matricula anual", "arancel": "arancel anual",
         "vigencia": "vigencia"}


def _leer(src, es_csv, header):
    if hasattr(src, "seek"):
        src.seek(0)
    if not es_csv:
        return pd.read_excel(src, header=header)
    for enc in ("utf-8-sig", "latin-1"):
        try:
            if hasattr(src, "seek"):
                src.seek(0)
            return pd.read_csv(src, sep=None, engine="python", encoding=enc, header=header)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo decodificar el CSV")


def _normalizar(df):
    """Mapea columnas SIES -> esquema interno, tipifica y agrega columnas auxiliares."""
    ncols = {norm(c): c for c in df.columns}
    out = pd.DataFrame(index=df.index)
    for k, pref in CANON.items():
        col = next((c for n, c in ncols.items() if n.startswith(pref)), None)
        out[k] = df[col] if col is not None else np.nan
    for c in ["semestres", "demre", "matricula", "arancel"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    for c in ["codigo", "tipo_inst", "region", "comuna", "area", "generica", "ies", "sede", "carrera",
              "modalidad", "jornada", "plan", "nivel", "acred", "beca", "requisito", "vigencia"]:
        out[c] = out[c].fillna("").astype(str).str.strip()
    if (out["vigencia"] == "").all():
        out["vigencia"] = "Vigente con estudiantes nuevos"
    out["_area"] = out["area"].map(norm)
    out["_car"] = (out["carrera"] + " " + out["generica"]).map(norm)
    return out.reset_index(drop=True)


def _fallback():
    """Respaldo mínimo con registros reales del SIES 2026 (Coquimbo / La Serena)."""
    f = [("Universidades", "UNIVERSIDAD DE LA SERENA", "LA SERENA", "LA SERENA", "INGENIERIA CIVIL MECANICA", "Plan Regular", 10, 25002, 226580, 4598000, "Educación Media", "Tecnología"),
         ("Universidades", "UNIVERSIDAD DE LA SERENA", "LA SERENA", "LA SERENA", "INGENIERIA CIVIL EN COMPUTACION E INFORMATICA", "Plan Regular", 10, 25006, 226580, 4598000, "Educación Media", "Tecnología"),
         ("Universidades", "UNIVERSIDAD DE LA SERENA", "LA SERENA", "LA SERENA", "INGENIERIA EN CONSTRUCCION", "Plan Regular", 10, 25010, 226580, 4598000, "Educación Media", "Tecnología"),
         ("Universidades", "UNIVERSIDAD DE LA SERENA", "LA SERENA", "LA SERENA", "INGENIERIA COMERCIAL", "Plan Regular", 10, 25067, 226580, 4596000, "Educación Media", "Administración y Comercio"),
         ("Universidades", "UNIVERSIDAD CATOLICA DEL NORTE", "SEDE COQUIMBO", "COQUIMBO", "INGENIERIA CIVIL EN COMPUTACION E INFORMATICA", "Plan Regular", 10, 18092, 195000, 5940000, "Educación Media", "Tecnología"),
         ("Universidades", "UNIVERSIDAD CENTRAL DE CHILE", "SEDE LA SERENA", "LA SERENA", "INGENIERIA CIVIL INDUSTRIAL", "Plan Regular", 11, 51274, 330000, 4780000, "Educación Media", "Tecnología"),
         ("Institutos Profesionales", "IP AIEP", "SEDE LA SERENA", "LA SERENA", "TECNICO EN ELECTRICIDAD Y ELECTRONICA", "Plan Regular", 5, 0, 240000, 2410000, "Educación Media", "Tecnología"),
         ("Institutos Profesionales", "IP AIEP", "SEDE LA SERENA", "LA SERENA", "TECNICO EN MECANICA AUTOMOTRIZ Y AUTOTRONICA", "Plan Regular", 5, 0, 240000, 2760000, "Educación Media", "Tecnología"),
         ("Institutos Profesionales", "IP AIEP", "SEDE LA SERENA", "LA SERENA", "TECNICO EN CONSTRUCCION", "Plan Regular", 5, 0, 240000, 2400000, "Educación Media", "Tecnología"),
         ("Institutos Profesionales", "IP AIEP", "SEDE LA SERENA", "LA SERENA", "TECNICO EN MINERIA", "Plan Regular", 5, 0, 240000, 2610000, "Educación Media", "Tecnología"),
         ("Institutos Profesionales", "IP SANTO TOMAS", "SEDE LA SERENA", "LA SERENA", "INGENIERIA EN ELECTRICIDAD Y ELECTRONICA INDUSTRIAL", "Plan Regular de Continuidad", 4, 0, 132000, 3383000, "Técnico de Nivel Superior", "Tecnología"),
         ("Institutos Profesionales", "IP SANTO TOMAS", "SEDE LA SERENA", "LA SERENA", "INGENIERIA EN INFORMATICA", "Plan Regular de Continuidad", 4, 0, 132000, 3252000, "Técnico de Nivel Superior", "Tecnología"),
         ("Institutos Profesionales", "IP SANTO TOMAS", "SEDE LA SERENA", "LA SERENA", "INGENIERIA EN ADMINISTRACION DE EMPRESAS", "Plan Regular de Continuidad", 4, 0, 132000, 2776000, "Técnico de Nivel Superior", "Administración y Comercio")]
    d = pd.DataFrame(f, columns=["tipo_inst", "ies", "sede", "comuna", "carrera", "plan", "semestres", "demre",
                                 "matricula", "arancel", "requisito", "area"])
    d["codigo"], d["region"], d["generica"], d["modalidad"], d["jornada"] = "", "Coquimbo", "", "Presencial", ""
    d["nivel"], d["acred"], d["beca"], d["vigencia"] = "", "", "", "Vigente con estudiantes nuevos"
    d["_area"] = d["area"].map(norm)
    d["_car"] = d["carrera"].map(norm)
    return d


@st.cache_data(show_spinner="Cargando oferta académica SIES 2026…")
def cargar_oferta(contenido, nombre):
    """Lee la base subida o la local; tolera filas de título superiores y encabezados desplazados."""
    if contenido is not None:
        src, nm = io.BytesIO(contenido), nombre
    else:
        locales = sorted(glob.glob("Oferta_Academica*.xlsx") + glob.glob("Oferta_Academica*.csv"))
        if not locales:
            return _fallback(), "Respaldo mínimo (13 programas reales del SIES). Sube el archivo para ver toda la oferta."
        src = nm = locales[0]
    es_csv = nm.lower().endswith(".csv")
    df = _leer(src, es_csv, 0)
    if not any(norm(c).startswith("codigo unico") for c in df.columns):
        raw = _leer(src, es_csv, None)
        for i in range(min(15, len(raw))):
            if any(norm(v).startswith("codigo unico") for v in raw.iloc[i].tolist()):
                df = raw.iloc[i + 1:].reset_index(drop=True)
                df.columns = [str(v) for v in raw.iloc[i]]
                break
    return _normalizar(df), nm


# ----------------------------------------------------------------------------
# 3. TEST 1: INTERESES SITUACIONALES (SJT elección forzosa RIASEC)
# ----------------------------------------------------------------------------
# cada situación: opciones en orden R, I, A, S, E, C
SJT = [
    ("En un proyecto escolar libre de fin de semestre, ¿qué rol asumes naturalmente?",
     ["Armo el prototipo con mis manos", "Investigo por qué funciona y pruebo ideas", "Diseño cómo se ve y cómo se cuenta",
      "Organizo al grupo y apoyo a quien se atrasa", "Convenzo a otros y presento el proyecto", "Armo el cronograma y reviso cada detalle"]),
    ("Se echó a perder algo en tu casa. ¿Qué haces primero?",
     ["Lo desarmo y trato de repararlo", "Averiguo cuál es la causa del problema", "Pienso cómo dejarlo más bonito o distinto",
      "Pregunto cómo afecta a quienes lo usan", "Busco quién lo arregle y negocio el precio", "Sigo el manual paso a paso"]),
    ("Hay una feria en tu liceo. ¿Qué te gustaría hacer?",
     ["Montar el escenario y las conexiones", "Preparar un experimento o demostración", "Crear afiches, música o decoración",
      "Recibir y orientar a los visitantes", "Vender y conseguir auspicios", "Llevar la caja y el inventario"]),
    ("En tu tiempo libre en internet, ¿qué te atrapa más?",
     ["Videos de cómo se construyen o arreglan cosas", "Documentales y artículos de ciencia", "Dibujo, música, edición o diseño",
      "Conversar y ayudar en comunidades", "Cómo emprender o ganar dinero", "Ordenar archivos, planillas y listas"]),
    ("Tu curso debe resolver un conflicto. ¿Qué rol tomas?",
     ["Propongo una solución práctica y la ejecuto", "Analizo los hechos antes de opinar", "Propongo una forma creativa de verlo",
      "Escucho a todos y busco que se entiendan", "Lidero la negociación y decido", "Propongo reglas claras y las anoto"]),
    ("Tienes un fin de semana para aprender algo nuevo. ¿Qué eliges?",
     ["Un taller de mecánica o electricidad", "Un curso de programación o ciencia", "Un taller de fotografía, teatro o dibujo",
      "Voluntariado con niños o adultos mayores", "Un taller para armar tu propio negocio", "Un curso de contabilidad y organización"]),
]


def puntaje_riasec(elecciones):
    """elecciones: lista de (más, menos) por situación. Cada 'más' suma +1 y cada 'menos' resta -1 a su
    dimensión (cuasi-ipsativo). Puntaje 0-100 = (suma + n) / (2n) * 100, con n = situaciones completas."""
    suma, n = dict.fromkeys("RIASEC", 0), 0
    for (_, ops), (m, l) in zip(SJT, elecciones):
        if m is not None and l is not None and m != l:
            n += 1
            suma["RIASEC"[ops.index(m)]] += 1
            suma["RIASEC"[ops.index(l)]] -= 1
    return ({d: (suma[d] + n) / (2 * n) * 100 for d in "RIASEC"} if n else None), n


# ----------------------------------------------------------------------------
# 4. TEST 2: MICRO-DAT ESCALONADO (MST 1-2-2, TRI 3PL, EAP)
# ----------------------------------------------------------------------------
PAR_A = [1.3, 1.4, 1.5, 1.5, 1.6]      # discriminación a_i
PAR_B = [-1.2, -0.4, 0.3, 1.0, 1.7]    # dificultad b_i (k=0-2 Nivel 1, k=3-4 Nivel 2)
PAR_C = 0.25                           # adivinación c_i (4 opciones)
CH = "ABCDEFGHJKLMNPRSTUVWXYZ23456789"

ESTATICOS = {
    "Gq": [("Si 3 cuadernos cuestan $2.400, ¿cuánto cuestan 5 cuadernos?", ["$4.000", "$3.600", "$4.800", "$3.200"]),
           ("Un 20% de descuento sobre $15.000 deja un precio final de:", ["$12.000", "$13.000", "$3.000", "$12.500"]),
           ("Una receta para 4 personas usa 3/4 de taza de harina. ¿Cuántas tazas se necesitan para 10 personas?", ["1,875", "1,5", "2,25", "1,25"]),
           ("Un tren recorre 150 km en 1,5 horas. A la misma velocidad, ¿cuánto demora en recorrer 400 km?", ["4 horas", "3,5 horas", "4,5 horas", "5 horas"]),
           ("Un precio sube 25% y luego baja 20%. Respecto del precio original, el precio final es:", ["Igual", "5% mayor", "5% menor", "20% mayor"])],
    "Gc": [("Sinónimo de «veloz»:", ["rápido", "pesado", "tranquilo", "pequeño"]),
           ("Sinónimo de «escaso»:", ["insuficiente", "abundante", "costoso", "antiguo"]),
           ("«Corroborar» significa:", ["confirmar", "ignorar", "aplazar", "modificar"]),
           ("«Efímero» significa:", ["pasajero", "eterno", "frágil", "brillante"]),
           ("«Inexorable» significa:", ["que no se puede evitar", "que no se puede ver", "que no se puede pagar", "que no se puede leer"])],
    "Gf": [("Completa la secuencia:   ▲ ● ■ ▲ ● ?", ["■", "▲", "●", "◆"]),
           ("Completa la secuencia:   ◆ ◆◆ ◆◆◆ ◆◆◆◆ ?", ["◆◆◆◆◆", "◆◆◆◆◆◆", "◆◆◆", "◆◆"]),
           ("Completa la secuencia:   A C E G ?", ["I", "H", "J", "K"]),
           ("Completa la secuencia:   B 2 D 4 F 6 ?", ["H", "G", "8", "I"]),
           ("Completa la secuencia:   Z 1 Y 2 X 4 W 8 ?", ["V", "16", "U", "T"])],
    "Gkn": [("El engranaje A (20 dientes) mueve al B (40 dientes). Si A da 10 vueltas, B da:", ["5 vueltas", "20 vueltas", "10 vueltas", "2 vueltas"]),
            ("Tres engranajes A, B y C en línea se engranan entre sí. Si A gira en sentido horario, C gira en sentido:", ["horario", "antihorario", "alterno", "no gira"]),
            ("Una polea móvil ideal levanta un bloque de 120 kg. La fuerza necesaria es de:", ["60 kg", "120 kg", "240 kg", "30 kg"]),
            ("Un sistema ideal de poleas con 4 tramos de cuerda sosteniendo la carga levanta 200 kg. La fuerza necesaria es de:", ["50 kg", "100 kg", "200 kg", "800 kg"]),
            ("Una palanca tiene una carga de 90 kg a 20 cm del apoyo. ¿Qué fuerza, aplicada a 60 cm del apoyo del otro lado, la equilibra?", ["30 kg", "270 kg", "90 kg", "15 kg"])],
}


def _txt(m):
    return "\n".join("".join("■" if v else "□" for v in fila) for fila in m)


def _lado(figs, letras):
    """Dibuja varias figuras una al lado de la otra (texto monoespaciado)."""
    bloques = [[l] + _txt(f).split("\n") for f, l in zip(figs, letras)]
    alto = max(len(b) for b in bloques)
    ancho = max(len(x) for b in bloques for x in b) + 3
    return "\n".join("".join((b[i] if i < len(b) else "").ljust(ancho) for b in bloques) for i in range(alto))


def _item_rotacion(k):
    """Gv: rotación mental. Correcta = giro 90° horario; distractores = antihorario, espejo y 180°."""
    n, celdas = [3, 3, 4, 4, 5][k], [3, 5, 6, 8, 10][k]
    rng = np.random.default_rng(100 + k)
    while True:
        m = np.zeros(n * n, int)
        m[rng.choice(n * n, celdas, replace=False)] = 1
        m = m.reshape(n, n)
        corr = np.rot90(m, -1)
        cand = [corr, np.rot90(m, 1), np.fliplr(corr), np.rot90(m, 2)]
        if len({x.tobytes() for x in cand}) == 4:
            break
    orden = rng.permutation(4)
    return m, [cand[i] for i in orden], int(np.where(orden == 0)[0][0])


def _item_pares(k):
    """Gs: rapidez/exactitud perceptiva. Contar pares de códigos idénticos."""
    n, rng = [4, 5, 6, 7, 8][k], np.random.default_rng(200 + k)
    pares, iguales = [], 0
    for _ in range(n):
        s = "".join(rng.choice(list(CH), 6))
        if rng.random() < 0.5:
            t, iguales = s, iguales + 1
        else:
            i = int(rng.integers(0, 6))
            t = s[:i] + str(rng.choice([c for c in CH if c != s[i]])) + s[i + 1:]
        pares.append((s, t))
    stim = "\n".join(f"{i + 1:>2}.  {s}    {t}" for i, (s, t) in enumerate(pares))
    pool = sorted(sorted(range(n + 1), key=lambda x: (abs(x - iguales), x))[:4])
    return "¿Cuántos pares de códigos son idénticos? (sin cronómetro en esta demo)", stim, [str(x) for x in pool], pool.index(iguales)


def construir_banco():
    """30 ítems: 6 aptitudes x 5. k=0,1,2 forman el Nivel 1 (enrutamiento); k=3,4 el Nivel 2."""
    banco = []
    for apt in APT:
        for k in range(5):
            stim = ""
            if apt == "Gv":
                m, figs, ans = _item_rotacion(k)
                letras = ["A", "B", "C", "D"]
                q, opts = "¿Cuál figura resulta al girar la original 90° hacia la derecha (sentido horario)?", letras
                stim = "Original:\n" + _txt(m) + "\n\nOpciones:\n" + _lado(figs, letras)
            elif apt == "Gs":
                q, stim, opts, ans = _item_pares(k)
            else:
                q, lista = ESTATICOS[apt][k]
                orden = np.random.default_rng(300 + k + 7 * len(apt)).permutation(4)
                opts, ans = [lista[i] for i in orden], int(np.where(orden == 0)[0][0])
            banco.append(dict(id=f"{apt}{k}", apt=apt, k=k, nivel=1 if k < 3 else 2, a=PAR_A[k], b=PAR_B[k],
                              c=PAR_C, q=q, stim=stim, opts=opts, ans=ans))
    return banco


BANCO = construir_banco()
POR_ID = {it["id"]: it for it in BANCO}


def p_3pl(theta, a, b, c):
    """Curva característica del ítem 3PL: P(theta) = c + (1 - c) / (1 + exp(-a (theta - b)))."""
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))


def info_fisher(theta, a, b, c):
    """Información de Fisher 3PL: a² (P - c)² / ((1 - c)² P (1 - P))."""
    p = p_3pl(theta, a, b, c)
    return a ** 2 * (p - c) ** 2 / ((1 - c) ** 2 * p * (1 - p))


def eap(par, mu=0.0, sd=1.0):
    """Estimador bayesiano EAP sobre una grilla de cuadratura. par = [(a, b, c, acierto)]. Retorna (theta, EE)."""
    g = np.linspace(-4, 4, 161)
    logp = -0.5 * ((g - mu) / sd) ** 2
    for a, b, c, ok in par:
        p = p_3pl(g, a, b, c)
        logp = logp + np.log(p if ok else 1 - p)
    w = np.exp(logp - logp.max())
    w /= w.sum()
    th = float((w * g).sum())
    return th, float(np.sqrt((w * (g - th) ** 2).sum()))


def thetas_mirt(resp):
    """Habilidad latente por aptitud, tomando fuerza estadística de las demás: el a priori de cada aptitud
    es N(LAM * theta_g(otras aptitudes), 1 - LAM²), con theta_g estimado con los ítems de las otras cinco."""
    def par(it):
        return it["a"], it["b"], it["c"], resp[it["id"]]
    out = {}
    for apt in APT:
        propios = [par(it) for it in BANCO if it["apt"] == apt and it["id"] in resp]
        if not propios:
            out[apt] = None
            continue
        otros = [par(it) for it in BANCO if it["apt"] != apt and it["id"] in resp]
        g = eap(otros)[0] if otros else 0.0
        out[apt] = eap(propios, LAM * g, math.sqrt(1 - LAM ** 2))
    return out


# ----------------------------------------------------------------------------
# 5. TEST 3: PERSONALIDAD BFI-10 (Rammstedt y John, 2007)
# ----------------------------------------------------------------------------
# (n, rasgo, texto, inverso)
BFI = [(1, "E", "Es reservado/a", True), (2, "A", "Generalmente confía en los demás", False),
       (3, "C", "Tiende a ser desorganizado/a o postergar tareas", True),
       (4, "N", "Es relajado/a, maneja bien el estrés", True),
       (5, "O", "Tiene pocos intereses artísticos o abstractos", True),
       (6, "E", "Es extrovertido/a, sociable", False), (7, "A", "Tiende a encontrar defectos en los demás", True),
       (8, "C", "Hace las cosas de manera eficiente y planificada", False),
       (9, "N", "Se pone nervioso/a o ansioso/a con facilidad ante evaluaciones", False),
       (10, "O", "Tiene una imaginación activa y curiosidad intelectual", False)]


def bfi_percentiles(resp):
    """Invierte 1R,3R,4R,5R,7R con (6 - valor), promedia los 2 ítems del rasgo y lo lleva a percentil 0-100
    con un baremo provisional normal (media 3.0, DE 0.9; no hay normas chilenas publicadas)."""
    out = {}
    for rasgo in "EACNO":
        v = [(6 - resp[n] if rev else resp[n]) for n, r, _, rev in BFI if r == rasgo and resp.get(n) is not None]
        out[rasgo] = phi((float(np.mean(v)) - 3.0) / 0.9) * 100 if len(v) == 2 else None
    return out


def alertas(p):
    """Triaje socioemocional con las 3 reglas validadas."""
    if any(p[r] is None for r in "EACNO"):
        return []
    a = []
    if p["C"] > 75 and p["N"] > 65:
        a.append(("red", "Alerta Roja · Burnout Perfeccionista", "Responsabilidad > P75 y Neuroticismo > P65: +40% de riesgo de burnout clínico (β = 0.418). Sugerencia: contención de ansiedad pre-PAES y flexibilizar la visión de túnel."))
    if p["C"] < 25 and p["N"] > 65:
        a.append(("orange", "Alerta Naranja · Desvinculación por Procrastinación", "Responsabilidad < P25 y Neuroticismo > P65: riesgo de abandono en el 1.er semestre (β indirecto = −0.13). Sugerencia: hábitos de estudio y metas semanales."))
    if p["E"] < 25 and p["A"] < 25:
        a.append(("yellow", "Alerta Amarilla · Aislamiento Transicional", "Extraversión < P25 y Amabilidad < P25: riesgo de despersonalización en la transición terciaria. Sugerencia: acompañamiento para integración social."))
    return a


# ----------------------------------------------------------------------------
# 6. MOTOR DE RECOMENDACIÓN: vector de 17 dimensiones + Similitud del Coseno
# ----------------------------------------------------------------------------
def _vec(d):
    v = np.full(17, 40.0)
    for k, x in d.items():
        v[IDX[k]] = x
    return v


# Complejos de rasgos de Ackerman y Heggestad (1997): vector de requerimientos B (0-100)
COMPLEJOS = {
    "stem": _vec({"R": 90, "I": 80, "Gv": 85, "Gkn": 85, "Gf": 80, "Gq": 80, "C_big5": 65, "Estabilidad_Emocional": 55}),
    "cultural": _vec({"A": 90, "I": 75, "Gc": 80, "Gv": 70, "Gf": 65, "O": 90}),
    "social": _vec({"S": 90, "E": 70, "Gc": 70, "E_big5": 75, "A_big5": 85, "C_big5": 70, "Estabilidad_Emocional": 65}),
    "conv": _vec({"C": 90, "E": 65, "Gq": 80, "Gs": 80, "C_big5": 85}),
}
# Orden de prioridad: Ingeniería Comercial es convencional, Pedagogía en Matemática es social, etc.
REGLAS = [("conv", ["administracion", "comercial", "contador", "contabil", "auditor", "finanzas", "secretar", "logistica", "negocios", "gestion"]),
          ("social", ["pedagog", "educacion", "enfermer", "psicolog", "kinesi", "medicina", "odontolog", "nutricion", "fonoaud", "obstetric", "terapia", "trabajo social", "parvul", "farmac"]),
          ("stem", ["ingenier", "informat", "computac", "mecanic", "electric", "electron", "construc", "minas", "mineri", "geolog", "industrial", "matematic", "fisica", "quimica", "automotriz", "mantencion", "programacion", "telecomunic", "geomensura", "agricol", "civil"]),
          ("cultural", ["arte", "diseno", "arquitect", "periodis", "literatur", "historia", "filosof", "musica", "comunicac", "cine", "traduc", "derecho", "humanidad", "publicidad", "antropolog"])]
AREAS = [("stem", ["tecnolog", "ciencias basicas", "agropecuar"]), ("cultural", ["arte", "humanidad", "derecho"]),
         ("social", ["salud", "educacion", "ciencias sociales"]), ("conv", ["administracion"])]


# Matices dentro del complejo Ciencia/Ingeniería: separan mecánica/electricidad, informática y construcción
AJUSTES = [(["mecanic", "electric", "electron", "automotriz", "mantencion", "mineri", "minas", "industrial"], {"Gkn": 8, "R": 5}),
           (["informat", "computac", "programacion", "telecomunic"], {"Gf": 8, "Gq": 6, "R": -12}),
           (["construc", "civil", "topograf", "geomensura"], {"Gv": 8, "Gkn": -3})]


def vector_carrera(area, carrera):
    """Asigna el complejo de rasgos por palabras clave de la carrera y, si no calza, por el área SIES."""
    for comp, kws in REGLAS:
        if any(k in carrera for k in kws):
            v = COMPLEJOS[comp].copy()
            if comp == "stem":
                for kw, adj in AJUSTES:
                    if any(k in carrera for k in kw):
                        for dim, x in adj.items():
                            v[IDX[dim]] = min(100.0, v[IDX[dim]] + x)
            return v
    for comp, kws in AREAS:
        if any(k in area for k in kws):
            return COMPLEJOS[comp]
    return np.full(17, 50.0)   # sin información: neutro


def matriz_requerimientos(d):
    cache, out = {}, np.empty((len(d), 17))
    for i, k in enumerate(zip(d["_area"], d["_car"])):
        if k not in cache:
            cache[k] = vector_carrera(*k)
        out[i] = cache[k]
    return out


def coseno(A, B):
    """Similitud del Coseno = A·B / (||A|| ||B||). Los vectores se centran en 50 (punto neutro) y se escalan
    a [-1, 1]; así una dimensión sin información (50) no sesga y la similitud discrimina entre carreras."""
    a, b = (np.asarray(A, float) - 50) / 50, (np.asarray(B, float) - 50) / 50
    num, den = b @ a, np.linalg.norm(b, axis=1) * np.linalg.norm(a)
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


def vector_estudiante(riasec, thetas, bfi):
    """Vector A de 17 dimensiones (0-100). Lo no evaluado queda en 50 (neutro)."""
    v = np.full(17, 50.0)
    if riasec:
        v[0:6] = [riasec[d] for d in "RIASEC"]
    for apt, t in thetas.items():
        if t is not None:
            v[IDX[apt]] = phi(t[0]) * 100            # percentil de la habilidad latente
    for rasgo, dim in [("O", "O"), ("C", "C_big5"), ("E", "E_big5"), ("A", "A_big5")]:
        if bfi[rasgo] is not None:
            v[IDX[dim]] = bfi[rasgo]
    if bfi["N"] is not None:
        v[IDX["Estabilidad_Emocional"]] = 100 - bfi["N"]
    return v


def carriles(d):
    """3 carriles: universitario (Plan Regular con DEMRE), técnico-profesional de admisión directa
    (DEMRE = 0, sin barrera PAES) y ruta de articulación (Plan Regular de Continuidad desde TNS)."""
    plan, req = d["plan"].map(norm), d["requisito"].map(norm)
    univ = d["tipo_inst"].map(norm).str.startswith("universidad")
    reg, em = plan.eq("plan regular"), req.str.contains("educacion media")
    demre = d["demre"].fillna(0)
    sel = [d[univ & reg & em & (demre > 0)], d[~univ & reg & em & (demre == 0)],
           d[plan.str.contains("continuidad") & req.str.contains("tecnico")]]
    return [x.sort_values("afinidad", ascending=False).drop_duplicates(["ies", "sede", "carrera"]).head(5) for x in sel]


# ----------------------------------------------------------------------------
# 7. INTERFAZ
# ----------------------------------------------------------------------------
def grafico(etq, vals, colores, alto=300):
    fig = go.Figure(go.Bar(x=vals, y=etq, orientation="h", marker_color=colores,
                           text=[f"{v:.0f}" for v in vals], textposition="outside"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=alto,
                      font=dict(family="Inter, sans-serif", color="#111"), margin=dict(l=10, r=10, t=30, b=10),
                      xaxis=dict(range=[0, 112], showgrid=False), yaxis=dict(autorange="reversed"))
    ancho = {"width": "stretch"} if "width" in inspect.signature(st.plotly_chart).parameters else {"use_container_width": True}
    st.plotly_chart(fig, **ancho)


def tarjeta(r, color):
    dem = "Admisión directa" if (pd.isna(r.demre) or r.demre == 0) else f"DEMRE {int(r.demre)}"
    sem = "—" if pd.isna(r.semestres) else int(r.semestres)
    e = html.escape
    return (f'<div class="career-card" style="border-top-color:{color}"><b>{e(r.carrera.title())}</b>'
            f'<small>{e(r.ies.title())} · {e(r.sede.title())}</small>'
            f'<div><span class="pill">{e(r.tipo_inst)}</span><span class="pill pc">{e(r.modalidad or "—")}</span>'
            f'<span class="pill {"pg" if dem.startswith("Adm") else "pn"}">{dem}</span></div>'
            f'<div class="af"><span>Afinidad {r.afinidad:.0f}%</span><div><i style="width:{r.afinidad:.0f}%"></i></div></div>'
            f'<small>Arancel anual {clp(r.arancel)} · Matrícula {clp(r.matricula)} · {sem} sem</small></div>')


def render_item(it):
    st.markdown(f"**{it['q']}**")
    if it["stim"]:
        st.code(it["stim"], language=None)
    st.radio("Respuesta", it["opts"], index=None, key="dat_" + it["id"], horizontal=True, label_visibility="collapsed")


def main():
    st.set_page_config(page_title="Faro Vocacional", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="hero-banner"><span class="badge">MVP Demo - Jump Chile 2026</span><h1>Faro Vocacional</h1>'
                '<p>Responde los 3 tests y recibe trayectorias reales de la oferta SIES 2026</p></div>', unsafe_allow_html=True)

    # --- barra lateral: base de datos y filtros
    sb = st.sidebar
    sb.header("Base SIES 2026")
    up = sb.file_uploader("Sube el .xlsx o .csv oficial", type=["xlsx", "csv"])
    df, origen = cargar_oferta(up.getvalue() if up else None, up.name if up else None)
    sb.caption(f"{origen} · {len(df):,} programas".replace(",", "."))
    sb.header("Filtros")
    reg = sb.selectbox("Región", ["Todas"] + sorted(x for x in df["region"].unique() if x))
    tipos = sorted(x for x in df["tipo_inst"].unique() if x)
    tipo = sb.multiselect("Tipo de institución", tipos, default=tipos)
    mods = sorted(x for x in df["modalidad"].unique() if x)
    mod = sb.multiselect("Modalidad", mods, default=mods)
    tope = max(int(df["arancel"].max() or 0), 1_000_000)
    max_ar = sb.slider("Arancel anual máximo", 0, tope, tope, step=100_000)
    solo_vig = sb.checkbox("Solo vigentes con estudiantes nuevos", True)
    solo_acr = sb.checkbox("Solo carreras acreditadas", False)
    if sb.button("Reiniciar los 3 tests"):
        for k in [k for k in st.session_state if str(k).startswith(("sjt_", "dat_", "bfi_"))]:
            del st.session_state[k]
        st.rerun()

    t1, t2, t3, t4 = st.tabs(["1 · Intereses (RIASEC)", "2 · Micro-DAT", "3 · Personalidad (BFI-10)", "4 · Resultados"])

    # --- Test 1
    with t1:
        st.caption("Elige lo que MÁS y lo que MENOS te representa en cada situación (formato de elección forzosa).")
        elec = []
        for i, (preg, ops) in enumerate(SJT):
            st.markdown(f"**{i + 1}. {preg}**")
            c1, c2 = st.columns(2)
            m = c1.selectbox("Más me representa", ops, index=None, key=f"sjt_m{i}")
            l = c2.selectbox("Menos me representa", ops, index=None, key=f"sjt_l{i}")
            if m is not None and m == l:
                st.warning("Elige opciones distintas para «más» y «menos».")
            elec.append((m, l))
        riasec, n_sjt = puntaje_riasec(elec)
        if riasec:
            st.progress(n_sjt / len(SJT), text=f"{n_sjt} de {len(SJT)} situaciones completas")
            grafico(["Realista", "Investigativo", "Artístico", "Social", "Emprendedor", "Convencional"],
                    [riasec[d] for d in "RIASEC"], [CYAN] * 6)

    # --- Test 2 (MST 1-2-2)
    resp = {}
    for it in BANCO:
        v = st.session_state.get("dat_" + it["id"])
        if v is not None:
            resp[it["id"]] = (v == it["opts"][it["ans"]])
    th1 = thetas_mirt({i: ok for i, ok in resp.items() if POR_ID[i]["nivel"] == 1})   # módulo de enrutamiento
    desbloqueadas = [a for a in APT if th1[a] is not None and th1[a][0] >= CORTE_NIVEL2
                     and all(f"{a}{k}" in resp for k in range(3))]
    with t2:
        st.caption("Nivel 1: 3 retos por aptitud. Si tu habilidad estimada (θ̂) llega a +0.43, se desbloquea el Nivel 2 en esa aptitud.")
        for apt, nombre in APT.items():
            with st.expander(f"{nombre} ({apt})", expanded=(apt == "Gv")):
                for it in [x for x in BANCO if x["apt"] == apt and x["nivel"] == 1]:
                    render_item(it)
                if apt in desbloqueadas:
                    st.success("¡Talento Latente Detectado! Has desbloqueado el Nivel 2 de Confirmación Avanzada.")
                    for it in [x for x in BANCO if x["apt"] == apt and x["nivel"] == 2]:
                        render_item(it)
        st.progress(len(resp) / max(1, len(BANCO)), text=f"{len(resp)} ítems respondidos (máx. 30)")
    thetas = thetas_mirt(resp)
    with t2:
        filas = []
        for apt, nombre in APT.items():
            t = thetas[apt]
            if t is None:
                continue
            its = [POR_ID[i] for i in resp if POR_ID[i]["apt"] == apt]
            info = sum(info_fisher(t[0], x["a"], x["b"], x["c"]) for x in its)
            filas.append({"Aptitud": nombre, "Aciertos": f"{sum(resp[x['id']] for x in its)}/{len(its)}",
                          "θ̂": round(t[0], 2), "EE": round(t[1], 2), "Percentil": round(phi(t[0]) * 100),
                          "Info. Fisher": round(float(info), 2), "Nivel 2": "Desbloqueado" if apt in desbloqueadas else "—"})
        if filas:
            st.dataframe(pd.DataFrame(filas), hide_index=True)

    # --- Test 3
    with t3:
        st.caption("1 = Muy en desacuerdo … 5 = Muy de acuerdo. Me veo como alguien que…")
        for n, _, texto, _ in BFI:
            st.radio(f"{n}. {texto}", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"bfi_{n}")
    bresp = {n: st.session_state.get(f"bfi_{n}") for n, *_ in BFI}
    bfi = bfi_percentiles(bresp)
    with t3:
        if all(bfi[r] is not None for r in "EACNO"):
            nombres = {"E": "Extraversión", "A": "Amabilidad", "C": "Responsabilidad", "N": "Neuroticismo", "O": "Apertura"}
            grafico([nombres[r] for r in "EACNO"], [bfi[r] for r in "EACNO"], [AMBER] * 5, 260)
            st.caption("Percentiles aproximados con baremo provisional.")
        else:
            st.info("Responde los 10 ítems para ver tu perfil.")

    # --- Resultados
    with t4:
        hechos = [("Intereses", n_sjt == len(SJT)), ("Micro-DAT", len(resp) >= 18), ("BFI-10", all(bfi[r] is not None for r in "EACNO"))]
        st.write(" · ".join(("✅ " if ok else "⬜ ") + n for n, ok in hechos))
        if not (riasec or resp or any(bfi[r] is not None for r in "EACNO")):
            st.warning("Completa al menos un test para generar recomendaciones.")
            return
        if not all(ok for _, ok in hechos):
            st.caption("Resultado parcial: las dimensiones sin evaluar se tratan como neutras (50).")
        A = vector_estudiante(riasec, thetas, bfi)
        st.subheader("Tu vector de 17 dimensiones")
        col = [CYAN] * 6 + [BLUE] * 6 + [AMBER] * 5
        grafico(DIMS, list(A), col, 520)
        for c, t, x in alertas(bfi):
            st.markdown(f'<div class="alert-box-{c}"><b>{t}</b><br>{x}</div>', unsafe_allow_html=True)

        d = df.copy()
        if solo_vig:
            d = d[d["vigencia"].map(norm).str.contains("con estudiante")]
        if reg != "Todas":
            d = d[d["region"] == reg]
        d = d[d["tipo_inst"].isin(tipo) & d["modalidad"].isin(mod) & (d["arancel"].fillna(0) <= max_ar)]
        if solo_acr:
            d = d[d["acred"].map(norm) == "acreditada"]
        if d.empty:
            st.warning("Ningún programa cumple los filtros.")
            return
        d = d.copy()
        d["afinidad"] = (coseno(A, matriz_requerimientos(d)) + 1) / 2 * 100   # cos θ ∈ [-1,1] -> 0-100%
        st.subheader("Trayectorias recomendadas")
        st.caption(f"{len(d):,} programas evaluados con Similitud del Coseno.".replace(",", "."))
        titulos = ["Carril 1 · Universidades de alto ajuste", "Carril 2 · CFT/IP de admisión directa (sin PAES)",
                   "Carril 3 · Ruta de articulación (Continuidad desde TNS)"]
        top = carriles(d)
        for c, t, x, color in zip(st.columns(3), titulos, top, [BLUE, CYAN, AMBER]):
            with c:
                st.markdown(f"**{t}**")
                if x.empty:
                    st.info("Sin programas con estos filtros.")
                else:
                    st.markdown("".join(tarjeta(r, color) for r in x.itertuples()), unsafe_allow_html=True)
        rep = pd.concat([x.assign(carril=i + 1) for i, x in enumerate(top)])
        if not rep.empty:
            cols = ["carril", "afinidad", "ies", "sede", "carrera", "plan", "modalidad", "demre", "semestres", "matricula", "arancel"]
            st.download_button("Descargar recomendaciones (CSV)", rep[cols].round(1).to_csv(index=False).encode("utf-8-sig"),
                               "recomendaciones_faro.csv", "text/csv")


if __name__ == "__main__":
    main()
