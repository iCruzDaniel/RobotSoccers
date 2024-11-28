from oculus import * 
from paquetes.controller_ui import *

class Tree:
    def __init__(self):

        self.index_desition  = {
            #    KEY: movimiento|PWM|pateo?,
            "vvvffv": "F1500", 
            "vvvfff": "X1500",

            "vvfffv": "F1500",
            "vvffff": "X1500", 

            "vfvffv": "F1500",
            "vfvfff": "X1500",

            "vffffv": "F1500",
            "vfffff": "X1500",

            "fvvffv": "F1500",
            "fvvffv": "X1500",

            "fvfffv": "F1500",
            "fvffff": "X1500",

            "ffvffv": "F1500",
            "ffvfff": "X1500",

            "fffffv": "F1500",
            "ffffff": "X1500"
        }
        
    def eval(self, id_maquina):
        ID = id_maquina-1
        current_key = "" 
        # -- valor = valor_si_true if condicion else valor_si_false
        #eval 1 
        current_key += "v" if camara.Posicion_pelota() else "f" 

        #eval 2
        current_key += "v" if camara.mas_cerca_arco_local(ID) else "f" 

        #eval 3
        current_key += "v" if camara.mas_cerca_pelota(ID) else "f" 

        #eval 4
        current_key += "v" if camara.posesion_pelota(ID) else "f" 

        #eval 5
        current_key += "v" if camara.alineado_pelota(ID) else "f" 

        #eval 6
        current_key += "v" if camara.desplazado_hacia(ID) else "f" 
        
        
        try: 
            print(self.index_desition[current_key])
            return self.index_desition[current_key]
    
        except:
            pass




if __name__ == "__main__":
    tree = Tree()
    
    print(tree.eval())
    
    pass