from pathlib import Path
p = Path("godot/experiment_v02.gd")
s = p.read_text()
# ci_v09_movement_foundation.py owns walking frame cadence and facing.
# Do not overwrite its displacement-based animation with elapsed-time animation.
expected = 'int(walk_distance/14.0)%4 if is_walking and stage == 3 and menu == "" else 0'
if expected not in s:
    raise RuntimeError("Movement foundation not applied; inspect pipeline order")
# Keep the approved tree art assets; only adjust world-space drawing dimensions.
s = s.replace('var tree_size := Vector2(220.0,288.0)*scale',
              'var tree_size := Vector2(190.0,250.0)*scale')
p.write_text(s)
print("Vertical slice applied without conflicting with movement foundation.")
