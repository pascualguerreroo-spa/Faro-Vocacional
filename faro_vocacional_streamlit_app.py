import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Faro Vocacional - Orientación Vocacional Adaptativa",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados con la paleta de Faro Vocacional
st.markdown("""
<style>
    /* Paleta de colores: Terracota #C85A32, Verde Botánico #2D5A42, Pergamino #FBF8F3 */
    .main {
        background-color: #FBF8F3;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #FBF8F3;
    }
    .header-title {
        color: #C85A32;
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .header-subtitle {
        color: #2D5A42;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 1.8rem;
        font-weight: 600;
    }
    .match-card {
        background-color: #2D5A42;
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(45, 90, 66, 0.15);
    }
    .badge-gratuidad {
        background-color: #2D5A42;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-top: 6px;
    }
    .card-carrera {
        background-color: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .stButton>button {
        background-color: #C85A32 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.6rem 1.2rem !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de estado de sesión
if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'usuario' not in st.session_state:
    st.session_state.usuario = {}

# Barra lateral para navegación y Dashboard B2B
st.sidebar.title("🧭 Faro Vocacional")
st.sidebar.caption("Orientación Vocacional Adaptativa")

modo_vista = st.sidebar.radio("Vista de la Plataforma:", ["Estudiante (Experiencia)", "Orientador / Liceo (Dashboard B2B)"])

if modo_vista == "Estudiante (Experiencia)":
    
    # Barra de progreso del estudiante
    pasos_titulos = ["1. Registro", "1.5. Expectativa", "1.8. FODA Exprès", "2. Charla IA", "3. Desafíos", "4. Match Real"]
    progreso_val = min(1.0, (st.session_state.paso) / 6.0)
    st.progress(progreso_val)
    st.caption(f"Paso {st.session_state.paso} de 6: {pasos_titulos[min(st.session_state.paso - 1, 5)]}")

    # HEADER PRINCIPAL
    st.markdown('<div class="header-title">Faro Vocacional</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Descubre tu verdadero talento sin visión de túnel</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # PASO 1: REGISTRO LIVIANO
    # ---------------------------------------------------------
    if st.session_state.paso == 1:
        st.subheader("📋 Paso 1: Registro Liviano de Estudiante")
        st.write("Ingresa tus datos básicos para crear tu perfil único de orientación.")
        
        with st.form("form_paso1"):
            nombre = st.text_input("Nombre Completo o Alias:", placeholder="Ej: Valentina Morales")
            email = st.text_input("Correo Electrónico:", placeholder="ejemplo@liceo.cl")
            nem = st.number_input("NEM Aproximado (Promedio de Notas 1° a 3° Medio):", min_value=4.0, max_value=7.0, value=5.8, step=0.1)
            tipo_liceo = st.selectbox("Tipo de Establecimiento:", ["Humanista-Científico (HC)", "Técnico-Profesional (TP)"])
            
            submitted = st.form_submit_button("Siguiente: Elegir Carrera Pensada ➔")
            if submitted:
                if nombre and email:
                    st.session_state.usuario['nombre'] = nombre
                    st.session_state.usuario['email'] = email
                    st.session_state.usuario['nem'] = nem
                    st.session_state.usuario['tipo_liceo'] = tipo_liceo
                    st.session_state.paso = 2
                    st.rerun()
                else:
                    st.warning("Por favor completa tu nombre y correo para continuar.")

    # ---------------------------------------------------------
    # PASO 1.5: EXPECTATIVA INICIAL (LÍNEA BASE)
    # ---------------------------------------------------------
    elif st.session_state.paso == 2:
        st.subheader("🎯 Paso 1.5: Expectativa Inicial")
        st.write(f"¡Hola **{st.session_state.usuario.get('nombre', '')}**! ¿Tienes alguna carrera o área en mente que estés considerando hoy?")
        
        carreras_catalogo = [
            "Ingeniería Civil Informática (Universidad)",
            "Técnico en Programación y Análisis (IP/CFT)",
            "Enfermería (Universidad)",
            "Técnico en Enfermería / TENS (IP/CFT)",
            "Diseño Digital y Multimedia (IP/U)",
            "Ingeniería en Electricidad y Automatización (IP/CFT)",
            "Psicología (Universidad)",
            "Técnico en Gastronomía Internacional (IP/CFT)",
            "Aún no lo tengo claro / Quiero descubrirlo desde cero (Indeciso)"
        ]
        
        expectativa = st.selectbox("Busca o selecciona la carrera que tienes en mente:", carreras_catalogo)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver"):
                st.session_state.paso = 1
                st.rerun()
        with col2:
            if st.button("Siguiente: Tu FODA Exprès ➔"):
                st.session_state.usuario['expectativa_inicial'] = expectativa
                st.session_state.paso = 3
                st.rerun()

    # ---------------------------------------------------------
    # PASO 1.8: FODA PERSONAL EXPRÈS
    # ---------------------------------------------------------
    elif st.session_state.paso == 3:
        st.subheader("⚡ Paso 1.8: Tu FODA Personal Exprès")
        st.write("Selecciona los atributos que mejor te describen hoy para ayudar a la IA a conocer tus fortalezas y desafíos:")
        
        col_f, col_d = st.columns(2)
        with col_f:
            st.markdown("🟢 **Fortalezas (Tus Superpoderes)**")
            fortalezas = st.multiselect(
                "¿En qué te destacas?",
                ["Me concentro fácil cuando algo me interesa", "Paciencia para escuchar y explicar", 
                 "Ordenado/a con mis tiempos", "Habilidad para armar o reparar cosas",
                 "Expreso bien mis ideas hablando o escribiendo", "Curioso/a para investigar por mi cuenta"]
            )
        
        with col_d:
            st.markdown("🟡 **Debilidades (Tus Puntos Ciegos)**")
            debilidades = st.multiselect(
                "¿Qué te cuesta hoy?",
                ["Me cuesta organizarme a tiempo", "Me frustran las matemáticas/cálculos",
                 "Me aburro si estoy sentado leyendo mucho", "Ansiedad para hablar en público",
                 "Me distraigo rápido en tareas largas"]
            )
            
        col_o, col_a = st.columns(2)
        with col_o:
            st.markdown("🔵 **Oportunidades (Tus Apoyos)**")
            oportunidades = st.multiselect(
                "¿Con qué cuentas en tu entorno?",
                ["Mi familia me apoya en lo que elija", "Puedo postular a Gratuidad / FUAS",
                 "Tengo computador e internet en casa", "Conozco gente trabajando en el área"]
            )
            
        with col_a:
            st.markdown("🔴 **Amenazas (Tus Barreras)**")
            amenazas = st.multiselect(
                "¿Qué te preocupa del afuera?",
                ["La carrera no está en mi ciudad/comuna", "Tengo que trabajar saliendo de 4° medio",
                 "Temor a que el NEM o PAES no alcance", "Miedo a endeudarme"]
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver"):
                st.session_state.paso = 2
                st.rerun()
        with col2:
            if st.button("Siguiente: Charla con la IA ➔"):
                st.session_state.usuario['fortalezas'] = fortalezas
                st.session_state.usuario['debilidades'] = debilidades
                st.session_state.usuario['oportunidades'] = oportunidades
                st.session_state.usuario['amenazas'] = amenazas
                st.session_state.paso = 4
                st.rerun()

    # ---------------------------------------------------------
    # PASO 2: CHARLA CONVERSACIONAL CON LA IA (SIMULADOR)
    # ---------------------------------------------------------
    elif st.session_state.paso == 4:
        st.subheader("🤖 Paso 2: Orientador Virtual (IA Socrática)")
        
        nombre = st.session_state.usuario.get('nombre', 'Estudiante')
        expectativa = st.session_state.usuario.get('expectativa_inicial', 'la carrera que elegiste')
        forts = ", ".join(st.session_state.usuario.get('fortalezas', ['tus talentos'])) if st.session_state.usuario.get('fortalezas') else "tus habilidades"
        
        st.info(f"💬 **Orientador Faro Vocacional:**\n\n"
                f"¡Hola {nombre}! Veo que cursas en un liceo {st.session_state.usuario.get('tipo_liceo')} con un NEM aproximado de {st.session_state.usuario.get('nem')}.\n\n"
                f"Analizando tu FODA, veo que cuentas con fortalezas clave como: *{forts}*. Y hoy estás considerando: **{expectativa}**.\n\n"
                f"Cuéntame: ¿Qué proyecto o actividad práctica te imaginas realizando en tu futuro trabajo que te haga sentir motivado/a?")
        
        respuesta_alumno = st.text_area("Tu respuesta para el orientador:", placeholder="Ej: Me gustaría crear aplicaciones o trabajar resolviendo problemas prácticos con tecnología...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver"):
                st.session_state.paso = 3
                st.rerun()
        with col2:
            if st.button("Siguiente: Desafíos Cognitivos ➔"):
                if respuesta_alumno:
                    st.session_state.usuario['relato_ia'] = respuesta_alumno
                st.session_state.paso = 5
                st.rerun()

    # ---------------------------------------------------------
    # PASO 3: PSICOMETRÍA Y DESAFÍOS COGNITIVOS
    # ---------------------------------------------------------
    elif st.session_state.paso == 5:
        st.subheader("🎮 Paso 3: Desafíos Cognitivos y Situaciones Cotidianas")
        st.write("Responde estas breves situaciones prácticas para calibrar tu verdadero perfil vocacional:")
        
        p1 = st.radio(
            "1. Si se corta la luz en tu casa o colegio, ¿cuál es tu reacción instintiva?",
            ["Buscar la caja de fusibles o linternas para revisar qué falló (Técnico/Práctico)",
             "Organizar al grupo para mantener la calma y comunicarse (Docencia/Resolución)",
             "Aprovechar de imaginar historias o crear juegos a oscuras (Creativo/Comunicación)",
             "Analizar lógicamente cuánto tiempo durará según la zona (Lógico/Numérico)"]
        )
        
        p2 = st.radio(
            "2. Desafío Espacial Rápido: Si giras una figura L 90° a la derecha y luego la inviertes horizontalmente, ¿qué patrón obtienes?",
            ["Patrón A (Correcto)", "Patrón B", "Patrón C"]
        )
        
        p3 = st.radio(
            "3. Desafío Secuencial: En la serie 2, 4, 8, 16, 32... ¿cuál es el número siguiente?",
            ["64 (Correcto)", "48", "128"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Volver"):
                st.session_state.paso = 4
                st.rerun()
        with col2:
            if st.button("🎉 Generar Mi Match y Resultados ➔"):
                st.session_state.usuario['p1'] = p1
                st.session_state.usuario['p2'] = p2
                st.session_state.usuario['p3'] = p3
                st.session_state.paso = 6
                st.rerun()

    # ---------------------------------------------------------
    # PASO 4: PANTALLA DE RESULTADOS (EL MATCH REAL)
    # ---------------------------------------------------------
    elif st.session_state.paso == 6:
        st.balloons()
        st.subheader("🌟 Tus Resultados y Match Vocacional")
        
        # Tarjeta de Match Principal
        st.markdown("""
        <div class="match-card">
            <h2>¡Tu Talento Dominante es: LÓGICO / TÉCNICO!</h2>
            <p style="font-size: 1.2rem; margin-top: 0.5rem;">Tienes un <b>92% de Afinidad</b> con carreras del área de Tecnología, Automatización y Computación.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de Fortalezas (7 Categorías)
        st.markdown("### 📊 Desglose de tus 7 Categorías Vocacionales")
        data_cat = {
            "Categoría": ["Lógico / Numérico", "Técnico / Práctico", "Científico / Investigativo", "Creativo / Comunicación", "Docencia / Resolución", "Contención / Salud Mental", "Servicio / Pragmático"],
            "Puntaje (%)": [92, 85, 68, 55, 48, 42, 60]
        }
        df_cat = pd.DataFrame(data_cat).set_index("Categoría")
        st.bar_chart(df_cat)
        
        # Tarjeta de Disonancia Constructiva
        expectativa = st.session_state.usuario.get('expectativa_inicial', 'Carrera elegida')
        st.markdown("### ⚖️ Contraste con tu Expectativa Inicial")
        if "Enfermería" in expectativa or "Psicología" in expectativa:
            st.warning(f"⚠️ **Observación de Disonancia:** Tu expectativa inicial era *{expectativa}* (Afinidad: 45%). Sin embargo, tus resultados en los juegos lógicos y tu FODA muestran un potencial significativamente mayor (92%) en el área **Técnica e Informática**.")
        else:
            st.success(f"✅ **¡Excelente Alineación!** Tu expectativa inicial (*{expectativa}*) tiene una alta concordancia (88%) con tus capacidades reales de pensamiento lógico y estructurado.")

        # Matriz de Trayectorias Flexibles (4 Carreras SIES)
        st.markdown("### 🎓 Trayectorias Recomendadas (Sueldos y Empleabilidad Oficial SIES)")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("""
            <div class="card-carrera">
                <h4>1. Técnico en Programación y Análisis</h4>
                <p><b>Institución:</b> IP / CFT (Educación TP)</p>
                <p><b>Empleabilidad 1er año:</b> 85% (SIES)</p>
                <p><b>Ingreso al 4° año:</b> $1.100.000 - $1.400.000</p>
                <span class="badge-gratuidad">✓ GRATUIDAD DISPONIBLE</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card-carrera">
                <h4>2. Ingeniería en Automatización y Control</h4>
                <p><b>Institución:</b> Instituto Profesional (IP)</p>
                <p><b>Empleabilidad 1er año:</b> 89% (SIES)</p>
                <p><b>Ingreso al 4° año:</b> $1.300.000 - $1.650.000</p>
                <span class="badge-gratuidad">✓ GRATUIDAD DISPONIBLE</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col_c2:
            st.markdown("""
            <div class="card-carrera">
                <h4>3. Ingeniería Civil Informática</h4>
                <p><b>Institución:</b> Universidad (U)</p>
                <p><b>Empleabilidad 1er año:</b> 91% (SIES)</p>
                <p><b>Ingreso al 4° año:</b> $1.800.000 - $2.200.000</p>
                <span class="badge-gratuidad">✓ GRATUIDAD DISPONIBLE</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card-carrera">
                <h4>4. Técnico en Ciberseguridad</h4>
                <p><b>Institución:</b> IP / CFT</p>
                <p><b>Empleabilidad 1er año:</b> 83% (SIES)</p>
                <p><b>Ingreso al 4° año:</b> $1.200.000 - $1.500.000</p>
                <span class="badge-gratuidad">✓ GRATUIDAD DISPONIBLE</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.button("📥 Enviar mi Ficha en PDF a mi Correo")
        if st.button("🔄 Reiniciar Prueba"):
            st.session_state.paso = 1
            st.rerun()

# ---------------------------------------------------------
# VISTA B2B: DASHBOARD INSTITUCIONAL DEL COLEGIO
# ---------------------------------------------------------
else:
    st.title("🏫 Dashboard Institucional - Liceo Ignacio Carrera Pinto")
    st.caption("Vista B2B para Orientadores y UTP (Ley 21.091)")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Estudiantes Evaluados", "24 / 24", "100% Cohorte 3° Medio")
    col_m2.metric("Índice de Indecisión Inicial", "37.5%", "-8% respecto a 2025")
    col_m3.metric("Alerta de Disonancia Vocacional", "29.1%", "7 alumnos a reorientar")
    
    st.markdown("---")
    st.subheader("📊 Mapa Consolidado de Talentos de la Cohorte")
    data_grupo = {
        "Área Vocacional": ["Técnico / Práctico", "Lógico / Numérico", "Contención / Salud", "Creativo / Comunicación", "Servicio / Pragmático"],
        "N° Estudiantes": [8, 6, 4, 4, 2]
    }
    df_grupo = pd.DataFrame(data_grupo).set_index("Área Vocacional")
    st.bar_chart(df_grupo)
    
    st.subheader("📋 Nómina Resumen de Alumnos (3° Medio A)")
    tabla_alumnos = pd.DataFrame({
        "Estudiante": ["Valentina Morales", "Diego Araya", "Camila Tapia", "Lucas Silva", "Sofía Rojas"],
        "NEM": [6.2, 5.4, 5.9, 5.1, 6.5],
        "Expectativa Inicial": ["Enfermería", "Ing. Mecánica", "Indeciso", "Gastronomía", "Medicina"],
        "Match Real": ["Técnico en Programación", "Ing. Electricidad", "Diseño Digital", "Técnico Gastronomía", "Enfermería U"],
        "Alerta Disonancia": ["Alta (Reorientar)", "Baja (Alineado)", "Resuelta", "Baja (Alineado)", "Media (Revisar NEM)"]
    })
    st.table(tabla_alumnos)
