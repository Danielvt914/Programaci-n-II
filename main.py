import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# FUNCIONES
# ============================================================

def convertir_monto(texto):
    """
    Convierte el monto ingresado a número.
    Permite formatos como:
    1000000
    1000000.50
    1.000.000,50
    """
    texto = texto.strip().replace("$", "").replace(" ", "")

    # Si contiene punto y coma, asumimos formato colombiano
    if "." in texto and "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def formatear_pesos(valor):
    """
    Formato colombiano:
    1014330.07 -> $ 1.014.330,07
    """
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return "$ " + texto


def calcular_cdt():
    # --------------------------------------------------------
    # RF1 y RF2 - Obtener y validar datos
    # --------------------------------------------------------

    monto = convertir_monto(entry_monto.get())

    if monto is None:
        messagebox.showerror(
            "Error",
            "El monto debe ser un número válido."
        )
        entry_monto.focus()
        return

    if monto <= 0:
        messagebox.showerror(
            "Error",
            "El monto debe ser mayor que cero."
        )
        entry_monto.focus()
        return

    plazo_texto = entry_plazo.get().strip()

    # Validar que sea entero
    try:
        plazo = int(plazo_texto)
    except ValueError:
        messagebox.showerror(
            "Error",
            "El plazo debe ser un número entero."
        )
        entry_plazo.focus()
        return

    if plazo < 1:
        messagebox.showerror(
            "Error",
            "El plazo debe ser mayor o igual a 1 mes."
        )
        entry_plazo.focus()
        return

    # Evitar que valores como 2.5 sean aceptados
    if "." in plazo_texto or "," in plazo_texto:
        messagebox.showerror(
            "Error",
            "El plazo debe ser un número entero, no decimal."
        )
        entry_plazo.focus()
        return

    # --------------------------------------------------------
    # RF3 - Calcular tasa mensual
    # --------------------------------------------------------

    tasa = 0.001695 * plazo + 0.0983

    # --------------------------------------------------------
    # RF4 y RF5 - Liquidación y proyección mensual
    # --------------------------------------------------------

    saldo = monto
    total_intereses = 0

    # Limpiar tabla
    for item in tabla.get_children():
        tabla.delete(item)

    # Mes 0
    tabla.insert(
        "",
        "end",
        values=(
            0,
            formatear_pesos(0),
            formatear_pesos(saldo)
        )
    )

    # Calcular cada mes
    for mes in range(1, plazo + 1):

        # La tasa viene expresada en porcentaje,
        # por eso se divide entre 100.
        interes = saldo * (tasa / 100)

        # Capitalización
        saldo = saldo + interes

        total_intereses += interes

        tabla.insert(
            "",
            "end",
            values=(
                mes,
                formatear_pesos(interes),
                formatear_pesos(saldo)
            )
        )

    # --------------------------------------------------------
    # RF6 - Mostrar resultado final
    # --------------------------------------------------------

    label_tasa.config(
        text=f"Tasa mensual: {tasa:.4f}%"
    )

    label_saldo_final.config(
        text=f"Saldo final: {formatear_pesos(saldo)}"
    )

    label_intereses.config(
        text=f"Total intereses: {formatear_pesos(total_intereses)}"
    )


def limpiar():
    entry_monto.delete(0, tk.END)
    entry_plazo.delete(0, tk.END)

    for item in tabla.get_children():
        tabla.delete(item)

    label_tasa.config(
        text="Tasa mensual: --"
    )

    label_saldo_final.config(
        text="Saldo final: --"
    )

    label_intereses.config(
        text="Total intereses: --"
    )

    entry_monto.focus()


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

ventana = tk.Tk()
ventana.title("Proyección de CDT")
ventana.geometry("750x650")
ventana.resizable(False, False)

# ============================================================
# TÍTULO
# ============================================================

titulo = tk.Label(
    ventana,
    text="PROYECCIÓN DE CDT",
    font=("Arial", 20, "bold")
)

titulo.pack(pady=15)

subtitulo = tk.Label(
    ventana,
    text="Cálculo de intereses y saldo mensual",
    font=("Arial", 11)
)

subtitulo.pack(pady=5)

# ============================================================
# FRAME DE DATOS
# ============================================================

frame_datos = tk.LabelFrame(
    ventana,
    text="Datos del CDT",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=15
)

frame_datos.pack(
    padx=20,
    pady=10,
    fill="x"
)

# Monto
label_monto = tk.Label(
    frame_datos,
    text="Monto inicial (COP):",
    font=("Arial", 11)
)

label_monto.grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

entry_monto = tk.Entry(
    frame_datos,
    width=25,
    font=("Arial", 11)
)

entry_monto.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)

# Plazo
label_plazo = tk.Label(
    frame_datos,
    text="Plazo (meses):",
    font=("Arial", 11)
)

label_plazo.grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

entry_plazo = tk.Entry(
    frame_datos,
    width=25,
    font=("Arial", 11)
)

entry_plazo.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)

# ============================================================
# BOTONES
# ============================================================

frame_botones = tk.Frame(ventana)

frame_botones.pack(pady=10)

boton_calcular = tk.Button(
    frame_botones,
    text="CALCULAR CDT",
    command=calcular_cdt,
    font=("Arial", 11, "bold"),
    width=18
)

boton_calcular.grid(
    row=0,
    column=0,
    padx=10
)

boton_limpiar = tk.Button(
    frame_botones,
    text="LIMPIAR",
    command=limpiar,
    font=("Arial", 11),
    width=18
)

boton_limpiar.grid(
    row=0,
    column=1,
    padx=10
)

# ============================================================
# RESULTADOS
# ============================================================

frame_resultados = tk.LabelFrame(
    ventana,
    text="Resultado",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)

frame_resultados.pack(
    padx=20,
    pady=10,
    fill="x"
)

label_tasa = tk.Label(
    frame_resultados,
    text="Tasa mensual: --",
    font=("Arial", 11)
)

label_tasa.pack(anchor="w", pady=3)

label_saldo_final = tk.Label(
    frame_resultados,
    text="Saldo final: --",
    font=("Arial", 11, "bold")
)

label_saldo_final.pack(anchor="w", pady=3)

label_intereses = tk.Label(
    frame_resultados,
    text="Total intereses: --",
    font=("Arial", 11)
)

label_intereses.pack(anchor="w", pady=3)

# ============================================================
# TABLA DE PROYECCIÓN
# ============================================================

frame_tabla = tk.LabelFrame(
    ventana,
    text="Proyección mensual",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)

frame_tabla.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)

columnas = (
    "mes",
    "interes",
    "saldo"
)

tabla = ttk.Treeview(
    frame_tabla,
    columns=columnas,
    show="headings",
    height=10
)

tabla.heading(
    "mes",
    text="Mes"
)

tabla.heading(
    "interes",
    text="Interés"
)

tabla.heading(
    "saldo",
    text="Saldo final"
)

tabla.column(
    "mes",
    width=80,
    anchor="center"
)

tabla.column(
    "interes",
    width=220,
    anchor="e"
)

tabla.column(
    "saldo",
    width=220,
    anchor="e"
)

tabla.pack(
    side="left",
    fill="both",
    expand=True
)

# Barra de desplazamiento
scrollbar = ttk.Scrollbar(
    frame_tabla,
    orient="vertical",
    command=tabla.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

tabla.configure(
    yscrollcommand=scrollbar.set
)

# ============================================================
# INICIO
# ============================================================

entry_monto.focus()

ventana.mainloop()