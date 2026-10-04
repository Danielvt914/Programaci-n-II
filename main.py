"""Proyección de CDT - un solo archivo.

- En Google Colab (o sin pantalla) se ejecuta en modo consola.
- En un computador con entorno gráfico abre la ventana tkinter.
- Para forzar consola: python cdt.py --consola
"""
import re
import sys


# ============================================================
# LÓGICA (RF1 - RF6)
# ============================================================

def convertir_monto(texto):
    """Acepta 1000000, 1000000.50, 1.000.000, 1.000.000,50, $ 1.000.000"""
    texto = texto.strip().replace("$", "").replace(" ", "")
    if "," in texto:                                   # formato colombiano
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1 or re.fullmatch(r"[+-]?\d{1,3}\.\d{3}", texto):
        texto = texto.replace(".", "")                 # 1.000.000 / 1.000
    if re.fullmatch(r"[+-]?\d+(\.\d+)?", texto):       # rechaza nan, inf, 1e5
        return float(texto)
    return None


def formatear_pesos(valor):
    """1014330.07 -> $ 1.014.330,07"""
    t = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "$ " + t


def validar_monto(texto):
    """Devuelve (monto, error)."""
    monto = convertir_monto(texto)
    if monto is None:
        return None, "El monto debe ser un número válido."
    if monto <= 0:
        return None, "El monto debe ser mayor que cero."
    return monto, None


def validar_plazo(texto):
    """Devuelve (plazo, error). Rechaza cero, negativos, decimales y texto."""
    texto = texto.strip()
    if re.fullmatch(r"[+-]?\d+", texto):
        plazo = int(texto)
        if plazo < 1:
            return None, "El plazo debe ser mayor o igual a 1 mes."
        return plazo, None
    if re.fullmatch(r"[+-]?\d+[.,]\d+", texto):
        return None, "El plazo debe ser un número entero, no decimal."
    return None, "El plazo debe ser un número entero."


def calcular_tasa(plazo):
    """RF3: tasa mensual en porcentaje."""
    return 0.001695 * plazo + 0.0983


def proyectar(monto, plazo):
    """RF4 y RF5: devuelve (tasa, filas, saldo_final, total_intereses).
    filas = [(mes, interes, saldo)], con el mes 0 sin interés (None)."""
    tasa = calcular_tasa(plazo)
    saldo = monto
    filas = [(0, None, saldo)]
    for mes in range(1, plazo + 1):
        interes = saldo * (tasa / 100)       # sin redondear
        saldo += interes
        filas.append((mes, interes, saldo))
    return tasa, filas, saldo, saldo - monto


# ============================================================
# MODO CONSOLA (Google Colab)
# ============================================================

def ejecutar_consola():
    while True:
        monto, error = validar_monto(input("Monto inicial (COP): "))
        if error:
            print("Error:", error)
        else:
            break
    while True:
        plazo, error = validar_plazo(input("Plazo (meses): "))
        if error:
            print("Error:", error)
        else:
            break

    tasa, filas, saldo, intereses = proyectar(monto, plazo)

    print(f"\n{'Mes':>4} | {'Intereses':>20} | {'Saldo final mes':>22}")
    print("-" * 52)
    for mes, interes, s in filas:
        i = "" if interes is None else formatear_pesos(interes)
        print(f"{mes:>4} | {i:>20} | {formatear_pesos(s):>22}")

    print(f"\nTasa mensual aplicada: {str(round(tasa, 7)).replace('.', ',')}%")
    print(f"Saldo final:           {formatear_pesos(saldo)}")
    print(f"Total intereses:       {formatear_pesos(intereses)}")


# ============================================================
# MODO GRÁFICO (tkinter)
# ============================================================

def ejecutar_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    ventana = tk.Tk()          # lanza TclError si no hay pantalla
    ventana.title("Proyección de CDT")
    ventana.geometry("750x650")
    ventana.resizable(False, False)

    def calcular_cdt():
        monto, error = validar_monto(entry_monto.get())
        if error:
            messagebox.showerror("Error", error)
            entry_monto.focus()
            return
        plazo, error = validar_plazo(entry_plazo.get())
        if error:
            messagebox.showerror("Error", error)
            entry_plazo.focus()
            return

        tasa, filas, saldo, total = proyectar(monto, plazo)

        for item in tabla.get_children():
            tabla.delete(item)
        for mes, interes, s in filas:
            ti = "" if interes is None else formatear_pesos(interes)
            tabla.insert("", "end", values=(mes, ti, formatear_pesos(s)))

        label_tasa.config(text=f"Tasa mensual: {tasa:.4f}%".replace(".", ","))
        label_saldo_final.config(text=f"Saldo final: {formatear_pesos(saldo)}")
        label_intereses.config(
            text=f"Total intereses: {formatear_pesos(total)}")

    def limpiar():
        entry_monto.delete(0, tk.END)
        entry_plazo.delete(0, tk.END)
        for item in tabla.get_children():
            tabla.delete(item)
        label_tasa.config(text="Tasa mensual: --")
        label_saldo_final.config(text="Saldo final: --")
        label_intereses.config(text="Total intereses: --")
        entry_monto.focus()

    tk.Label(ventana, text="PROYECCIÓN DE CDT",
             font=("Arial", 20, "bold")).pack(pady=15)
    tk.Label(ventana, text="Cálculo de intereses y saldo mensual",
             font=("Arial", 11)).pack(pady=5)

    frame_datos = tk.LabelFrame(ventana, text="Datos del CDT",
                                font=("Arial", 11, "bold"), padx=15, pady=15)
    frame_datos.pack(padx=20, pady=10, fill="x")
    tk.Label(frame_datos, text="Monto inicial (COP):", font=("Arial", 11)
             ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_monto = tk.Entry(frame_datos, width=25, font=("Arial", 11))
    entry_monto.grid(row=0, column=1, padx=10, pady=10)
    tk.Label(frame_datos, text="Plazo (meses):", font=("Arial", 11)
             ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_plazo = tk.Entry(frame_datos, width=25, font=("Arial", 11))
    entry_plazo.grid(row=1, column=1, padx=10, pady=10)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)
    tk.Button(frame_botones, text="CALCULAR CDT", command=calcular_cdt,
              font=("Arial", 11, "bold"), width=18
              ).grid(row=0, column=0, padx=10)
    tk.Button(frame_botones, text="LIMPIAR", command=limpiar,
              font=("Arial", 11), width=18).grid(row=0, column=1, padx=10)

    frame_res = tk.LabelFrame(ventana, text="Resultado",
                              font=("Arial", 11, "bold"), padx=15, pady=10)
    frame_res.pack(padx=20, pady=10, fill="x")
    label_tasa = tk.Label(frame_res, text="Tasa mensual: --",
                          font=("Arial", 11))
    label_tasa.pack(anchor="w", pady=3)
    label_saldo_final = tk.Label(frame_res, text="Saldo final: --",
                                 font=("Arial", 11, "bold"))
    label_saldo_final.pack(anchor="w", pady=3)
    label_intereses = tk.Label(frame_res, text="Total intereses: --",
                               font=("Arial", 11))
    label_intereses.pack(anchor="w", pady=3)

    frame_tabla = tk.LabelFrame(ventana, text="Proyección mensual",
                                font=("Arial", 11, "bold"), padx=10, pady=10)
    frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)
    tabla = ttk.Treeview(frame_tabla, columns=("mes", "interes", "saldo"),
                         show="headings", height=10)
    tabla.heading("mes", text="Mes")
    tabla.heading("interes", text="Intereses")
    tabla.heading("saldo", text="Saldo final mes")
    tabla.column("mes", width=80, anchor="center")
    tabla.column("interes", width=220, anchor="e")
    tabla.column("saldo", width=220, anchor="e")
    tabla.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    sb.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=sb.set)

    entry_monto.focus()
    ventana.mainloop()


# ============================================================
# INICIO
# ============================================================

def main():
    if "--consola" in sys.argv:
        ejecutar_consola()
        return
    try:
        ejecutar_gui()
    except Exception:          # sin tkinter o sin pantalla (Colab)
        ejecutar_consola()


if __name__ == "__main__":
    main()