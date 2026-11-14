from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
# Never overwrite the authored tree art with procedurally generated placeholder images.
# Only animate when a direction input is present, and lock facing to actual motion.
old='var direction := 0\n if absf(facing.x)>absf(facing.y):'
if old not in s: raise RuntimeError("Direction code changed; inspect before patching")
s=s.replace(old,'''var direction := facing_index
 if absf(facing.x)>absf(facing.y):''',1)
# Frame cadence and equipment anchor both use same direction index.
old='var frame: int = int(elapsed*5.0)%4 if moving and stage == 3 and menu == "" else 0'
if old not in s: raise RuntimeError("Walking frame anchor missing")
s=s.replace(old,'''var frame: int = int(elapsed*7.0)%4 if moving and stage == 3 and menu == "" else 0''',1)
# Full source texture with visible trunk: avoid cropping canopy by a fixed camera rectangle.
s=s.replace('var tree_size := Vector2(220.0,288.0)*scale','var tree_size := Vector2(190.0,250.0)*scale')
p.write_text(s)
print("Direction state and animation cadence patched.")
