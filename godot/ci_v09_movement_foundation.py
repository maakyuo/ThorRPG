from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
# Keep animation tied to actual displacement rather than elapsed wall clock.
anchor="var facing_index: int = 0"
if anchor in s:
 s=s.replace(anchor,anchor+"\nvar walk_distance: float = 0.0\nvar is_walking: bool = false")
# movement block from base script
old='''  if move.length() > 0.1:
   facing = move.normalized()
   player = (player+move*190.0*(1.0+float(stats["민첩"])*0.001)*delta).clamp(Vector2(32,32),WORLD-Vector2(32,32))'''
new='''  is_walking = move.length() > 0.1
  if is_walking:
   facing = move.normalized()
   var previous_position: Vector2 = player
   player = (player+facing*190.0*(1.0+float(stats["민첩"])*0.001)*delta).clamp(Vector2(32,32),WORLD-Vector2(32,32))
   walk_distance += previous_position.distance_to(player)
  else:
   walk_distance = 0.0'''
assert old in s,"Movement block changed; abort rather than silently skip"
s=s.replace(old,new)
# Animation only when moving and synchronized to distance traveled.
s=s.replace('int(elapsed*5.0)%4 if moving and stage == 3 and menu == "" else 0','int(walk_distance/14.0)%4 if is_walking and stage == 3 and menu == "" else 0')
# prevent wrong direction mapping if screen facing: original atlas order down/right/up/left.
p.write_text(s)
print("Applied displacement-synced walking animation and normalized direction")
