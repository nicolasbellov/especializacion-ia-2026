r"""U2.6/B30-L1: costo humano estimado de etiquetado y segunda revision.

Reproduce los ejemplos de Skillnest y aplica el MISMO supuesto didactico
al dataset propio de Booking Core AI. Todos los valores monetarios son
estimaciones ilustrativas en USD; NO representan costos reales facturados.

PowerShell:
    .\.venv\Scripts\python.exe .\costos_personalizacion.py

No crea trabajos de tuning ni se conecta a Gemini.
"""

from __future__ import annotations

from dataclasses import dataclass

from dataset_tuning import ejemplos_raw


def estimar_costo_de_etiquetar(
    num_ejemplos: float, minutos_por_ejemplo: float, costo_por_hora: float
) -> tuple[float, float]:
    """Estimacion lineal de horas y USD, segun la formula oficial B30/L1."""
    if num_ejemplos < 0 or minutos_por_ejemplo < 0 or costo_por_hora < 0:
        raise ValueError("Los valores de la estimacion no pueden ser negativos")
    horas = (num_ejemplos * minutos_por_ejemplo) / 60
    costo = horas * costo_por_hora
    return horas, costo


@dataclass(frozen=True)
class CostoEtiquetado:
    ejemplos: int
    ejemplos_revisados: float
    horas_base: float
    costo_base_usd: float
    horas_revision: float
    costo_revision_usd: float

    @property
    def horas_totales(self) -> float:
        return self.horas_base + self.horas_revision

    @property
    def costo_total_usd(self) -> float:
        return self.costo_base_usd + self.costo_revision_usd

    @property
    def jornadas_ocho_horas(self) -> float:
        return self.horas_totales / 8


def estimar_con_segunda_revision(
    num_ejemplos: int,
    minutos_por_ejemplo: float,
    costo_por_hora: float,
    fraccion_revision: float,
    minutos_por_revision: float,
) -> CostoEtiquetado:
    """Aplica costo base y segunda revision a una fraccion del dataset."""
    if not isinstance(num_ejemplos, int) or num_ejemplos < 0:
        raise ValueError("num_ejemplos debe ser un entero no negativo")
    if not 0 <= fraccion_revision <= 1:
        raise ValueError("fraccion_revision debe estar entre 0 y 1")
    horas_base, costo_base = estimar_costo_de_etiquetar(
        num_ejemplos, minutos_por_ejemplo, costo_por_hora
    )
    revisados = num_ejemplos * fraccion_revision
    horas_revision, costo_revision = estimar_costo_de_etiquetar(
        revisados, minutos_por_revision, costo_por_hora
    )
    return CostoEtiquetado(
        ejemplos=num_ejemplos,
        ejemplos_revisados=revisados,
        horas_base=horas_base,
        costo_base_usd=costo_base,
        horas_revision=horas_revision,
        costo_revision_usd=costo_revision,
    )


def mostrar_caso(titulo: str, c: CostoEtiquetado) -> None:
    print(f"\n=== {titulo} ===")
    print(f"ejemplos: {c.ejemplos}")
    print(f"segunda revision: {c.ejemplos_revisados:g} ejemplos")
    print(f"etiquetado base: {c.horas_base:.2f} horas, aprox USD {c.costo_base_usd:.2f}")
    print(f"segunda revision: {c.horas_revision:.2f} horas, aprox USD {c.costo_revision_usd:.2f}")
    print(f"total: {c.horas_totales:.2f} horas, aprox USD {c.costo_total_usd:.2f}")
    print(f"jornadas de 8 horas: {c.jornadas_ocho_horas:.1f}")


def main() -> None:
    print("=== EJEMPLOS OFICIALES: 8 VS 200 ===")
    horas_8, costo_8 = estimar_costo_de_etiquetar(8, 5, 25)
    horas_200, costo_200 = estimar_costo_de_etiquetar(200, 5, 25)
    print(f"8 ejemplos: {horas_8:.2f} horas, aprox USD {costo_8:.2f}")
    print(f"200 ejemplos: {horas_200:.2f} horas, aprox USD {costo_200:.2f}")
    print(f"factor de crecimiento: {horas_200 / horas_8:.1f}x")

    # Mini-ejercicio EXACTO del curso: 500, 4 min, USD 20/h,
    # 20 % de segunda revision de 2 minutos cada una.
    curso = estimar_con_segunda_revision(500, 4, 20, 0.20, 2)
    mostrar_caso("MINI-EJERCICIO SKILLNEST: 500 EJEMPLOS", curso)

    # Extension propia: contar el dataset versionado B29 y aplicar los
    # mismos supuestos del curso (NO horas ni tarifas medidas en el proyecto).
    booking_core = estimar_con_segunda_revision(
        len(ejemplos_raw), 4, 20, 0.20, 2
    )
    mostrar_caso("BOOKING CORE AI: ESCENARIO HIPOTETICO", booking_core)

    assert curso.ejemplos_revisados == 100
    assert round(curso.horas_totales, 2) == 36.67
    assert round(curso.costo_total_usd, 2) == 733.33
    assert len(ejemplos_raw) == 20, "Revisar el caso de estudio si cambia el dataset"
    print("\nCOSTOS B30/L1: CALCULOS VALIDADOS (ESTIMACIONES, SIN API)")


if __name__ == "__main__":
    main()
