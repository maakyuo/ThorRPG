from pathlib import Path
p = Path("godot/main.gd")
s = p.read_text()
old = ''' for path in DirAccess.get_files_at("res://assets"):
  if path.ends_with(".png"):
   textures[path.trim_suffix(".png")] = load("res://assets/"+path)'''
new = ''' for key in ["grass","grass_0","grass_1","grass_2","flowers_0","flowers_1","dirt","house","tree_0","tree_1","tree_2","bush_0","bush_1","npc_0","npc_1","npc_2","rabbit","horn_rabbit","wolf","goblin","rock","stump"]:
  var path := "res://assets/" + key + ".png"
  if ResourceLoader.exists(path):
   textures[key] = load(path)
 for direction in 4:
  for frame in 4:
   var key := "player_%d_%d" % [direction,frame]
   var path := "res://assets/" + key + ".png"
   if ResourceLoader.exists(path):
    textures[key] = load(path)'''
assert old in s, "sprite loader source changed"
s = s.replace(old, new).replace("user://thor_art_v01.json", "user://thor_art_v02.json")
p.write_text(s)
project = Path("godot/project.godot")
cfg = project.read_text()
if "window/handheld/orientation=" not in cfg:
    cfg = cfg.replace("[display]", "[display]\nwindow/handheld/orientation=1")
project.write_text(cfg)
print("Pixel art loader fixed; character creation reset; landscape enabled")
