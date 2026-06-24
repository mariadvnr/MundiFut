import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from q_learning import QLearning
from basededatos import estados_posib, acciones_posib
import numpy as np


agente = QLearning()

estado_actual = None
accion_actual = None
btn_like = None
btn_dislike = None

def clasificar_mensaje(mensaje_usuario):
    """Busca palabras clave para determinar el Estado."""
    palabras_mensaje = mensaje_usuario.lower().split() 
    
    for estado, palabras_clave in estados_posib.items():
        for palabra_clave in palabras_clave:
            if palabra_clave in palabras_mensaje: 
                return estado
                
    return 11 


def agregar_mensaje_chat(remitente, texto):
    msg_container = tk.Frame(scrollable_frame, bg="#ffffff")
    
    if remitente == "usuario":
        bubble = tk.Frame(msg_container, bg="#4f46e5", bd=0)
        lbl_msg = tk.Label(
            bubble, 
            text=texto, 
            bg="#4f46e5", 
            fg="#ffffff", 
            font=("Segoe UI", 11), 
            wraplength=450, 
            justify="left",
            padx=12,
            pady=8,
        )
        lbl_msg.pack(fill=tk.BOTH, expand=True)
        bubble.pack(anchor="e", padx=(50, 10), pady=4)
        msg_container.pack(fill=tk.X, anchor="e")

    elif remitente == "agente":
        bubble = tk.Frame(msg_container, bg="#f1f5f9", bd=0)
        lbl_msg = tk.Label(
            bubble, 
            text=texto, 
            bg="#f1f5f9", 
            fg="#0f172a", 
            font=("Segoe UI", 11), 
            wraplength=450, 
            justify="left",
            padx=12,
            pady=8,
        )
        lbl_msg.pack(fill=tk.BOTH, expand=True)
        bubble.pack(side=tk.LEFT, padx=(10, 5), pady=4)
        
        global btn_like, btn_dislike
        
        frame_btns = tk.Frame(msg_container, bg="#ffffff")
        frame_btns.pack(side=tk.LEFT, padx=(5, 10), pady=4)
        
        btn_like = tk.Button(
            frame_btns, 
            text="Like", 
            font=("Segoe UI", 10, "bold"), 
            bd=0, 
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: evaluar_respuesta(1)
        )
        btn_like.pack(side=tk.LEFT, padx=2)
        
        btn_dislike = tk.Button(
            frame_btns, 
            text="Dislike", 
            font=("Segoe UI", 10, "bold"), 
            bd=0, 
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: evaluar_respuesta(-1)
        )
        btn_dislike.pack(side=tk.LEFT, padx=2)
        
        bind_hover(btn_like, "#059669", "#10b981")
        bind_hover(btn_dislike, "#dc2626", "#ef4444")
        
        btn_like.config(state=tk.DISABLED, bg="#e2e8f0", fg="#94a3b8")
        btn_dislike.config(state=tk.DISABLED, bg="#e2e8f0", fg="#94a3b8")
        
        msg_container.pack(fill=tk.X, anchor="w")

    else:
        lbl_msg = tk.Label(
            msg_container, 
            text=texto, 
            bg="#ffffff", 
            fg="#64748b", 
            font=("Segoe UI", 9, "italic"), 
            wraplength=500, 
            justify="left",
            pady=6
        )
        lbl_msg.pack(anchor="w")
        msg_container.pack(fill=tk.X, anchor="center")

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)


def enviar_mensaje(event=None):
    global estado_actual, accion_actual
    
    mensaje_usuario = entry_mensaje.get()
    if not mensaje_usuario.strip():
        return 
        
    agregar_mensaje_chat("usuario", mensaje_usuario)
    entry_mensaje.delete(0, tk.END) 
    
    estado_actual = clasificar_mensaje(mensaje_usuario)
    accion_actual = agente.elegir_accion(estado_actual)
    respuesta_bot = acciones_posib[accion_actual]
    
    agregar_mensaje_chat("agente", respuesta_bot)
    
    set_like_dislike_state(tk.NORMAL)


def evaluar_respuesta(recompensa):
    global estado_actual, accion_actual
    
    if estado_actual is not None and accion_actual is not None:
        q_anterior = agente.q_tabla[estado_actual, accion_actual]
        q_nuevo = agente.actualizar_q(q_anterior, estado_actual, accion_actual, recompensa)
        
        eval_texto = "+1 (Like)" if recompensa == 1 else "-1 (Dislike)"
        agregar_mensaje_chat("sistema", f"Respuesta evaluada con recompensa: {eval_texto}")
        
        actualizar_panel_matematico(q_anterior, q_nuevo, recompensa)
        actualizar_tabla_visual()
        
        set_like_dislike_state(tk.DISABLED)
        
        estado_actual = None
        accion_actual = None


def set_like_dislike_state(state):
    global btn_like, btn_dislike
    if btn_like is None or btn_dislike is None:
        return
    if state == tk.NORMAL:
        btn_like.config(state=tk.NORMAL, bg="#10b981", fg="white")
        btn_dislike.config(state=tk.NORMAL, bg="#ef4444", fg="white")
    else:
        btn_like.config(state=tk.DISABLED, bg="#e2e8f0", fg="#94a3b8")
        btn_dislike.config(state=tk.DISABLED, bg="#e2e8f0", fg="#94a3b8")


def actualizar_panel_matematico(q_anterior, q_nuevo, recompensa):
    texto = (
        f" Ecuación de Bellman Simplificada | Actualización en tiempo real:\n"
        f"  • Estado clasificado (S) = S{estado_actual}  |  Acción elegida (A) = A{accion_actual}\n"
        f"  • Recompensa recibida (R) = {recompensa}    |  Q-anterior(S{estado_actual}, A{accion_actual}) = {q_anterior:.4f}\n\n"
        f"  Fórmula: Q(S, A) = Q(S, A) + α * [ R - Q(S, A) ]\n"
        f"  Cálculo: Q(S{estado_actual}, A{accion_actual}) = {q_anterior:.4f} + {agente.alpha} * [ {recompensa} - {q_anterior:.4f} ]\n"
        f"  Resultado: Q-nuevo(S{estado_actual}, A{accion_actual}) = {q_nuevo:.4f}"
    )
    label_ecuacion.config(text=texto)


def actualizar_tabla_visual():
    for row in tabla_q.get_children():
        tabla_q.delete(row)
        
    for i in range(agente.estados):
        valores_fila = [f"{val:.2f}" for val in agente.q_tabla[i]]

        tabla_q.insert("", "end", values=([f"S{i}"] + valores_fila))


def reiniciar_entrenamiento():
    confirmacion = messagebox.askyesno(
        "Reiniciar Entrenamiento", 
        "¿Estás seguro de que deseas borrar todo el aprendizaje?\nEsta acción pondrá la Tabla Q a cero y no se puede deshacer."
    )
    
    if confirmacion:
        
        agente.q_tabla.fill(0.0)
        
        try:
            np.save("memoria_agente.npy", agente.q_tabla)
        except Exception as e:
            print(f"Error al guardar el reinicio: {e}")
            
        actualizar_tabla_visual()
        
        label_ecuacion.config(text="Realiza una interacción para ver la actualización matemática...")
        
        agregar_mensaje_chat("sistema", "Se ha borrado toda la memoria del agente.")


def bind_hover(widget, hover_bg, normal_bg):
    """Vincula eventos de hover para cambiar el color de fondo."""
    def on_enter(event):
        if str(widget['state']) != 'disabled':
            widget.config(bg=hover_bg)
    def on_leave(event):
        if str(widget['state']) != 'disabled':
            widget.config(bg=normal_bg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# Interfaz Grafica

ventana = tk.Tk()
ventana.title("MundiFut")
ventana.geometry("1000x750")
ventana.configure(bg="#f8fafc")

style = ttk.Style()
style.theme_use("clam")

style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#cbd5e1",
                troughcolor="#f8fafc",
                bordercolor="#f8fafc",
                lightcolor="#f8fafc",
                darkcolor="#f8fafc",
                arrowsize=0)
style.configure("Horizontal.TScrollbar",
                gripcount=0,
                background="#cbd5e1",
                troughcolor="#f8fafc",
                bordercolor="#f8fafc",
                lightcolor="#f8fafc",
                darkcolor="#f8fafc",
                arrowsize=0)

style.configure("Treeview",
                background="#ffffff",
                foreground="#0f172a",
                rowheight=26,
                fieldbackground="#ffffff",
                font=("Segoe UI", 10))

style.configure("Treeview.Heading",
                background="#f1f5f9",
                foreground="#475569",
                font=("Segoe UI", 10, "bold"),
                borderwidth=0,
                relief="flat")

style.map("Treeview.Heading",
          background=[('active', '#e2e8f0')])

# Panel del chat
frame_chat = tk.Frame(ventana, bg="#f8fafc")
frame_chat.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 10))

frame_header = tk.Frame(frame_chat, bg="#ffffff", bd=0, highlightbackground="#e2e8f0", highlightthickness=1)
frame_header.pack(fill=tk.X, ipady=8, ipadx=10)

lbl_titulo_chat = tk.Label(frame_header, text="MundiFut Chatbot", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#0f172a")
lbl_titulo_chat.pack(side=tk.LEFT, padx=10)

# Contenedor para burbujas de chat
chat_container = tk.Frame(frame_chat, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
chat_container.pack(pady=(10, 10), fill=tk.BOTH, expand=True)

canvas = tk.Canvas(chat_container, bg="#ffffff", bd=0, highlightthickness=0)
scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#ffffff")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def _on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind('<Configure>', _on_canvas_configure)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
scrollbar.pack(side="right", fill="y")

# Rueda del mouse en el chat
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _bind_to_mousewheel(event):
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def _unbind_from_mousewheel(event):
    canvas.unbind_all("<MouseWheel>")

canvas.bind("<Enter>", _bind_to_mousewheel)
canvas.bind("<Leave>", _unbind_from_mousewheel)

# Controles de entrada
frame_controles = tk.Frame(frame_chat, bg="#f8fafc")
frame_controles.pack(fill=tk.X, pady=(0, 10))

entry_container = tk.Frame(frame_controles, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1)
entry_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

entry_mensaje = tk.Entry(entry_container, font=("Segoe UI", 11), bg="#ffffff", fg="#0f172a", bd=0, insertbackground="#0f172a")
entry_mensaje.pack(fill=tk.X, padx=12, pady=8)
entry_mensaje.bind("<Return>", enviar_mensaje)

btn_enviar = tk.Button(
    frame_controles, 
    text="Enviar", 
    bg="#4f46e5", 
    fg="white", 
    font=("Segoe UI", 10, "bold"), 
    bd=0, 
    padx=18, 
    pady=8,
    cursor="hand2",
    activebackground="#4338ca",
    activeforeground="white",
    command=enviar_mensaje
)
btn_enviar.pack(side=tk.RIGHT)
bind_hover(btn_enviar, "#4338ca", "#4f46e5")

# Panel de tabla Q
frame_cerebro = tk.Frame(ventana, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
frame_cerebro.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

# Cabecera de cerebro
frame_brain_header = tk.Frame(frame_cerebro, bg="#ffffff")
frame_brain_header.pack(fill=tk.X, padx=15, pady=(15, 10))

frame_brain_title_container = tk.Frame(frame_brain_header, bg="#ffffff")
frame_brain_title_container.pack(side=tk.LEFT)

lbl_titulo_cerebro = tk.Label(frame_brain_title_container, text="Tabla Q", font=("Segoe UI", 12, "bold"), fg="#1e293b", bg="#ffffff")
lbl_titulo_cerebro.pack(anchor="w")

lbl_info = tk.Label(
    frame_brain_title_container, 
    text=f"Parámetros: Exploración (ε) = {agente.epsilon}  |  Tasa de Aprendizaje (α) = {agente.alpha}", 
    font=("Segoe UI", 9), 
    fg="#64748b", 
    bg="#ffffff"
)
lbl_info.pack(anchor="w", pady=(2, 0))

btn_borrar_memoria = tk.Button(
    frame_brain_header, 
    text="Borrar Entrenamiento", 
    bg="#ef4444", 
    fg="white", 
    font=("Segoe UI", 9, "bold"), 
    bd=0,
    padx=12,
    pady=6,
    cursor="hand2",
    activebackground="#dc2626",
    activeforeground="white",
    command=reiniciar_entrenamiento
)
btn_borrar_memoria.pack(side=tk.RIGHT)
bind_hover(btn_borrar_memoria, "#dc2626", "#ef4444")

# Tabla Q
columnas = ["Estado"] + [f"A{i}" for i in range(agente.acciones)]
tabla_q = ttk.Treeview(frame_cerebro, columns=columnas, show="headings", height=8)

tabla_q.heading("Estado", text="Estado \\ Acción")
tabla_q.column("Estado", width=90, anchor="center")
for i in range(agente.acciones):
    tabla_q.heading(f"A{i}", text=f"A{i}")
    tabla_q.column(f"A{i}", width=48, anchor="center")

scrollbar_x = ttk.Scrollbar(frame_cerebro, orient=tk.HORIZONTAL, command=tabla_q.xview, style="Horizontal.TScrollbar")
tabla_q.configure(xscrollcommand=scrollbar_x.set)

tabla_q.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 2))
scrollbar_x.pack(fill=tk.X, padx=15, pady=(0, 10))

# Inicializar la vista de la tabla
actualizar_tabla_visual()

# Panel de la Ecuacion
frame_ecuacion = tk.Frame(frame_cerebro, bg="#0f172a", pady=10, padx=15)
frame_ecuacion.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 15))

label_ecuacion = tk.Label(frame_ecuacion, text="Realiza una interacción para ver la actualización matemática...", 
                          font=("Consolas", 10), fg="#38bdf8", bg="#0f172a", justify="left", anchor="w")
label_ecuacion.pack(fill=tk.X)

# Inicio del programa
ventana.mainloop()
