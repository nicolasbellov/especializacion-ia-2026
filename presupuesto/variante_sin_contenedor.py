from presupuesto_alcance import funcionalidades, informe

sin_contenedor = [f for f in funcionalidades if f["id"] != "RF-03"]
informe(sin_contenedor)
