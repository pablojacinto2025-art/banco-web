import os
import json
import random
import time
from datetime import datetime, timedelta
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA STREAMLIT ---
st.set_page_config(
    page_title="Sistema El Duke - Online Banking",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DATOS Y CONSTANTES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "banco_datos.json")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

NOMBRES_SOCIOS = {
    "1": "Maria Garcia",
    "2": "Luis Fernandez",
    "3": "Carlos Mendoza",
    "4": "Sofía Castro",
    "5": "Mateo Rivera",
    "6": "Santiago Gómez",
    "7": "Sebastián Peña",
    "8": "Mariana Silva",
    "9": "Diego Torres"
}

NOMBRES_INVENTADOS = [
    "Lucas Alcaraz", "Martina Benítez", "Benjamín Calderón", "Valeria Delgado", "Nicolás Espinosa", 
    "Emma Fuentes", "Alejandro Garrido", "Zoe Hidalgo", "Daniel Ibarra", "Sara Juárez", 
    "Mateo Lozano", "Sofía Medina", "Santiago Navarro", "Valentina Ortega", "Sebastián Pacheco", 
    "Camila Quiroga", "Leonardo Ríos", "Isabella Salinas", "Diego Tejada", "Mariana Urbina", 
    "Tomás Vargas", "Lucía Zamora", "Samuel Abad", "Elena Blanco", "Gabriel Crespo", 
    "Victoria Díaz", "Joaquín Estévez", "Julieta Fajardo", "Matías Guzmán", "Catalina Herrera"
]

# --- FUNCIONES DE LÓGICA DE DATOS ---
def obtener_fecha_corta(fecha_str):
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
        return f"{dt.day} de {MESES[dt.month - 1]}"
    except:
        return str(fecha_str)[:10]

def enmascarar_cuenta(cuenta_str):
    c = str(cuenta_str).strip()
    if len(c) > 4:
        return ("*" * (len(c) - 4)) + c[-4:]
    return c

def enmascarar_nombre(nombre_completo):
    """Mantiene el primer nombre y reemplaza los apellidos por asteriscos (*)"""
    partes = str(nombre_completo).strip().split(" ")
    if len(partes) > 1:
        primer_nombre = partes[0]
        apellidos = " ".join(partes[1:])
        apellidos_ocultos = "".join(["*" if c != " " else " " for c in apellidos])
        return f"{primer_nombre} {apellidos_ocultos}"
    return nombre_completo

def enmascarar_descripcion(desc):
    """Procesa la descripción del movimiento para enmascarar el apellido"""
    if desc.startswith("Transf. a "):
        nombre_persona = desc.replace("Transf. a ", "")
        return f"Transf. a {enmascarar_nombre(nombre_persona)}"
    return desc

def generar_datos_iniciales():
    socios = {}
    for i in range(1, 10):
        cuenta = f"215-0000{i}"
        socios[str(i)] = {
            "cuenta": cuenta,
            "saldo": round(random.uniform(30000, 40000), 2),
            "movimientos": [],
            "pendientes": []
        }
    
    hoy = datetime.now()
    hace_4 = hoy - timedelta(days=4)
    hace_3 = hoy - timedelta(days=3)
    anteayer = hoy - timedelta(days=2)
    ayer = hoy - timedelta(days=1)
    
    opciones_monto = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0]

    def agregar_movimiento(s, fecha):
        nombre = random.choice(NOMBRES_INVENTADOS)
        monto = random.choice(opciones_monto)
        hora_mov = f"{random.randint(8,20):02d}:{random.randint(0,59):02d}:00"
        fecha_completa = f"{fecha.strftime('%Y-%m-%d')} {hora_mov}"
        cta_base = str(random.randint(10000000000000, 99999999999999))
        cta_enmascarada = enmascarar_cuenta(cta_base)
        s["movimientos"].append({
            "tipo": "-",
            "monto": monto,
            "fecha": fecha_completa,
            "desc": f"Transf. a {nombre}",
            "cuenta_enmascarada": cta_enmascarada
        })

    for s in socios.values():
        for _ in range(4): agregar_movimiento(s, hace_4)
        for _ in range(3): agregar_movimiento(s, hace_3)
        for _ in range(4): agregar_movimiento(s, anteayer)
        for _ in range(3): agregar_movimiento(s, ayer)
        s["movimientos"].sort(key=lambda x: x["fecha"], reverse=True)

    afiliados_iniciales = [
        {"codigo": "AF-001", "usuario": "juanperez", "pass": "admin123", "fecha": "2026-01-10", "saldo": 150.0},
        {"codigo": "AF-002", "usuario": "mariagomez", "pass": "maria456", "fecha": "2026-02-15", "saldo": 200.0},
        {"codigo": "AF-003", "usuario": "luisfernandez", "pass": "luis789", "fecha": "2026-03-20", "saldo": 50.0},
        {"codigo": "AF-004", "usuario": "anacastro", "pass": "ana321", "fecha": "2026-04-05", "saldo": 300.0},
        {"codigo": "AF-005", "usuario": "pedrorivera", "pass": "pedro654", "fecha": "2026-05-12", "saldo": 0.0}
    ]

    return {
        "socios": socios,
        "afiliados": afiliados_iniciales,
        "config": {
            "cuenta_falsa_nombre": "Julio Cesar Ortega Pusari",
            "cuenta_falsa_num": "00219411476777203991",
            "texto_banco": "BCP",
            "monto_minimo": 100.0,
            "token_activo": True,
            "token_modo": "sunat",  # "tarifa" o "sunat"
            "cronometro_activo": False,
            "qr_path": "",
            "qr_tarifa_path": "",
            "curso1_path": "",
            "curso2_path": "",
            "tiempo_espera_seg": 3
        },
        "ultima_fecha_simulacion": hoy.strftime("%Y-%m-%d")
    }

def cargar_datos():
    if not os.path.exists(DATA_FILE):
        datos = generar_datos_iniciales()
        guardar_datos(datos)
        return datos
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)
        if "afiliados" not in datos:
            datos["afiliados"] = generar_datos_iniciales()["afiliados"]
        if "token_modo" not in datos["config"]:
            datos["config"]["token_modo"] = "sunat"
        if "qr_tarifa_path" not in datos["config"]:
            datos["config"]["qr_tarifa_path"] = ""
        if "curso1_path" not in datos["config"]:
            datos["config"]["curso1_path"] = ""
        if "curso2_path" not in datos["config"]:
            datos["config"]["curso2_path"] = ""
        return datos

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def simular_movimientos_diarios(datos):
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    if datos.get("ultima_fecha_simulacion") != hoy_str:
        for id_socio, socio in datos["socios"].items():
            num_movimientos = random.randint(3, 4)
            for _ in range(num_movimientos):
                monto = float(random.choice([1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0]))
                nombre = random.choice(NOMBRES_INVENTADOS)
                hora = f"{random.randint(8,20):02d}:{random.randint(0,59):02d}:00"
                fecha_hora = f"{hoy_str} {hora}"
                cta_base = str(random.randint(10000000000000, 99999999999999))
                cta_enmascarada = enmascarar_cuenta(cta_base)
                
                socio["saldo"] -= monto
                socio["movimientos"].insert(0, {
                    "tipo": "-",
                    "monto": monto,
                    "fecha": fecha_hora,
                    "desc": f"Transf. a {nombre}",
                    "cuenta_enmascarada": cta_enmascarada
                })
        datos["ultima_fecha_simulacion"] = hoy_str
        guardar_datos(datos)

def guardar_imagen_subida(archivo_subido, nombre_archivo):
    """Guarda una imagen subida por el usuario en el disco"""
    if archivo_subido is not None:
        ruta_completa = os.path.join(BASE_DIR, nombre_archivo)
        with open(ruta_completa, "wb") as f:
            f.write(archivo_subido.getbuffer())
        return ruta_completa
    return None

# --- INICIALIZACIÓN DE ESTADO EN STREAMLIT ---
if "datos" not in st.session_state:
    st.session_state["datos"] = cargar_datos()
    simular_movimientos_diarios(st.session_state["datos"])

if "socio_actual" not in st.session_state:
    st.session_state["socio_actual"] = None

if "tab_actual" not in st.session_state:
    st.session_state["tab_actual"] = "Mi Cuenta"

if "transf_step" not in st.session_state:
    st.session_state["transf_step"] = 1

if "temp_transf" not in st.session_state:
    st.session_state["temp_transf"] = None

datos = st.session_state["datos"]

# --- PANTALLAS DE LOGIN ---
if not st.session_state["socio_actual"]:
    st.markdown("<h1 style='text-align: center; color: #1565C0;'>ONLINE BANKING EL DUKE</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Acceso al Sistema")
            socio_input = st.text_input("Número de Socio (1 al 9)", placeholder="Ej: 1")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Clave: 1234")
            
            btn_login = st.form_submit_button("Ingresar", use_container_width=True)
            
            if btn_login:
                socio_clean = socio_input.strip()
                if socio_clean in datos["socios"]:
                    if pass_input == "1234":
                        st.session_state["socio_actual"] = socio_clean
                        st.toast("¡Bienvenido al sistema!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta (Use: 1234)")
                else:
                    st.error("Socio no encontrado (Ingrese un número del 1 al 9)")

else:
    # --- BARRA LATERAL (SIDEBAR) ---
    socio_id = st.session_state["socio_actual"]
    socio_info = datos["socios"][socio_id]
    nombre_real = NOMBRES_SOCIOS.get(socio_id, "Socio Desconocido")

    st.sidebar.markdown(f"## **Sistema El Duke**")
    st.sidebar.markdown(f"👤 **{nombre_real}**")
    st.sidebar.markdown(f"💳 Cuenta: `{socio_info['cuenta']}`")
    st.sidebar.divider()

    opcion = st.sidebar.radio(
        "Menú de Navegación",
        ["Mi Cuenta", "Transferencias", "Operaciones Pendientes", "Afiliados", "Curso", "Seguridad"],
        index=["Mi Cuenta", "Transferencias", "Operaciones Pendientes", "Afiliados", "Curso", "Seguridad"].index(st.session_state["tab_actual"])
    )
    st.session_state["tab_actual"] = opcion

    st.sidebar.divider()
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state["socio_actual"] = None
        st.session_state["transf_step"] = 1
        st.rerun()

    # --- TAB 0: MI CUENTA ---
    if opcion == "Mi Cuenta":
        st.title(f"Bienvenido, {nombre_real}")
        st.caption(f"Cuenta Origen: {socio_info['cuenta']}")
        
        col_saldo, col_btn = st.columns([2, 1])
        with col_saldo:
            st.metric(label="SALDO DISPONIBLE", value=f"S/ {socio_info['saldo']:,.2f}")
        with col_btn:
            st.write("")
            if st.button("💸 Nueva Transferencia", use_container_width=True, type="primary"):
                st.session_state["tab_actual"] = "Transferencias"
                st.session_state["transf_step"] = 1
                st.rerun()

        st.divider()
        st.subheader("MOVIMIENTOS RECIENTES")

        movimientos = socio_info["movimientos"][:20]
        if movimientos:
            for idx, mov in enumerate(movimientos):
                desc_enmascarada = enmascarar_descripcion(mov["desc"])
                monto = mov["monto"]
                fecha = obtener_fecha_corta(mov["fecha"])
                
                with st.expander(f"{mov['tipo']} S/ {monto:,.2f} — {desc_enmascarada} ({fecha})"):
                    st.markdown(f"**Detalles del Movimiento:**")
                    st.write(f"• **Destino:** {desc_enmascarada.replace('Transf. a ', '')}")
                    st.write(f"• **Cuenta:** {mov.get('cuenta_enmascarada', 'N/A')}")
                    st.write(f"• **Fecha:** {fecha}")
                    st.write(f"• **Monto:** S/ {monto:,.2f}")
                    if datos["config"].get("texto_banco"):
                        st.write(f"• **Banco:** {datos['config']['texto_banco']}")
        else:
            st.info("No hay movimientos registrados.")

    # --- TAB 1: TRANSFERENCIAS ---
    elif opcion == "Transferencias":
        st.title("Transferencias Bancarias")

        step = st.session_state["transf_step"]

        # PASO 1: Formulario Inicial
        if step == 1:
            st.subheader("PASO 1: DATOS DE TRANSFERENCIA")
            with st.form("form_paso1"):
                cuenta_dest = st.text_input("Cuenta Destino", value=st.session_state["temp_transf"]["cuenta"] if st.session_state["temp_transf"] else "")
                monto_dest = st.number_input("Monto a Enviar (S/)", min_value=1.0, value=float(st.session_state["temp_transf"]["monto"]) if st.session_state["temp_transf"] else 100.0)
                
                btn_p1 = st.form_submit_button("Continuar", type="primary")
                if btn_p1:
                    if not cuenta_dest:
                        st.warning("Ingrese una cuenta de destino.")
                    else:
                        nombre_dest = "Desconocido"
                        if cuenta_dest.strip() == datos["config"]["cuenta_falsa_num"]:
                            nombre_dest = datos["config"]["cuenta_falsa_nombre"]
                        elif datos["config"]["cuenta_falsa_nombre"]:
                            # Usar el nombre configurado en destinatario preferente
                            nombre_dest = datos["config"]["cuenta_falsa_nombre"]

                        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        fecha_mostrar = obtener_fecha_corta(ahora)
                        cuenta_enmascarada = enmascarar_cuenta(cuenta_dest)

                        st.session_state["temp_transf"] = {
                            "cuenta": cuenta_dest.strip(),
                            "cuenta_enmascarada": cuenta_enmascarada,
                            "nombre": nombre_dest,
                            "monto": monto_dest,
                            "fecha": ahora,
                            "fecha_corta": fecha_mostrar
                        }
                        st.session_state["transf_step"] = 2
                        st.rerun()

        # PASO 2: Confirmación
        elif step == 2:
            t = st.session_state["temp_transf"]
            st.subheader("PASO 2: CONFIRMACIÓN")
            
            st.info(f"**Destinatario:** {t['nombre']}\n\n"
                    f"**Número de Cuenta:** {t['cuenta_enmascarada']}\n\n"
                    f"**Banco:** {datos['config'].get('texto_banco', 'El Duke Bank')}\n\n"
                    f"**Monto:** S/ {t['monto']:,.2f}\n\n"
                    f"**Fecha:** {t['fecha_corta']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirmar Transferencia", type="primary", use_container_width=True):
                    minimo = datos["config"]["monto_minimo"]
                    if t["monto"] < minimo:
                        st.error(f"El monto mínimo de transferencia es S/ {minimo}")
                        st.error(f"Monto De S/ {t['monto']:,.1f} Agotado.")
                    elif datos["config"].get("token_activo", True):
                        st.session_state["transf_step"] = 5  # Error Token
                        st.rerun()
                    elif datos["config"].get("cronometro_activo", False):
                        st.session_state["transf_step"] = 3  # Cronómetro
                        st.rerun()
                    else:
                        socio_info["saldo"] -= t["monto"]
                        socio_info["movimientos"].insert(0, {
                            "tipo": "-",
                            "monto": t["monto"],
                            "fecha": t["fecha"],
                            "desc": f"Transf. a {t['nombre']}",
                            "cuenta_enmascarada": t["cuenta_enmascarada"]
                        })
                        guardar_datos(datos)
                        st.session_state["transf_step"] = 4  # Éxito
                        st.rerun()
            with col2:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state["transf_step"] = 1
                    st.rerun()

        # PASO 3: Cronómetro
        elif step == 3:
            st.subheader("PASO 3: PROCESANDO TRANSACCIÓN")
            segundos = datos["config"].get("tiempo_espera_seg", 3)
            
            progreso = st.progress(0)
            status = st.empty()
            
            for i in range(segundos, 0, -1):
                status.markdown(f"### ⏳ Esperando confirmación de red: **{i} segundos**")
                progreso.progress(int(((segundos - i + 1) / segundos) * 100))
                time.sleep(1)
            
            t = st.session_state["temp_transf"]
            socio_info["saldo"] -= t["monto"]
            socio_info["movimientos"].insert(0, {
                "tipo": "-",
                "monto": t["monto"],
                "fecha": t["fecha"],
                "desc": f"Transf. a {t['nombre']}",
                "cuenta_enmascarada": t["cuenta_enmascarada"]
            })
            guardar_datos(datos)
            st.session_state["transf_step"] = 4
            st.rerun()

        # PASO 4: Voucher Éxito
        elif step == 4:
            t = st.session_state["temp_transf"]
            st.success("✅ ¡TRANSFERENCIA EXITOSA!")
            
            st.markdown(f"### Voucher de Operación")
            st.write(f"**Para:** {t['nombre']}")
            st.write(f"**Cuenta:** {t['cuenta_enmascarada']}")
            if datos["config"].get("texto_banco"):
                st.write(f"**Banco:** {datos['config']['texto_banco']}")
            st.write(f"**Monto:** S/ {t['monto']:,.2f}")
            st.write(f"**Fecha:** {t['fecha_corta']}")
            
            if st.button("Volver al Inicio", type="primary"):
                st.session_state["temp_transf"] = None
                st.session_state["transf_step"] = 1
                st.session_state["tab_actual"] = "Mi Cuenta"
                st.rerun()

        # PASO 5: Advertencia Token Digital
        elif step == 5:
            st.error("⚠️ ¡ADVERTENCIA! Transferencia Rechazada")
            st.markdown("**Debe activar y escanear su Token Digital para continuar.**")
            
            modo_actual = datos["config"].get("token_modo", "sunat")

            if modo_actual == "tarifa":
                qr_tarifa = datos["config"].get("qr_tarifa_path", "")
                if qr_tarifa and os.path.exists(qr_tarifa):
                    st.image(qr_tarifa, caption="Escanee su Código QR", width=200)
                else:
                    st.warning("Imagen QR para Modo Tarifa no configurada (Ajuste en Seguridad).")

                st.error("No se puede completar la solicitud. Debes abonar la tarifa correspondiente para mantener tu nombre oculto")
            else:
                qr_path = datos["config"].get("qr_path", "")
                if qr_path and os.path.exists(qr_path):
                    st.image(qr_path, caption="Escanee su Código QR", width=200)
                else:
                    st.warning("Imagen QR para Modo SUNAT no configurada (Ajuste en Seguridad).")

                st.error("Por motivos de seguridad tributaria ante la SUNAT, no está permitido realizar esta operación")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar en Operaciones Pendientes", use_container_width=True):
                    if st.session_state["temp_transf"]:
                        # 1. Guardar en lista de pendientes
                        socio_info["pendientes"].append(st.session_state["temp_transf"])
                        
                        # 2. Sincronizar automáticamente con Destinatario Preferente en Seguridad
                        datos["config"]["cuenta_falsa_nombre"] = st.session_state["temp_transf"]["nombre"]
                        datos["config"]["cuenta_falsa_num"] = st.session_state["temp_transf"]["cuenta"]
                        
                        guardar_datos(datos)
                        st.toast("Guardado en pendientes y sincronizado con Seguridad", icon="💾")
                        st.session_state["transf_step"] = 1
                        st.session_state["tab_actual"] = "Operaciones Pendientes"
                        st.rerun()
            with col2:
                if st.button("Volver", use_container_width=True):
                    st.session_state["transf_step"] = 1
                    st.rerun()

    # --- TAB 2: OPERACIONES PENDIENTES ---
    elif opcion == "Operaciones Pendientes":
        st.title("Transferencias Pendientes")
        pendientes = socio_info.get("pendientes", [])

        if pendientes:
            for idx, p in enumerate(pendientes):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1.2, 1])
                with col1:
                    st.write(f"**Destinatario:** {p['nombre']}")
                with col2:
                    st.write(f"**Cuenta:** {p['cuenta_enmascarada']}")
                with col3:
                    st.write(f"**Monto:** S/ {p['monto']:,.2f}")
                with col4:
                    if st.button("Continuar", key=f"pend_cont_{idx}"):
                        # Cargar transferencia en estado temporal SIN eliminarla de la lista
                        st.session_state["temp_transf"] = p
                        # Actualizar automáticamente en Destinatario Preferente
                        datos["config"]["cuenta_falsa_nombre"] = p["nombre"]
                        datos["config"]["cuenta_falsa_num"] = p["cuenta"]
                        guardar_datos(datos)
                        
                        st.session_state["tab_actual"] = "Transferencias"
                        st.session_state["transf_step"] = 1
                        st.rerun()
                with col5:
                    if st.button("❌ Eliminar", key=f"pend_del_{idx}"):
                        # Eliminar de la lista de pendientes solo si presiona la X
                        socio_info["pendientes"].pop(idx)
                        guardar_datos(datos)
                        st.toast("Operación pendiente eliminada", icon="🗑️")
                        st.rerun()
        else:
            st.info("No hay transferencias pendientes.")

    # --- TAB 3: AFILIADOS ---
    elif opcion == "Afiliados":
        st.title("Gestión de Afiliados")

        with st.expander("➕ Agregar Nuevo Afiliado"):
            with st.form("form_nuevo_afiliado"):
                cod_af = st.text_input("Código (Ej: AF-006)")
                usu_af = st.text_input("Usuario")
                pass_af = st.text_input("Contraseña", type="password")
                btn_save_af = st.form_submit_button("Guardar Afiliado")
                
                if btn_save_af:
                    if cod_af and usu_af and pass_af:
                        nuevo_af = {
                            "codigo": cod_af.strip(),
                            "usuario": usu_af.strip(),
                            "pass": pass_af.strip(),
                            "fecha": datetime.now().strftime("%Y-%m-%d"),
                            "saldo": 0.0
                        }
                        datos["afiliados"].append(nuevo_af)
                        guardar_datos(datos)
                        st.toast("Afiliado registrado exitosamente", icon="✅")
                        st.rerun()
                    else:
                        st.warning("Todos los campos son obligatorios.")

        st.divider()

        afiliados = datos.get("afiliados", [])
        if afiliados:
            for af in afiliados:
                c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 2])
                c1.write(f"**{af['codigo']}**")
                c2.write(af['usuario'])
                c3.write("••••••••")
                c4.write(af['fecha'])
                c5.write(f"S/ {af['saldo']:,.2f}")
        else:
            st.info("No hay afiliados registrados.")

    # --- TAB 4: CURSO ---
    elif opcion == "Curso":
        st.title("Paquetes de Afiliación")

        st.subheader("Combo 1: Paquete de afiliado + USB con el sistema de transferencia")
        c1_path = datos["config"].get("curso1_path", "")
        if c1_path and os.path.exists(c1_path):
            st.image(c1_path, use_column_width=True)
        else:
            st.info("Sin imagen configurada para Combo 1 (Ajuste la imagen en Seguridad).")

        st.divider()

        st.subheader("Combo 2: Paquete de afiliado + proveedor de tarjetas + sistema de transferencia y lector")
        c2_path = datos["config"].get("curso2_path", "")
        if c2_path and os.path.exists(c2_path):
            st.image(c2_path, use_column_width=True)
        else:
            st.info("Sin imagen configurada para Combo 2 (Ajuste la imagen en Seguridad).")

    # --- TAB 5: SEGURIDAD Y CONFIGURACIÓN ---
    elif opcion == "Seguridad":
        st.title("CONFIGURACIÓN Y SEGURIDAD")

        cfg = datos["config"]

        # Destinatario preferente
        with st.expander("📌 REGISTRO DE DESTINATARIO PREFERENTE", expanded=True):
            nom_falso = st.text_input("Nombre Preferente", value=cfg.get("cuenta_falsa_nombre", ""))
            cta_falsa = st.text_input("Número de Cuenta", value=cfg.get("cuenta_falsa_num", ""))
            if st.button("Guardar Destinatario"):
                cfg["cuenta_falsa_nombre"] = nom_falso
                cfg["cuenta_falsa_num"] = cta_falsa
                guardar_datos(datos)
                st.success("Destinatario preferente actualizado.")

        # Nombre de Banco (SELECCIÓN RÁPIDA DE BANCOS)
        with st.expander("🏦 TEXTO DE BOLETA (BANCO)"):
            bancos_lista = ["BCP", "YAPE", "PLIN", "INTERBANK", "Otro (Escribir manualmente)..."]
            banco_actual = cfg.get("texto_banco", "BCP")
            
            index_banco = 0
            if banco_actual in bancos_lista:
                index_banco = bancos_lista.index(banco_actual)
            else:
                index_banco = 4 # Seleccionar "Otro" si no está en la lista rápida
                
            banco_sel = st.selectbox("Seleccionar Banco de la lista:", bancos_lista, index=index_banco)
            
            if banco_sel == "Otro (Escribir manualmente)...":
                banco_final = st.text_input("Escribe el nombre del banco personalizado:", value=banco_actual if banco_actual not in bancos_lista else "")
            else:
                banco_final = banco_sel

            if st.button("Guardar Banco"):
                cfg["texto_banco"] = banco_final
                guardar_datos(datos)
                st.success(f"Banco guardado como: '{banco_final}'")

        # Limite Mínimo
        with st.expander("💰 LÍMITE MÍNIMO DE TRANSFERENCIA"):
            m_min = st.number_input("Monto Mínimo (S/)", value=float(cfg.get("monto_minimo", 100.0)))
            if st.button("Actualizar Límite"):
                cfg["monto_minimo"] = m_min
                guardar_datos(datos)
                st.success("Límite mínimo actualizado.")

        # Token Digital
        with st.expander("🔑 TOKEN DIGITAL DE SEGURIDAD"):
            token_general = st.checkbox("Activar Validación por Token", value=cfg.get("token_activo", True))
            
            st.markdown("---")
            st.markdown("#### Selección de Modo de Rechazo:")
            
            if "token_modo_state" not in st.session_state:
                st.session_state["token_modo_state"] = cfg.get("token_modo", "sunat")

            # MODO 1: Tarifa Nombre Oculto (Con QR)
            st.markdown("**Modo 1: Activar Rechazo por Tarifa (Nombre Oculto - Con QR)**")
            col_check_tarifa, col_qr_tarifa = st.columns([2, 2])
            with col_check_tarifa:
                check_tarifa = st.checkbox(
                    "Activar Modo Tarifa", 
                    value=(st.session_state["token_modo_state"] == "tarifa")
                )
            with col_qr_tarifa:
                qr_file_modo1 = st.file_uploader("Seleccionar Imagen de QR para Modo Tarifa", type=["png", "jpg", "jpeg"], key="qr_modo1_upload")

            st.markdown("---")

            # MODO 2: SUNAT (Con QR)
            st.markdown("**Modo 2: Activar Rechazo por SUNAT (Con QR)**")
            col_check_sunat, col_qr_upload = st.columns([2, 2])
            with col_check_sunat:
                check_sunat = st.checkbox(
                    "Activar Modo SUNAT", 
                    value=(st.session_state["token_modo_state"] == "sunat")
                )
            with col_qr_upload:
                qr_file_modo2 = st.file_uploader("Seleccionar Imagen de QR para Modo SUNAT", type=["png", "jpg", "jpeg"], key="qr_modo2_upload")

            # Lógica de exclusión mutua
            modo_seleccionado = st.session_state["token_modo_state"]
            if check_tarifa and modo_seleccionado != "tarifa":
                st.session_state["token_modo_state"] = "tarifa"
                st.rerun()
            elif check_sunat and modo_seleccionado != "sunat":
                st.session_state["token_modo_state"] = "sunat"
                st.rerun()

            if st.button("Guardar Configuración de Token"):
                cfg["token_activo"] = token_general
                cfg["token_modo"] = st.session_state["token_modo_state"]
                
                # Guardar QR Modo 1
                if qr_file_modo1 is not None:
                    path1 = guardar_imagen_subida(qr_file_modo1, "qr_tarifa.png")
                    if path1:
                        cfg["qr_tarifa_path"] = path1

                # Guardar QR Modo 2
                if qr_file_modo2 is not None:
                    path2 = guardar_imagen_subida(qr_file_modo2, "qr_code.png")
                    if path2:
                        cfg["qr_path"] = path2

                guardar_datos(datos)
                st.success("Configuración de Token y Códigos QR actualizados correctamente.")

        # Subida de Imágenes Adicionales
        with st.expander("🖼️ IMÁGENES DEL SISTEMA"):
            st.write("Selecciona una imagen de tus archivos para cada sección:")
            
            c1_file = st.file_uploader("Seleccionar Paquete 1 (Curso)", type=["png", "jpg", "jpeg"], key="c1_upload")
            c2_file = st.file_uploader("Seleccionar Combo 2 (Curso)", type=["png", "jpg", "jpeg"], key="c2_upload")
            
            if st.button("Guardar Imágenes"):
                hubo_cambios = False
                if c1_file is not None:
                    path = guardar_imagen_subida(c1_file, "curso1.png")
                    if path:
                        cfg["curso1_path"] = path
                        hubo_cambios = True
                if c2_file is not None:
                    path = guardar_imagen_subida(c2_file, "curso2.png")
                    if path:
                        cfg["curso2_path"] = path
                        hubo_cambios = True
                
                if hubo_cambios:
                    guardar_datos(datos)
                    st.success("¡Imágenes subidas y guardadas con éxito!")
                else:
                    st.warning("Selecciona al menos un archivo antes de guardar.")

        # Cronómetro
        with st.expander("⏱️ TIEMPO DE ESPERA Y CRONÓMETRO"):
            cron_active = st.checkbox("Activar Cronómetro de Espera", value=cfg.get("cronometro_activo", False))
            t_seg = st.number_input("Tiempo de Espera (Segundos)", min_value=0, value=int(cfg.get("tiempo_espera_seg", 3)))
            if st.button("Guardar Configuración de Tiempo"):
                cfg["cronometro_activo"] = cron_active
                cfg["tiempo_espera_seg"] = t_seg
                guardar_datos(datos)
                st.success("Configuración de cronómetro guardada.")

        # Gestor de Saldos
        with st.expander("📊 GESTOR DE SALDOS DE SOCIOS"):
            for i in range(1, 10):
                id_s = str(i)
                nombre_s = NOMBRES_SOCIOS.get(id_s, f"Socio {id_s}")
                datos["socios"][id_s]["saldo"] = st.number_input(
                    f"{id_s} - {nombre_s}",
                    value=float(datos["socios"][id_s]["saldo"]),
                    key=f"saldo_socio_{id_s}"
                )
            if st.button("Guardar Saldos de Socios"):
                guardar_datos(datos)
                st.success("Saldos actualizados correctamente.")

        # Editor de Movimientos Recientes
        with st.expander("📝 EDITOR DE MIS MOVIMIENTOS RECIENTES"):
            movs = socio_info["movimientos"]
            for idx, m in enumerate(movs):
                st.markdown(f"**Movimiento {idx+1}:** {m['desc']}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    m["cuenta_enmascarada"] = st.text_input("Cuenta", value=m.get("cuenta_enmascarada", ""), key=f"mov_cta_{idx}")
                with c2:
                    m["fecha"] = st.text_input("Fecha (YYYY-MM-DD HH:MM:SS)", value=m["fecha"], key=f"mov_fec_{idx}")
                with c3:
                    m["monto"] = st.number_input("Monto (S/)", value=float(m["monto"]), key=f"mov_monto_{idx}")
            if st.button("Guardar Cambios de Movimientos"):
                guardar_datos(datos)
                st.success("Movimientos modificados correctamente.")

        # Editor de Afiliados
        with st.expander("👥 EDITOR DE AFILIADOS"):
            afiliados = datos.get("afiliados", [])
            for idx, af in enumerate(afiliados):
                st.markdown(f"**Afiliado {idx+1}:** {af['codigo']}")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    af["usuario"] = st.text_input("Usuario", value=af["usuario"], key=f"af_usu_{idx}")
                with c2:
                    af["pass"] = st.text_input("Contraseña", value=af["pass"], key=f"af_pass_{idx}")
                with c3:
                    af["fecha"] = st.text_input("Fecha", value=af["fecha"], key=f"af_fec_{idx}")
                with c4:
                    af["saldo"] = st.number_input("Saldo (S/)", value=float(af["saldo"]), key=f"af_sal_{idx}")
            if st.button("Guardar Cambios de Afiliados"):
                guardar_datos(datos)
                st.success("Afiliados modificados correctamente.")
