import math


def calc_n(vc: float, D: float) -> float:
    return (vc * 1000) / (math.pi * D)


def calc_vf(n: float, z: int, fz: float) -> float:
    return n * z * fz


def calc_Q(ap: float, ae: float, vf: float) -> float:
    return (ap * ae * vf) / 1000


def calc_kc(kc11: float, mc: float, h: float) -> float:
    return kc11 * (h ** (-mc))


def calc_Fc(kc: float, ap: float, h: float) -> float:
    return kc * ap * h


def calc_Pc(Fc: float, vc: float) -> float:
    return (Fc * vc) / 60000


def calc_Pa(Pc: float, eta: float) -> float:
    return Pc / eta


def calc_M(Fc: float, D: float) -> float:
    return (Fc * D) / 2000


def calc_Rz(fz: float, re: float) -> float:
    """Theoretische Rautiefe in µm (Formel nach DIN)."""
    if re <= 0:
        return 0.0
    return (fz ** 2) / (8 * re) * 1000


def calculate_all(
    vc: float,
    D: float,
    z: int,
    fz: float,
    ap: float,
    ae: float,
    re: float,
    kc11: float,
    mc: float,
    eta: float,
    n_max: float | None = None,
    P_max: float | None = None,
) -> dict:
    n  = calc_n(vc, D)
    vf = calc_vf(n, z, fz)
    Q  = calc_Q(ap, ae, vf)
    h  = fz  # Näherung bei κ = 90°
    kc = calc_kc(kc11, mc, h)
    Fc = calc_Fc(kc, ap, h)
    Pc = calc_Pc(Fc, vc)
    Pa = calc_Pa(Pc, eta)
    M  = calc_M(Fc, D)
    Rz = calc_Rz(fz, re)

    warnings: list[str] = []
    if n_max and n > n_max:
        warnings.append(f"Drehzahl {n:,.0f} U/min überschreitet Maschinenmax. {n_max:,.0f} U/min")
    if P_max and Pa > P_max:
        warnings.append(f"Antriebsleistung {Pa:.2f} kW überschreitet verfügbare {P_max:.1f} kW")

    return {
        "n": n, "vf": vf, "Q": Q,
        "kc": kc, "Fc": Fc, "Pc": Pc, "Pa": Pa,
        "M": M, "Rz": Rz, "hex": h,
        "warnings": warnings,
    }
