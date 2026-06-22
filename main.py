import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from q_learning import QLearning
from basededatos import estados_posib, acciones_posib
import numpy as np


agente = QLearning(epsilon=0.3, alpha=0.5)


estado_actual = None
accion_actual = None

def clasificar_mensaje(mensaje_usuario):
    """Busca palabras clave simples para determinar el Estado."""
   
    palabras_mensaje = mensaje_usuario.lower().split() 
    
    for estado, palabras_clave in estados_posib.items():
        for palabra_clave in palabras_clave:
            if palabra_clave in palabras_mensaje: 
                return estado
                
    return 11 


def enviar_mensaje():
    global estado_actual, accion_actual
    
    mensaje_usuario = entry_mensaje.get()
    if not mensaje_usuario.strip():
        return 
        
    chat_box.insert(tk.END, f"Tú: {mensaje_usuario}\n")
    entry_mensaje.delete(0, tk.END) 
    
    estado_actual = clasificar_mensaje(mensaje_usuario)
    accion_actual = agente.elegir_accion(estado_actual)
    respuesta_bot = acciones_posib[accion_actual]
    
    chat_box.insert(tk.END, f"Bot: {respuesta_bot}\n")
    chat_box.insert(tk.END, "-"*40 + "\n")
    chat_box.see(tk.END) 
    
    btn_like.config(state=tk.NORMAL)
    btn_dislike.config(state=tk.NORMAL)

def evaluar_respuesta(recompensa):
    global estado_actual, accion_actual
    
    if estado_actual is not None and accion_actual is not None:
    
        q_anterior = agente.q_tabla[estado_actual, accion_actual]
        q_nuevo = agente.actualizar_q(estado_actual, accion_actual, recompensa)
        
        eval_texto = "+1 (Like)" if recompensa == 1 else "-1 (Dislike)"
        chat_box.insert(tk.END, f"[Evaluado con recompensa: {eval_texto}]\n\n")
        chat_box.see(tk.END)
        
        actualizar_panel_matematico(q_anterior, q_nuevo, recompensa)
        actualizar_tabla_visual()
        
        btn_like.config(state=tk.DISABLED)
        btn_dislike.config(state=tk.DISABLED)
        
        estado_actual = None
        accion_actual = None

def actualizar_panel_matematico(q_anterior, q_nuevo, recompensa):

    """Actualiza el texto de la ecuación de Bellman."""
    texto = (
        f"Actualización Matemática:\n"
        f"Recompensa (R) = {recompensa}\n"
        f"Clasificacion de texto (Estado) = {estado_actual}\n"
        f"Q_anterior(S{estado_actual}, A{accion_actual}) = {q_anterior:.2f}\n\n"
        f"Fórmula Aplicada:\n"
        f"Q(S{estado_actual}, A{accion_actual}) = {q_anterior:.2f} + {agente.alpha} * ({recompensa} - {q_anterior:.2f})\n"
        f"Q_nuevo = {q_nuevo:.2f}"
    )
    label_ecuacion.config(text=texto)

def actualizar_tabla_visual():
    """Recarga el widget ttk.Treeview con la matriz Q actualizada."""
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
        
        chat_box.insert(tk.END, "\n[SISTEMA]: Se ha borrado toda la memoria del agente.\n")
        chat_box.see(tk.END)

# ==========================================
# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA (GUI)
# ==========================================
ventana = tk.Tk()
ventana.title("MundiFut")
ventana.geometry("1000x700") # Tamaño de la ventana
ventana.configure(bg="#f0f0f0")

# --- PANEL CHAT ---
frame_chat = tk.Frame(ventana, bg="#f0f0f0")
frame_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

lbl_titulo_chat = tk.Label(frame_chat, text="ChatBot MundiFut", font=("Frekuent Mono", 14, "bold"), bg="#c5dfc3", fg="black", pady=5)
lbl_titulo_chat.pack(fill=tk.X)

# Caja de texto del chat
chat_box = tk.Text(frame_chat, height=10, width=100, font=("", 11))
chat_box.pack(pady=10, fill=tk.BOTH, expand=True)

# Controles de entrada
frame_controles = tk.Frame(frame_chat, bg="#f0f0f0")
frame_controles.pack(fill=tk.X)

entry_mensaje = tk.Entry(frame_controles, font=("Arial", 12))
entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

btn_enviar = tk.Button(frame_controles, text="Enviar", bg="#3b82f6", fg="white", font=("Arial", 10, "bold"), command=enviar_mensaje)
btn_enviar.pack(side=tk.RIGHT)

# Botones de evaluación
frame_evaluacion = tk.Frame(frame_chat, bg="#f0f0f0")
frame_evaluacion.pack(fill=tk.X, pady=10)

btn_like = tk.Button(frame_evaluacion, text="👍 Like (+1)", bg="#4ade80", command=lambda: evaluar_respuesta(1), state=tk.DISABLED)
btn_like.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_dislike = tk.Button(frame_evaluacion, text="👎 Dislike (-1)", bg="#f87171", command=lambda: evaluar_respuesta(-1), state=tk.DISABLED)
btn_dislike.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)


# --- PANEL DERECHO: CEREBRO DEL AGENTE ---
frame_cerebro = tk.Frame(ventana, bg="white", relief=tk.GROOVE, borderwidth=2)
frame_cerebro.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

lbl_titulo_cerebro = tk.Label(frame_cerebro, text="Cerebro del Agente: Q-Learning", font=("Arial", 14, "bold"), fg="#2563eb", bg="white")
lbl_titulo_cerebro.pack(anchor="w", padx=10, pady=(10, 0))

lbl_info = tk.Label(frame_cerebro, text=f"Epsilon (ε): {agente.epsilon} | Tasa de Aprendizaje (α): {agente.alpha}", font=("Arial", 10, "italic"), bg="white")
lbl_info.pack(anchor="w", padx=10, pady=5)

# Botón para borrar entrenamiento (color rojo #ef4444 para advertencia)
btn_borrar_memoria = tk.Button(
    frame_cerebro, 
    text=" Borrar Entrenamiento", 
    bg="#ef4444", 
    fg="white", 
    font=("Arial", 10, "bold"), 
    command=reiniciar_entrenamiento
)
btn_borrar_memoria.pack(anchor="w", padx=10, pady=5)

# --- TABLA Q (Treeview) ---
# Creamos las columnas dinámicamente según el número de acciones
columnas = ["Estado"] + [f"A{i}" for i in range(agente.acciones)]
tabla_q = ttk.Treeview(frame_cerebro, columns=columnas, show="headings", height=15)

# Configurar encabezados y anchos
tabla_q.heading("Estado", text="Estado \\ Acción")
tabla_q.column("Estado", width=100, anchor="center")
for i in range(agente.acciones):
    tabla_q.heading(f"A{i}", text=f"A{i}")
    tabla_q.column(f"A{i}", width=50, anchor="center") # Columnas más pequeñas para que quepan las 13

# Agregar barra de desplazamiento (Scrollbar) para la tabla
scrollbar_x = ttk.Scrollbar(frame_cerebro, orient=tk.HORIZONTAL, command=tabla_q.xview)
tabla_q.configure(xscrollcommand=scrollbar_x.set)

tabla_q.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
scrollbar_x.pack(fill=tk.X, padx=10)

# Inicializar la vista de la tabla
actualizar_tabla_visual()

# --- PANEL DE LA ECUACIÓN DE BELLMAN ---
frame_ecuacion = tk.Frame(frame_cerebro, bg="#1e293b", pady=15, padx=15)
frame_ecuacion.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

label_ecuacion = tk.Label(frame_ecuacion, text="Realiza una interacción para ver la actualización matemática...", 
                          font=("Courier New", 10), fg="white", bg="#1e293b", justify="left", anchor="w")
label_ecuacion.pack(fill=tk.X)

# --- ARRANQUE DE LA INTERFAZ ---
# ESTA ES LA LÍNEA MÁGICA QUE MANTIENE LA VENTANA ABIERTA
ventana.mainloop()