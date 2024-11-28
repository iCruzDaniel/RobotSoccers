from oculus import * 
from paquetes.controller_ui import *

class Tree:
    def __init__(self):

        self.index_desition  = {
            "vvvffv": "horario|baja|0",
            "vvvfff": "antihorario|baja|0",

            "vvfffv": "horario|baja|0",
            "vvffff": "antihorario|baja|0", 

            "vfvffv": "horario|baja|0",
            "vfvfff": "antihorario|baja|0",

            "vffffv": "horario|baja|0",
            "vfffff": "antihorario|baja|0",

            "fvvffv": "horario|baja|0",
            "fvvffv": "antihorario|baja|0",

            "fvfffv": "horario|baja|0",
            "fvffff": "antihorario|baja|0",

            "ffvffv": "horario|baja|0",
            "ffvfff": "antihorario|baja|0",

            "fffffv": "horario|baja|0",
            "ffffff": "antihorario|baja|0"
        }
        
    def eval(self):
        
        #current_key = ""
        
        #eval 1 -- valor = valor_si_true if condicion else valor_si_false
        current_key += "v" if camara.Posicion_pelota() else "f" 

        #eval 2
        current_key += "v" if camara.mas_cerca_arco_local() else "f" 

        #eval 3
        current_key += "v" if camara.mas_cerca_pelota() else "f" 

        #eval 4
        current_key += "v" if camara.posesion_pelota() else "f" 

        #eval 5
        current_key += "v" if camara.alineado_pelota() else "f" 

        #eval 6
        current_key += "v" if camara.desplazado_hacia() else "f" 
        
        
        try: 
            print(self.index_desition[current_key])
            return self.index_desition[current_key]
    
        except:
            pass




if __name__ == "__main__":
    tree = Tree()
    
    print(tree.eval())
    
    pass