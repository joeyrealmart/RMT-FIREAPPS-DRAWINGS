import ezdxf
import numpy as np

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

top_entities = [e for e in msp if e.dxf.layer == 'MIMIC_SIZE' and any(-2100 <= p[0] <= -1000 and 600 <= p[1] <= 1050 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

bot_entities = [e for e in msp if any(-3300 <= p[0] <= -2700 and -1350 <= p[1] <= -1090 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

# Top bounds
top_xs = [p[0] for e in top_entities for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices])]
top_ys = [p[1] for e in top_entities for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices])]

# Bot bounds (excluding title block text far left)
bot_xs = [p[0] for e in bot_entities if e.dxf.layer in ('MIMIC_SIZE', '0') for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]) if p[0] > -3250]
bot_ys = [p[1] for e in bot_entities if e.dxf.layer in ('MIMIC_SIZE', '0') for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]) if p[1] < -1150]

print(f"Top bounds: X=[{min(top_xs):.2f}, {max(top_xs):.2f}], Y=[{min(top_ys):.2f}, {max(top_ys):.2f}]")
print(f"Bot bounds: X=[{min(bot_xs):.2f}, {max(bot_xs):.2f}], Y=[{min(bot_ys):.2f}, {max(bot_ys):.2f}]")

top_w, top_h = max(top_xs) - min(top_xs), max(top_ys) - min(top_ys)
bot_w, bot_h = max(bot_xs) - min(bot_xs), max(bot_ys) - min(bot_ys)

print(f"Top size: {top_w:.2f} x {top_h:.2f}")
print(f"Bot size: {bot_w:.2f} x {bot_h:.2f}")

scale_x = top_w / bot_w
scale_y = top_h / bot_h

print(f"Scale X: {scale_x:.4f}, Scale Y: {scale_y:.4f}")
