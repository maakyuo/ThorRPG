from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
assert 'func _draw_house(' in s and 'func _draw_monster(' in s
s=s.replace('var font: Font','var art: Dictionary = {}\nvar font: Font')
s=s.replace(' font = ThemeDB.fallback_font',' font = ThemeDB.fallback_font\n _load_art()')
anchor='func _spawn_mobs() -> void:'
load_art='''func _load_art() -> void:
 var names := ["grass","grass_0","grass_1","grass_2","flowers_0","flowers_1","dirt","house","tree_0","tree_1","tree_2","bush_0","bush_1","npc_0","npc_1","npc_2","rabbit","horn_rabbit","wolf","goblin","rock","stump"]
 for name in names:
  var path: String = "res://assets/" + name + ".png"
  if ResourceLoader.exists(path):
   art[name] = load(path)
 for d in 4:
  for frame in 4:
   var name: String = "player_%d_%d" % [d,frame]
   var path: String = "res://assets/" + name + ".png"
   if ResourceLoader.exists(path):
    art[name] = load(path)

func _sprite(name: String, at: Vector2, size: Vector2) -> bool:
 if not art.has(name):
  return false
 var tex: Texture2D = art[name]
 draw_texture_rect(tex,Rect2(at-size*0.5,size),false)
 return true

'''
assert anchor in s
s=s.replace(anchor,load_art+anchor)
start=s.index(' var start_x := maxi(0,int(camera.x/48.0))')
end=s.index(' _draw_house(Vector2(1040,520)-camera)',start)
s=s[:start]+''' # Seamless continuous grass: do not stamp bordered tiles in a checkerboard.
 # Scatter isolated vegetation as overlays rather than repeating framed squares.
 var start_x := maxi(0,int(camera.x/96.0))
 var start_y := maxi(0,int(camera.y/96.0))
 for x in range(start_x,start_x+int(s.x/96.0)+2):
  for y in range(start_y,start_y+int(s.y/96.0)+2):
   var hash_value: int = abs(x*92821+y*68917+x*y*131)
   var p := Vector2(x*96+hash_value%49,y*96+(hash_value/37)%49)-camera
   if hash_value%5 == 0:
    _sprite("flowers_0",p,Vector2(19,19))
   elif hash_value%3 == 0:
    _sprite("bush_0",p,Vector2(22,20))
''' + s[end:]
s=s.replace('  _draw_person(npc_pos,Color(["#c18a62","#7d89bd","#ba85a2"][i]),false)','  if not _sprite("npc_%d" % i,npc_pos+Vector2(0,-15),Vector2(66,85)):\n   _draw_person(npc_pos,Color(["#c18a62","#7d89bd","#ba85a2"][i]),false)')
s=s.replace(' _draw_person(center,Color("#467bb7"),true)',' var direction := 0\n if absf(facing.x)>absf(facing.y):\n  direction = 1 if facing.x>0 else 3\n elif facing.y<0:\n  direction = 2\n var sprite_key: String = "player_%d_%d" % [direction,int(elapsed*5.0)%4]\n if not _sprite(sprite_key,center+Vector2(0,-13),Vector2(65,85)):\n  _draw_person(center,Color("#467bb7"),true)')
s=s.replace('func _draw_house(p: Vector2) -> void:\n','func _draw_house(p: Vector2) -> void:\n if _sprite("house",p+Vector2(0,-30),Vector2(260,220)):\n  return\n')
s=s.replace('func _draw_tree(p: Vector2, seed: int) -> void:\n','func _draw_tree(p: Vector2, seed: int) -> void:\n if _sprite("tree_%d" % (seed%3),p+Vector2(0,-34),Vector2(115,150)):\n  return\n')
s=s.replace(' var kind: int = int(m["level"])\n var c := Color(m["color"])',' var kind: int = int(m["level"])\n var monster_key := "rabbit" if kind == 1 else ("horn_rabbit" if kind == 3 else ("wolf" if kind == 5 else "goblin"))\n var found_sprite := _sprite(monster_key,p+Vector2(0,-12),Vector2(76,76))\n var c := Color(m["color"])')
s=s.replace(' if kind <= 3:\n  draw_circle(p,18,c)',' if not found_sprite and kind <= 3:\n  draw_circle(p,18,c)')
s=s.replace(' elif kind == 5:\n  draw_colored_polygon',' elif not found_sprite and kind == 5:\n  draw_colored_polygon')
s=s.replace(' else:\n  draw_circle(p,21,c)\n  draw_colored_polygon',' elif not found_sprite:\n  draw_circle(p,21,c)\n  draw_colored_polygon')
s=s.replace(' draw_circle(p+Vector2(-7,-4),2,Color("#292c24"))\n draw_circle(p+Vector2(7,-4),2,Color("#292c24"))',' if not found_sprite:\n  draw_circle(p+Vector2(-7,-4),2,Color("#292c24"))\n  draw_circle(p+Vector2(7,-4),2,Color("#292c24"))')
p.write_text(s)
scene=Path("godot/main.tscn")
scene.write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://experiment_v02.gd" id="1"]\n\n[node name="ThorRPG" type="Node2D"]\nscript = ExtResource("1")\n')
print("Integrated RPG creation, equipment, stats, skills and pixel-art sprites with seamless base ground")

# Fix UI: a full-rect Control parented to Node2D has no sized Control parent.
# Attach HUD to a CanvasLayer and explicitly size it to the viewport.
s=p.read_text()
s=s.replace('var ui: Control','var hud_layer: CanvasLayer\nvar ui: Control')
s=s.replace(' ui = Control.new()\n ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)\n ui.mouse_filter = Control.MOUSE_FILTER_PASS\n add_child(ui)',' hud_layer = CanvasLayer.new()\n hud_layer.layer = 10\n add_child(hud_layer)\n ui = Control.new()\n ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)\n ui.size = get_viewport_rect().size\n ui.mouse_filter = Control.MOUSE_FILTER_PASS\n hud_layer.add_child(ui)\n get_viewport().size_changed.connect(_resize_hud)')
s=s.replace('func _clear_panel() -> void:', 'func _resize_hud() -> void:\n ui.size = get_viewport_rect().size\n\nfunc _clear_panel() -> void:')
s=s.replace(' var sprite_key: String = "player_%d_%d" % [direction,int(elapsed*5.0)%4]', ' var moving: bool = Input.get_vector("move_left","move_right","move_up","move_down").length() > 0.1 or touch_move.length() > 0.1\n var frame: int = int(elapsed*5.0)%4 if moving and stage == 3 and menu == "" else 0\n var sprite_key: String = "player_%d_%d" % [direction,frame]')
p.write_text(s)
print("Fixed HUD CanvasLayer/viewport sizing and stopped idle walking animation")
