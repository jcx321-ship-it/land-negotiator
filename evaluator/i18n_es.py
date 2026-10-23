"""Spanish rendering of the engine's output strings (display only; the engine itself stays in English).
Applied by webapi when lang == "es". Verdict and status codes are left untouched (the UI keys on them)."""
from __future__ import annotations
import re

KEEP_KEYS = {"verdict", "case_id", "vocation", "exit_route", "binding_hurdle", "direction", "band",
             "memo_md", "url", "title", "thesis_id", "developer_id", "market", "status"}
KEEP_TOP = {"label"}

EXACT = {
    "equity, with debt when the financing switch is on": "capital propio, con deuda cuando el crédito está activado",
    "equity multiple": "múltiplo de capital",
    "hard construction costs": "costos duros de construcción",
    "comparables (B)": "comparables (B)",
    "project (A)": "proyecto (A)",
    "Quick test only (Founder): admissible % rises in expensive high-demand areas, falls in cheap abundant product.":
        "Solo prueba rápida (Founder): el % admisible sube en zonas caras de alta demanda y baja en producto barato y abundante.",
    "Quick test (Founder): standard hard costs are ~40% of the sales value. Above it, check the specification or whether the sale price is too low for the product.":
        "Prueba rápida (Founder): los costos duros estándar son ~40% del valor de venta. Si están arriba, revisa la especificación o si el precio de venta es bajo para el producto.",
    "Founder's reference: land 20 / hard 40 / soft+sales 10 / finance 5 / contingency 5 / margin 20 (share of sales value). The margin is not the hurdle: the 20% IRR and 2.0x approve.":
        "Referencia del Founder: tierra 20 / duros 40 / suaves+ventas 10 / financiero 5 / contingencias 5 / margen 20 (sobre el valor de venta). El margen no es el umbral: aprueban la TIR de 20% y el 2.0x.",
    "Replaceable: develop, sell and recycle capital (Founder rule).": "Reemplazable: desarrollar, vender y reciclar el capital (regla del Founder).",
    "Irreplaceable / premium: evaluate keeping it as a rental asset (Founder rule).": "Irreemplazable / premium: evaluar conservarlo como activo en renta (regla del Founder).",
    "Critical feasibility still open: structure the deal so capital is not exposed until it is accredited.":
        "Factibilidad crítica abierta: estructura el trato para no exponer capital hasta que se acredite.",
    "Price fits, but a critical risk is open: tie payments to its accreditation before exposure.":
        "El precio cabe, pero hay un riesgo crítico abierto: amarra los pagos a su acreditación antes de exponer capital.",
    "The 12% yield on cost is the development target, the exit cap is the mechanism, the 20% IRR approves (Founder).":
        "El 12% de rendimiento sobre costo es la meta de desarrollo, el cap de salida es el mecanismo y la TIR de 20% aprueba (Founder).",
    "signed buyer's cap (forward sale)": "cap del comprador firmado (venta anticipada)",
    "No closed land comparables: value B unavailable; max bid rests on the project alone.":
        "Sin comparables cerrados de terreno: no hay valor B; la oferta máxima se apoya solo en el proyecto.",
    "above standard": "arriba del estándar",
    "Title certainty not yet established by DD.": "La certeza jurídica aún no se acredita en la due diligence.",
    "This vocation's protocol is not fully reconstructed from the Founder's evidence; no price is invented.":
        "El protocolo de esta vocación aún no está completo con la evidencia del Founder; no se inventa un precio.",
    "No certainty of title or of the seller's power to transfer.": "No hay certeza jurídica ni de la facultad del vendedor para transmitir.",
    "The offer is outside the developer's investment thesis: discarded before any number is run.":
        "La oferta está fuera de la tesis de inversión del desarrollador: se descarta antes de correr cualquier número.",
    "user in talks but no binding LOI: treated as speculative": "usuario en pláticas pero sin carta de intención vinculante: se trata como especulativo",
    "no identified user: speculative development": "sin usuario identificado: desarrollo especulativo",
    "identified user with a binding letter of intent": "usuario identificado con carta de intención vinculante",
    "Pre-let status": "Precolocación", "Tenant credit": "Crédito del inquilino", "Lease term": "Plazo del contrato",
    "Competing vacancy": "Vacancia de la competencia", "Hard-to-replicate location": "Ubicación difícil de replicar",
    "Lease designed to securitize the rents": "Contrato diseñado para bursatilizar las rentas",
    "rent locked in under a securitizable contract": "renta amarrada en un contrato bursatilizable",
    "exceptional location: patrimonial value and appreciation": "ubicación excepcional: valor patrimonial y plusvalía",
    "The investor's target IRR approves (20% pre-tax is the development reference). Risk factors are evidence, not automatic adjustments. Only a binding LOI makes the user 'identified'.":
        "Aprueba la TIR objetivo del inversionista (20% antes de impuestos es la referencia de desarrollo). Los factores de riesgo son evidencia, no ajustes automáticos. Solo una carta de intención vinculante hace 'identificado' al usuario.",
    "FICTITIOUS demo case - invented numbers, no real parcel, no client data": "Caso de demo FICTICIO: números inventados, sin predio real ni datos de clientes",
    "standard commercial exit cap": "cap de salida comercial estándar",
    "exit cap given (size and segment)": "cap de salida dado (tamaño y segmento)",
    "cap agreed with the identified user / buyer": "cap pactado con el usuario / comprador identificado",
    # demo-case scenario names and evidence (fictitious case data)
    "Prices -5% (two recent projects discounted)": "Precios -5% (dos proyectos recientes con descuento)",
    "Absorption 2/month (zone slowdown)": "Absorción 2/mes (desaceleración de la zona)",
    "Prices +5% (best recent launch)": "Precios +5% (mejor lanzamiento reciente)",
    "one launch sold above list": "un lanzamiento vendió arriba de lista",
    "Absorption 4/month (anchor employer arriving)": "Absorción 4/mes (llega un empleador ancla)",
    "No signed buyer: speculative exit at 10% cap": "Sin comprador firmado: salida especulativa a cap 10%",
    "binding LOI not yet signed": "carta vinculante aún no firmada",
    "Achieved rent -8% vs asking": "Renta lograda -8% vs pedida",
    "latest signed lease below asking": "el último contrato firmado quedó abajo de lo pedido",
    "Lease-up 6 units/month": "Colocación 6 unidades/mes",
    "competing building opened nearby": "abrió un edificio competidor cerca",
    "Lot prices -8% (new competing park)": "Precio de lotes -8% (nuevo parque competidor)",
    "competing park announced": "se anunció un parque competidor",
    "Anchor signs the binding LOI (AAA, 15 years, 9.5% cap)": "El ancla firma la carta vinculante (AAA, 15 años, cap 9.5%)",
    "pharmacy chain LOI in negotiation": "carta de intención de la cadena de farmacias en negociación",
    "Exit by selling rental units to small investors (10% cap)": "Salida vendiendo unidades rentadas a pequeños inversionistas (cap 10%)",
    "recent unit sales in comparable centres": "ventas recientes de unidades en centros comparables",
    "Achieved rent -10%": "Renta lograda -10%",
    "two recent leases below asking": "dos contratos recientes abajo de lo pedido",
    "Large-tract land-banking files and a commissioned territorial intelligence study (2019).":
        "Expedientes de reserva territorial de grandes extensiones y un estudio de inteligencia territorial encargado (2019).",
    "Read the city: historical growth and direction of the urban footprint; is the urban area under pressure (prices up, people no longer fit)?":
        "Leer la ciudad: crecimiento histórico y dirección de la mancha urbana; ¿la zona urbana está presionada (precios al alza, la gente ya no cabe)?",
    "Identify change drivers: announced investment, roads, rail, energy, anchor projects; current state -> drivers -> possible future state.":
        "Identificar detonadores: inversión anunciada, carreteras, tren, energía, proyectos ancla; estado actual -> detonadores -> estado futuro posible.",
    "Read economic corridors and their stage, not just distance to the centre.": "Leer los corredores económicos y su etapa, no solo la distancia al centro.",
    "Normative path as value creation (urban development plan, partial plan, master plan) - underwrite on CURRENT use; the change is upside.":
        "La ruta normativa como creación de valor (plan de desarrollo urbano, plan parcial, plan maestro): se valúa con el uso ACTUAL; el cambio es upside.",
    "Gross -> cessions/infrastructure -> usable -> monetizable land before any value per m2.":
        "Superficie bruta -> donaciones/infraestructura -> aprovechable -> monetizable, antes de cualquier valor por m2.",
    "Cost floor per m2 (land + accumulated holding costs: trust, legal, management) vs. today's sale value.":
        "Piso de costo por m2 (tierra + costos de tenencia acumulados: fideicomiso, legal, administración) vs. valor de venta hoy.",
    "Title regularisation and hectare reconciliation as the dominant risk; pay against milestones.":
        "La regularización del título y la conciliación de hectáreas son el riesgo dominante; pagar contra hitos.",
}

PATTERNS = [
    (r"^(\d+) asking-price comparable\(s\) ignored: only closed transactions count \(hypothesis pending Founder confirmation\)\.$",
     r"\1 comparable(s) de precio de lista ignorado(s): solo cuentan operaciones cerradas (hipótesis pendiente de confirmación del Founder)."),
    (r"^Asking price fits under the maximum bid \((.+?) binds\) at 20% pre-tax IRR and 2\.0x equity multiple\.$",
     r"El precio pedido cabe bajo la oferta máxima (manda \1) con TIR de 20% antes de impuestos y múltiplo de 2.0x."),
    (r"^Asking price fits under the maximum bid \((.+?) binds\) at (.+?) pre-tax IRR\.$",
     r"El precio pedido cabe bajo la oferta máxima (manda \1) con TIR de \2 antes de impuestos."),
    (r"^Deferral / payment in kind adds ([\d,]+) of supportable land value vs\. paying cash upfront\.$",
     r"El diferido / pago en especie agrega \1 de valor soportable del terreno vs. pagar de contado."),
    (r"^Financing on: (\d+)% of hard construction costs at ([\d.]+)%; hurdle that binds: (.+)\.$",
     lambda m: f"Con crédito: {m[1]}% de los costos duros de construcción al {m[2]}%; umbral que manda: {tr(m[3])}."),
    (r"^Asking exceeds the maximum bid by (\d+)% and no market scenario supports it\.$",
     r"Lo pedido supera la oferta máxima en \1% y ningún escenario de mercado lo soporta."),
    (r"^Asking exceeds the base maximum bid by (\d+)%; only the most favourable market scenario supports it: negotiate or restructure\.$",
     r"Lo pedido supera la oferta máxima base en \1%; solo el escenario de mercado más favorable lo soporta: negociar o reestructurar."),
    (r"^Supported only if: (.+)\. Do not pay the asking price before that is secured\.$",
     lambda m: f"Solo se soporta si: {'; '.join(tr(x) for x in m[1].split('; '))}. No pagar lo pedido antes de asegurarlo."),
    (r"^User status: (.+)\.$", lambda m: f"Estatus del usuario: {tr(m[1])}."),
    (r"^Yield on total cost at the asking price: ([\d.]+%) vs the 12% development target \(meets it\)\.$",
     r"Rendimiento sobre costo total al precio pedido: \1 vs la meta de desarrollo de 12% (la cumple)."),
    (r"^Yield on total cost at the asking price: ([\d.]+%) vs the 12% development target \(below it\)\.$",
     r"Rendimiento sobre costo total al precio pedido: \1 vs la meta de desarrollo de 12% (queda abajo)."),
    (r"^tenant rated (.+)$", r"inquilino con calificación \1"),
    (r"^(\d+)-year mandatory term$", r"plazo forzoso de \1 años"),
    (r"^(\d+)% vacancy in comparable centres nearby$", r"\1% de vacancia en centros comparables cercanos"),
    (r"^units sold to small investors at ([\d.]+%) cap over (\d+) months$", r"unidades vendidas a pequeños inversionistas a cap \1 en \2 meses"),
    (r"^held (\d+) years, then sold \((.+)\)$", lambda m: f"se conserva {m[1]} años y luego se vende ({tr(m[2])})"),
    (r"^Vocation (\S+) vs thesis (\S+)$", r"Vocación \1 vs tesis \2"),
    (r"^Market (.+) vs (.+)$", r"Mercado \1 vs \2"),
    (r"^Land ([\d,]+) m2 vs range (.+) m2$", r"Terreno \1 m2 vs rango \2 m2"),
    (r"^Ticket (.+) vs max (.+)$", r"Ticket \1 vs máx. \2"),
    (r"^frontage_m (\S+) vs min (\S+)$", r"Frente \1 m vs mín. \2 m"),
    (r"^parking_spaces (\S+) vs min (\S+)$", r"Cajones \1 vs mín. \2"),
    (r"^(\w+) (\S+) vs (min|max) (\S+)$", lambda m: f"{m[1]} {m[2]} vs {'mín.' if m[3]=='min' else 'máx.'} {m[4]}"),
]
_COMPILED = [(re.compile(p), r) for p, r in PATTERNS]


def tr(s: str) -> str:
    if s in EXACT:
        return EXACT[s]
    for rx, rep in _COMPILED:
        m = rx.match(s)
        if m:
            return rep(m) if callable(rep) else m.expand(rep)
    return s


def translate(obj, key=None):
    if isinstance(obj, dict):
        return {k: (v if k in KEEP_KEYS else translate(v, k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate(x, key) for x in obj]
    if isinstance(obj, str):
        return tr(obj)
    return obj
