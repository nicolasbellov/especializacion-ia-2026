import criterios_demo as cd


def consultar_roto(pregunta):
    return {"respuesta": "Tienes 30 dias desde la compra para devolver."}


cd.consultar = consultar_roto
cd.ejecutar(cd.CRITERIOS)
