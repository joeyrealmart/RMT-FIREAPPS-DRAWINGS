import ezdxf

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

top_mimic = []
bot_mimic = []

for e in msp:
    pts = []
    if e.dxftype() == 'LINE': pts = [e.dxf.start, e.dxf.end]
    elif e.dxftype() in ('TEXT', 'CIRCLE', 'INSERT', 'ARC'): pts = [e.dxf.insert if hasattr(e.dxf, 'insert') else e.dxf.center]
    elif e.dxftype() == 'POLYLINE': pts = [v.dxf.location for v in e.vertices]

    if any(-2100 <= p[0] <= -1000 and 600 <= p[1] <= 1050 for p in pts):
        top_mimic.append(e)
    if any(-3300 <= p[0] <= -2700 and -1350 <= p[1] <= -1090 for p in pts):
        bot_mimic.append(e)

print("Top Mimic entities:", len(top_mimic))
print("Bot Mimic entities:", len(bot_mimic))

# Check entity types in bot_mimic
from collections import Counter
print("Bot entities by layer & type:", Counter((e.dxf.layer, e.dxftype()) for e in bot_mimic))
