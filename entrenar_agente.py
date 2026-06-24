import time
import random
import numpy as np
from q_learning import QLearning

def entrenar(ciclos=10000):
    print(" INICIANDO ENTRENAMIENTO DEL AGENTE Q LEARNING")

    agente = QLearning()
    agente.q_tabla.fill(0.0)
    tiempo_inicio = time.perf_counter()
    total_estados = agente.estados
    
    for ciclo in range(1, ciclos + 1):
        estado = random.randint(0, total_estados - 1)

        accion = agente.elegir_accion(estado)

        recompensa = 1 if accion == estado else -1

        q_anterior = agente.q_tabla[estado, accion]
        agente.actualizar_q(q_anterior, estado, accion, recompensa, guardar=False)

        if ciclo % max(1, ciclo // 10) == 0:
            print(f"{ciclo}/{ciclos} ciclos")
            
    #agente.guardar_memoria()
    
    tiempo_fin = time.perf_counter()
    tiempo_transcurrido = tiempo_fin - tiempo_inicio
    
    print(" \n¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
    print(f"Tiempo transcurrido: {tiempo_transcurrido:.6f} segundos")
    print(f"Número de ciclos entrenados: {ciclos}")
    print(f"Promedio de tiempo por ciclo: {tiempo_transcurrido / ciclos:.8f} segundos")
    

    aciertos = 0
    print("\n--- Verificación del Aprendizaje ---")
    for estado in range(total_estados):
        accion_optima = np.argmax(agente.q_tabla[estado])

        convergido = "Correcto" if accion_optima == estado else "Incorrecto"
        if accion_optima == estado:
            aciertos += 1
        print(f"Estado {estado:2d} -> Acción recomendada: {accion_optima:2d} | Q-Valor: {agente.q_tabla[estado, accion_optima]:.4f} [{convergido}]")
        
    precision = (aciertos / total_estados) * 100
    print(f"\nPrecisión final del agente: {precision:.1f}% ({aciertos}/{total_estados} estados convergidos)")
    
    if precision == 100.0:
        print("¡El agente ha aprendido la asociación correcta para todos los estados!")
    else:
        print("El agente aún no ha convergido por completo. Considera entrenar con más episodios.")

if __name__ == "__main__":
    import sys
    n_ciclos = 1000
    if len(sys.argv) > 1:
        try:
            n_ciclos = int(sys.argv[1])
        except ValueError:
            sys.exit(1)
            
    entrenar(n_ciclos)
