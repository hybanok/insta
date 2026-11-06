import os, sys, shutil
sys.path.insert(0, "/home/claude/brand")
import numpy as np
from PIL import Image
import make_wod as mw

BASE = "/home/claude/week"
K, M = "k", "m"

DAYS = [
    dict(n=1, dia="Lunes", fecha="lunes 9 nov", slug="halterofilia", tag="HALTEROFILIA",
         warm=("ESPECÍFICO PARA SNATCH", [("3' row o bike suave", K), ("2 rondas (PVC y barra vacía)", M), ("10 pass-through con PVC", K), ("10 overhead squat con PVC", K), ("8 snatch grip good morning", K), ("6 muscle snatch", K), ("6 hang power snatch", K)]),
         st=("SNATCH", [("6 series de 2 reps", K), ("Series 1-2 al 60% del 1RM", K), ("Series 3-4 al 70% del 1RM", K), ("Series 5-6 al 75% del 1RM", K), ("Descanso 90 seg entre series", M), ("Técnica antes que carga", M)]),
         wod=("FOR TIME", "TIME CAP 12'", [("21-15-9", M), ("Power snatch (40/30 kg)", K), ("Burpees over the bar", K), ("Escala la carga a tu nivel", M)]),
         cap="""Hoy toca snatch: calentamiento, 6 series de 2 reps y un 21-15-9 con time cap de 12 minutos.

Desliza para ver el calentamiento para snatch, la fuerza y el WOD, en ese orden. Si el peso te hace dudar, bájalo. El cronómetro no te juzga.

Es un WOD de CrossFit pensado para entrenar halterofilia en un box, en casa o en el garaje, con la barra que tengas a mano. Si estás empezando, barra vacía y técnica.

Guárdalo para tu próxima sesión.

#crossfit #wod #snatch #halterofilia"""),

    dict(n=2, dia="Martes", fecha="martes 10 nov", slug="gimnasticos", tag="GIMNÁSTICOS",
         warm=("ESPECÍFICO PARA SHOULDER PRESS", [("3' row o bike suave", K), ("2 rondas", M), ("10 band pull-apart", K), ("10 pass-through con PVC", K), ("8 scap push-ups", K), ("8 press con PVC", K), ("6 strict press, barra vacía", K)]),
         st=("SHOULDER PRESS", [("5 series de 5 reps", K), ("Series 1-2 al 65% del 1RM", K), ("Series 3-5 al 70% del 1RM", K), ("Descanso 2 min entre series", M), ("Costillas abajo, glúteos firmes", M)]),
         wod=("AMRAP 14'", "GIMNÁSTICOS", [("Tantas rondas como puedas", M), ("6 handstand push-ups", K), ("10 toes-to-bar", K), ("14 air squats", K), ("Escala: pike y knee raises", M)]),
         cap="""Hoy toca shoulder press: 5 series de 5 y un AMRAP de 14 minutos con handstand push-ups y toes-to-bar.

Desliza para ver el calentamiento para shoulder press, la fuerza y el WOD. Si los handstand push-ups aún no te salen, pike push-ups. Escalar no es rendirse.

Es un WOD de CrossFit con gimnásticos para hacer en un box o con una barra de dominadas en casa. Costillas abajo y glúteos firmes en cada press.

Comenta cuántas rondas hiciste.

#crossfit #wod #handstandpushups #shoulderpress"""),

    dict(n=3, dia="Miércoles", fecha="miércoles 11 nov", slug="endurance", tag="ENDURANCE",
         warm=("ESPECÍFICO PARA BACK SQUAT", [("3' row o bike suave", K), ("2 rondas", M), ("10 air squats con pausa", K), ("8 goblet squats lentas", K), ("10 good mornings con PVC", K), ("6 back squats, barra vacía", K), ("30 seg movilidad de tobillo", K)]),
         st=("BACK SQUAT", [("4 series de 5 reps", K), ("Series 1-2 al 65% del 1RM", K), ("Series 3-4 al 75% del 1RM", K), ("Descanso 2 min entre series", M), ("Profundidad antes que carga", M)]),
         wod=("FOR TIME", "TIME CAP 30'", [("5 rondas", M), ("400 m run", K), ("15 cal row", K), ("30 double unders (60 simples)", K), ("Ritmo constante, sin sprint", M)]),
         cap="""Hoy toca back squat y 5 rondas de 400 m run, 15 cal row y 30 double unders. Time cap: 30 minutos.

Desliza para ver el calentamiento para back squat, las 4 series de 5 y el WOD de resistencia. Ritmo constante: si la ronda 1 te deja tirado, la 5 no existe.

Es un WOD de CrossFit de endurance para el box o para casa con una comba y una calle. Si no tienes remo, usa la bici.

Envíaselo a quien entrena contigo.

#crossfit #wod #backsquat #endurance"""),

    dict(n=4, dia="Jueves", fecha="jueves 12 nov", slug="mancuernas", tag="MANCUERNAS",
         warm=("ESPECÍFICO PARA BENCH PRESS", [("3' row suave", K), ("2 rondas", M), ("10 band pull-apart", K), ("10 push-ups con escápula", K), ("8 press con mancuerna ligera", K), ("6 bench press, barra vacía", K), ("10 rotaciones con banda", K)]),
         st=("BENCH PRESS", [("5 series de 3 reps", K), ("Series 1-2 al 70% del 1RM", K), ("Series 3-5 al 80% del 1RM", K), ("Descanso 2-3 min entre series", M), ("Sube carga solo con spotter", M)]),
         wod=("EMOM 20'", "4 ESTACIONES X 5 VUELTAS", [("Min 1: 10 DB snatch alternos", K), ("Min 2: 10 DB thrusters", K), ("Min 3: 10 burpees sobre DB", K), ("Min 4: 12 DB reverse lunges", K), ("Mancuernas de 22,5/15 kg", M)]),
         cap="""Hoy toca bench press: 5 series de 3 y un EMOM de 20 minutos con una sola mancuerna.

Desliza para ver el calentamiento para bench press, la fuerza y las 4 estaciones del WOD. Sube la carga solo si alguien te asegura. El ego no hace de spotter.

Es un WOD de CrossFit con mancuernas, pensado para el garaje o para el box, con una sola mancuerna por estación. En casa se hace igual.

Guárdalo para tu próximo jueves.

#crossfit #wod #benchpress #mancuernas"""),

    dict(n=5, dia="Viernes", fecha="viernes 13 nov", slug="calistenia", tag="CALISTENIA",
         warm=("ESPECÍFICO PARA DEADLIFT", [("3' row suave", K), ("2 rondas", M), ("10 good mornings con PVC", K), ("8 RDL con barra vacía", K), ("10 puentes de glúteo", K), ("6 deadlifts, barra vacía", K), ("30 seg plancha", K)]),
         st=("DEADLIFT", [("5 series de 3 reps", K), ("Series 1-2 al 70% del 1RM", K), ("Series 3-5 al 80% del 1RM", K), ("Descanso 2-3 min entre series", M), ("Espalda neutra, siempre", M)]),
         wod=("FOR TIME", "TIME CAP 18'", [("4 rondas", M), ("8 pull-ups", K), ("16 push-ups", K), ("24 air squats", K), ("32 sit-ups", K), ("Escala: bandas o ring rows", M)]),
         cap="""Hoy toca peso muerto: 5 series de 3 y un for time de 4 rondas solo con tu peso corporal.

Desliza para ver el calentamiento para peso muerto, la fuerza y el WOD de calistenia. Espalda neutra siempre: la carga es negociable, la espalda no.

Es un WOD de CrossFit que se hace en casa con una barra de dominadas, o con bandas si las dominadas aún no salen. Time cap de 18 minutos.

Comenta tu tiempo.

#crossfit #wod #calistenia #pesomuerto"""),

    dict(n=6, dia="Sábado", fecha="sábado 14 nov", slug="running", tag="RUNNING",
         warm=("ESPECÍFICO PARA FRONT SQUAT", [("3' trote suave", K), ("2 rondas", M), ("10 air squats con pausa", K), ("8 goblet squats con pausa", K), ("10 front squats con PVC", K), ("6 front squats, barra vacía", K), ("30 seg movilidad de rack", K)]),
         st=("FRONT SQUAT", [("4 series de 4 reps", K), ("Series 1-2 al 65% del 1RM", K), ("Series 3-4 al 75% del 1RM", K), ("Descanso 2 min entre series", M), ("Codos altos en todas las reps", M)]),
         wod=("FOR TIME", "TIME CAP 28'", [("4 rondas", M), ("800 m run", K), ("12 front squats (40/30 kg)", K), ("Ritmo cómodo en la carrera", M)]),
         cap="""Hoy toca front squat y 4 rondas de 800 m run con 12 front squats entre vuelta y vuelta.

Desliza para ver el calentamiento para front squat, la fuerza y el WOD de running. Codos altos y ritmo cómodo: los últimos 800 m se corren con lo que guardes al principio.

Es un WOD de CrossFit para el sábado, en la pista, el parque o el box. Time cap de 28 minutos.

Guárdalo para tu sábado de running.

#crossfit #wod #frontsquat #running"""),

    dict(n=7, dia="Domingo", fecha="domingo 15 nov", slug="mixto", tag="MIXTO",
         warm=("ESPECÍFICO PARA CLEAN & JERK", [("3' row o bike suave", K), ("2 rondas (PVC y barra vacía)", M), ("10 pass-through con PVC", K), ("8 front squats con PVC", K), ("6 muscle clean", K), ("6 hang power clean", K), ("4 push jerks", K)]),
         st=("CLEAN & JERK", [("EMOM 10': 1 clean + 1 jerk", K), ("Min 1-4 al 65% del 1RM", K), ("Min 5-8 al 75% del 1RM", K), ("Min 9-10 al 80% del 1RM", K), ("Si la barra se va, suéltala", M)]),
         wod=("AMRAP 15'", "MIXTO", [("Tantas rondas como puedas", M), ("5 clean & jerks (40/30 kg)", K), ("10 box jumps (60/50 cm)", K), ("15 cal bike", K)]),
         cap="""Hoy toca clean & jerk: EMOM de 10 minutos y un AMRAP de 15 con cleans, box jumps y bici.

Desliza para ver el calentamiento para clean & jerk, la fuerza y el WOD. Domingo mixto: de todo un poco y sin florituras. Si la barra se va, suéltala.

Es un WOD de CrossFit para cerrar la semana en el box, con barra, un cajón y una bici o un remo.

Envíaselo a tu compañero de entreno.

#crossfit #wod #cleanandjerk #halterofilia"""),
]


def alt(title, sub, lines):
    return f"Imagen negra y dorada con el logo de la cuenta. {title} ({sub.lower()}): " + "; ".join(t for t, _ in lines) + "."


if os.path.exists(BASE):
    shutil.rmtree(BASE)
os.makedirs(BASE + "/captions")
md = ["# Semana 1 · @wod.cada.dia", "",
      "Fechas propuestas: lunes 9 a domingo 15 de noviembre de 2026 (hora de Madrid). Pendiente de confirmar fecha y hora de cada publicación.", ""]
thumbs = []
for d in DAYS:
    folder = f"{BASE}/dia{d['n']}_{d['slug']}"
    wsub, wlines = d["warm"]; stsub, stlines = d["st"]; wt, wsubt, wl = d["wod"]
    files = [
        (mw.make_slide(d["tag"], "WARM UP", wsub, wlines, f"{folder}/dia{d['n']}_1_warmup.png"), alt("WARM UP", wsub, wlines)),
        (mw.make_slide(d["tag"], "STRENGTH", stsub, stlines, f"{folder}/dia{d['n']}_2_strength.png"), alt("STRENGTH", stsub, stlines)),
        (mw.make_slide(d["tag"], wt, wsubt, wl, f"{folder}/dia{d['n']}_3_wod.png"), alt(wt, wsubt, wl)),
    ]
    open(f"{BASE}/captions/dia{d['n']}.txt", "w", encoding="utf-8").write(d["cap"] + "\n")
    thumbs.append([f for f, _ in files])
    md += [f"## Día {d['n']} · {d['dia']} · {d['tag'].title()}", f"Fecha propuesta: {d['fecha']}", "",
           "**Caption**", "", "```", d["cap"], "```", "", "**Texto alternativo**"]
    for i, (f, a) in enumerate(files, 1):
        md.append(f"{i}. {a}")
    md.append("")
open(f"{BASE}/captions_semana.md", "w", encoding="utf-8").write("\n".join(md))

# vista previa 7 filas x 3 columnas
tw, th = 360, 450
sheet = Image.new("RGB", (tw * 3 + 40, th * 7 + 80), (30, 30, 30))
for r, row in enumerate(thumbs):
    for c, f in enumerate(row):
        sheet.paste(Image.open(f).resize((tw, th), Image.LANCZOS), (10 + c * (tw + 10), 10 + r * (th + 10)))
sheet.save(f"{BASE}/vista_previa_semana.png")

# el día 1 debe ser idéntico al set ya aprobado
for a, b in [("dia1_halterofilia/dia1_1_warmup.png", "halterofilia_1_warmup.png"), ("dia1_halterofilia/dia1_2_strength.png", "halterofilia_2_strength.png"), ("dia1_halterofilia/dia1_3_wod.png", "halterofilia_3_wod.png")]:
    x = np.array(Image.open(f"{BASE}/{a}")); y = np.array(Image.open(f"/mnt/user-data/outputs/{b}"))
    print("día 1 idéntico al aprobado:", b, bool((x == y).all()))
print("ok")
