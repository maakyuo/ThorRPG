from pathlib import Path
p=Path("godot/experiment_v02.gd");s=p.read_text()
s=s.replace('var names := ["grass"','var names := ["gear_0","gear_1","gear_2","gear_3","gear_4","gear_5","gear_6","gear_7","gear_8","gear_9","grass"')
start=s.index('func _item_icon(index: int) -> Texture2D:')
end=s.index('func _inventory_grid() -> void:',start)
s=s[:start]+'''func _item_icon(index: int) -> Texture2D:
 var key: String="gear_%d" % index
 if art.has(key):
  return art[key]
 if icon_cache.has(index):
  return icon_cache[index]
 var fallback := Image.create(48,48,false,Image.FORMAT_RGBA8)
 fallback.fill(Color("#785b42"))
 var tex := ImageTexture.create_from_image(fallback)
 icon_cache[index]=tex
 return tex

'''+s[end:]
# Bigger trees already drawn using their dedicated PNGs.
p.write_text(s)
print("Integrated sprite textures into Godot art loading and equipment UI")
