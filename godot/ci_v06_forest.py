from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
start=s.index(' for i in 65:\n  var cluster: int = i % 5')
end=s.index(' for i in 3:\n  var npc_pos',start)
s=s[:start]+''' # Forest is made of coherent, dense groves, not diagonal scatter.
 # Sort by world Y for natural front-to-back canopy overlap.
 var forest_trees: Array[Dictionary] = []
 var grove_centers: Array[Vector2] = [
  Vector2(280,240),Vector2(550,260),Vector2(1660,240),
  Vector2(1910,420),Vector2(280,1110),Vector2(560,1260),
  Vector2(1600,1170),Vector2(1910,1080),Vector2(1120,1360)
 ]
 for grove in grove_centers.size():
  var center_pos: Vector2 = grove_centers[grove]
  for n in 28:
   var hash: int = abs((grove+17)*73856093+(n+13)*19349663+n*n*83492791)
   var angle: float = float(hash%6283)*0.001
   var radius: float = sqrt(float((hash/17)%1000)/1000.0)*235.0
   var pos: Vector2 = center_pos+Vector2(cos(angle),sin(angle))*radius
   pos.x = clampf(pos.x,95.0,WORLD.x-95.0)
   pos.y = clampf(pos.y,135.0,WORLD.y-75.0)
   # Preserve the settlement clearing and the southward entry trail.
   if pos.distance_to(Vector2(1040,560)) < 315.0:
    continue
   if absf(pos.x-1030.0)<110.0 and pos.y<1140.0:
    continue
   forest_trees.append({"pos":pos,"variant":hash%3,"scale":0.92+float((hash/101)%28)*0.01})
 forest_trees.sort_custom(func(a: Dictionary,b: Dictionary) -> bool: return (a["pos"] as Vector2).y < (b["pos"] as Vector2).y)
 for tree in forest_trees:
  var pos: Vector2 = tree["pos"]
  var scale: float = tree["scale"]
  var screen_pos: Vector2 = pos-camera
  # Cull using full canopy bounds, never just the trunk center.
  if screen_pos.x < -130.0*scale or screen_pos.x > s.x+130.0*scale:
   continue
  if screen_pos.y < -210.0*scale or screen_pos.y > s.y+100.0*scale:
   continue
  _draw_forest_tree(screen_pos,int(tree["variant"]),scale)
''' + s[end:]
anchor='func _draw_person(p: Vector2, coat: Color, is_player: bool) -> void:'
fn='''func _draw_forest_tree(p: Vector2, variant: int, scale: float) -> void:
 # The tree is a complete pixel-art texture, not a cropped sprite-sheet cell.
 var tex_name: String = "tree_%d" % variant
 var tree_size := Vector2(158.0,208.0)*scale
 draw_ellipse_shadow(p,scale)
 _sprite(tex_name,p+Vector2(0,-tree_size.y*0.39),tree_size)

func draw_ellipse_shadow(p: Vector2, scale: float) -> void:
 draw_set_transform(p,0.0,Vector2(1.5*scale,0.48*scale))
 draw_circle(Vector2(0,0),34.0,Color(0.08,0.17,0.09,0.24))
 draw_set_transform(Vector2.ZERO)

'''
if anchor not in s: raise RuntimeError("missing anchor")
s=s.replace(anchor,fn+anchor,1)
p.write_text(s)
print("Forest overhaul applied: 9 groves, 252 candidate trees, larger full tree sprites, world-Y sorting, clearing and path")
