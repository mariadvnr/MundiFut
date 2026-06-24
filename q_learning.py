import numpy as np
import os
import random

class QLearning:
    
    def __init__(self, total_estados=13, total_acciones=13, epsilon= 0.3, alpha=0.5):
        self.estados = total_estados
        self.acciones = total_acciones
        self.epsilon = epsilon
        self.alpha = alpha       
        self.archivo_memoria = 'memoria_agente.npy'
        
        self.cargar_memoria()

    def cargar_memoria(self):
        if os.path.exists(self.archivo_memoria):
            self.q_tabla = np.load(self.archivo_memoria)
        else:
            self.q_tabla = np.zeros((self.estados, self.acciones))

    def guardar_memoria(self):
        np.save(self.archivo_memoria, self.q_tabla)

   
    def elegir_accion(self, estado):

        numrandon = random.uniform(0, 1)
        
        if numrandon < self.epsilon:
            return random.randint(0, self.acciones - 1)
        else:
            return np.argmax(self.q_tabla[estado])

  
    def actualizar_q(self, anterior, estado, accion, recompensa, guardar=True):
        """Aplica la fórmula"""

        q_nuevo = anterior + self.alpha * (recompensa - anterior)
        
        self.q_tabla[estado, accion] = q_nuevo
        
        if guardar:
            self.guardar_memoria()
        
        return q_nuevo