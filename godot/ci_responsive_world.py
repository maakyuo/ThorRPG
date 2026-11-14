from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
# Always use a viewport-sized HUD, and place the panel using actual viewport pixels.
s=s.replace(' ui.size = get_viewport_rect().size\n ui.mouse_filter', ' ui.size = get_viewport_rect().size\n ui.mouse_filter')
s=s.replace(' get_viewport().size_changed.connect(_resize_hud)', ' get_viewport().size_changed.connect(_resize_hud)\n _resize_hud()')
s=s.replace('func _resize_hud() -> void:\n ui.size = get_viewport_rect().size', '''func _resize_hud() -> void:
 var viewport_size: Vector2 = get_viewport_rect().size
 ui.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
 ui.position = Vector2.ZERO
 ui.size = viewport_size
 var margin: float = 12.0
 var width: float = minf(520.0, maxf(260.0, viewport_size.x - margin*2.0))
 var height: float = minf(430.0, maxf(200.0, viewport_size.y - margin*2.0))
 panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
 panel.position = (viewport_size - Vector2(width,height))*0.5
 panel.size = Vector2(width,height)
 var scroller: ScrollContainer = panel.get_child(0) as ScrollContainer
 scroller.custom_minimum_size = Vector2.ZERO
 scroller.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 scroller.size_flags_vertical = Control.SIZE_EXPAND_FILL
 scroller.size = Vector2(width-12.0,height-12.0)
''')
# Explicit panel geometry and no oversized minimum forcing the panel out of screen.
s=s.replace(' scroll.custom_minimum_size = Vector2(520,430)', ' scroll.custom_minimum_size = Vector2.ZERO\n scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL')
s=s.replace(' scroll.add_child(panel_content)\n', ' scroll.add_child(panel_content)\n _resize_hud()\n')
# HUD buttons remain within screen bounds even at phone-sized viewport.
s=s.replace(' top.offset_left = -425',' top.offset_left = -minf(425.0,get_viewport_rect().size.x-16.0)')
# remove the opaque status overlay that obscures the forest, while preserving text on later passes.
s=s.replace('  draw_rect(Rect2(8,8,260,67),Color(0.06,0.12,0.10,0.87))','  # Avoid the large opaque square over the scenery.\n  draw_rect(Rect2(8,8,260,67),Color(0.06,0.12,0.10,0.28))')
# position the player in sight of the house, away from the trees.
s=s.replace('var player := Vector2(1030,850)','var player := Vector2(1030,690)')
# Avoid diagonal stripes in the generated forest: form separated irregular groves.
start=s.index(' for i in 45:\n  var x := 200.0+float((i*137)%1750)')
end=s.index(' for i in 3:\n  var npc_pos',start)
s=s[:start]+''' for i in 65:
  var cluster: int = i % 5
  var cx: float = [330.0,1840.0,350.0,1770.0,1100.0][cluster]
  var cy: float = [290.0,330.0,1170.0,1140.0,1330.0][cluster]
  var angle: float = float((i*137+cluster*43)%360)*PI/180.0
  var distance: float = 55.0+float((i*73)%320)
  var x: float = clampf(cx+cos(angle)*distance,70.0,WORLD.x-70.0)
  var y: float = clampf(cy+sin(angle)*distance,90.0,WORLD.y-70.0)
  if Vector2(x,y).distance_to(Vector2(1030,690)) < 245.0:
   continue
  if Vector2(x,y).distance_to(Vector2(1040,520)) < 190.0:
   continue
  _draw_tree(Vector2(x,y)-camera,i)
''' + s[end:]
# replace visible flat green ground with low-contrast texture detail; avoid framed tiles.
s=s.replace(' draw_rect(Rect2(Vector2.ZERO,s),Color("#80b36b"))',''' draw_rect(Rect2(Vector2.ZERO,s),Color("#80b36b"))
 # Natural soft ground variations, without repeating square tile borders.
 for patch in 110:
  var wx: float = float((patch*311+patch*patch*17)%2200)
  var wy: float = float((patch*193+patch*patch*23)%1500)
  var local_pos: Vector2 = Vector2(wx,wy)-camera
  if local_pos.x < -90 or local_pos.y < -90 or local_pos.x > s.x+90 or local_pos.y > s.y+90:
   continue
  var shade: Color = Color(0.27,0.41,0.21,0.07) if patch%3 == 0 else Color(0.78,0.87,0.47,0.06)
  draw_circle(local_pos,34.0+float(patch%4)*12.0,shade)
''')
# enforce horizontal orientation for Android; this is a Godot display setting.
p.write_text(s)
cfg=Path("godot/project.godot")
t=cfg.read_text()
if 'window/handheld/orientation=' in t:
 import re
 t=re.sub(r'window/handheld/orientation=\\d+', 'window/handheld/orientation=1', t)
else:
 t=t.replace('[display]','[display]\nwindow/handheld/orientation=1')
cfg.write_text(t)
print('Applied responsive centered menus, touch-safe panel, scattered forest and landscape orientation.')
