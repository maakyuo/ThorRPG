from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
def replace(a,b):
 global s
 if a not in s: raise RuntimeError("Missing patch anchor: "+a[:70])
 s=s.replace(a,b,1)
replace('var name_entry: LineEdit','''var name_entry: LineEdit
var pending_stats: Dictionary = {}
var pending_points: int = 0
var attack_visual: float = 0.0
var combo_index: int = 0
var last_attack_time: float = -10.0
var facing_index: int = 0''')
replace('for label in ["인벤토리","스탯","스킬"]:', 'for label in ["인벤토리","장비","스탯","스킬"]:')
replace(' b.custom_minimum_size = Vector2(125,43)',' b.custom_minimum_size = Vector2(84,42)')
replace(' top.offset_left = -minf(425.0,get_viewport_rect().size.x-16.0)',' top.offset_left = -minf(405.0,get_viewport_rect().size.x-16.0)')
replace(' scroll.add_child(panel_content)\n _resize_hud()', ''' scroll.add_child(panel_content)
 _apply_ui_theme()
 _resize_hud()''')
anchor='func _clear_panel() -> void:'
theme='''func _apply_ui_theme() -> void:
 var frame := StyleBoxFlat.new()
 frame.bg_color = Color("#35281f")
 frame.border_color = Color("#9d7950")
 frame.set_border_width_all(3)
 frame.set_corner_radius_all(9)
 frame.set_content_margin_all(12)
 panel.add_theme_stylebox_override("panel",frame)
 for child in ui.get_children():
  if child is HBoxContainer:
   for btn in child.get_children():
    _style_button(btn)

func _style_button(b: Button) -> void:
 var normal := StyleBoxFlat.new()
 normal.bg_color = Color("#604733")
 normal.border_color = Color("#b28c58")
 normal.set_border_width_all(2)
 normal.set_corner_radius_all(5)
 normal.set_content_margin_all(5)
 b.add_theme_stylebox_override("normal",normal)
 var hover := normal.duplicate() as StyleBoxFlat
 hover.bg_color = Color("#86603d")
 b.add_theme_stylebox_override("hover",hover)
 b.add_theme_stylebox_override("pressed",hover)
 b.add_theme_color_override("font_color",Color("#f6e8c8"))
 b.add_theme_color_override("font_hover_color",Color.WHITE)

func _stat_row(key: String) -> void:
 var row := HBoxContainer.new()
 row.add_theme_constant_override("separation",8)
 panel_content.add_child(row)
 var label := Label.new()
 label.text = "%s   %d" % [key,int(pending_stats[key])]
 label.custom_minimum_size.x = 155
 label.add_theme_font_size_override("font_size",18)
 row.add_child(label)
 var minus := Button.new()
 minus.text = "−"
 minus.custom_minimum_size = Vector2(53,43)
 minus.disabled = int(pending_stats[key]) <= int(stats[key])
 _style_button(minus)
 minus.pressed.connect(_change_pending.bind(key,-1))
 row.add_child(minus)
 var plus := Button.new()
 plus.text = "+"
 plus.custom_minimum_size = Vector2(53,43)
 plus.disabled = pending_points <= 0
 _style_button(plus)
 plus.pressed.connect(_change_pending.bind(key,1))
 row.add_child(plus)

func _change_pending(key: String, amount: int) -> void:
 if amount > 0 and pending_points <= 0:
  return
 if amount < 0 and int(pending_stats[key]) <= int(stats[key]):
  return
 pending_stats[key] = int(pending_stats[key])+amount
 pending_points -= amount
 _refresh_ui()

func _confirm_pending() -> void:
 if stage == 2 and pending_points != 0:
  message = "남은 포인트를 모두 분배하세요."
  _refresh_ui()
  return
 var old_hp := _max_hp()
 for key in STATS:
  stats[key] = int(pending_stats[key])
 points = pending_points
 hp = minf(_max_hp(),hp+_max_hp()-old_hp)
 mp = minf(_max_mp(),mp+10.0)
 if stage == 2:
  _begin_game()
 else:
  _save_game()
  _refresh_ui()

func _inventory_grid() -> void:
 var grid := GridContainer.new()
 grid.columns = 6
 grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 panel_content.add_child(grid)
 for i in ITEMS.size():
  var item: Dictionary = ITEMS[i]
  var b := Button.new()
  b.text = str(item["name"])
  b.tooltip_text = str(item["name"])
  b.custom_minimum_size = Vector2(112,68)
  b.add_theme_font_size_override("font_size",12)
  _style_button(b)
  b.pressed.connect(_equip.bind(i))
  grid.add_child(b)

func _equipment_slots() -> void:
 _label("장비 착용 현황",24)
 for slot in ["무기","상의","하의","장갑","신발"]:
  var index: int = int(equipped[slot])
  var title: String = str(ITEMS[index]["name"]) if index >= 0 else "미착용"
  var b := Button.new()
  b.text = "%s     %s" % [slot,title]
  b.custom_minimum_size.y = 48
  _style_button(b)
  if index >= 0:
   b.pressed.connect(_equip.bind(index))
  panel_content.add_child(b)

'''
replace(anchor,theme+anchor)
replace(' b.pressed.connect(cb)\n panel_content.add_child(b)',' _style_button(b)\n b.pressed.connect(cb)\n panel_content.add_child(b)')
replace('  for key in STATS:\n   _button("%s  %d     [+1]" % [key,stats[key]],_add_stat.bind(key))\n  _button("게임 시작",_begin_game)','''  for key in STATS:
   _stat_row(key)
  _button("확정",_confirm_pending)''')
a=s.index(' elif menu == "인벤토리":')
b=s.index(' elif menu == "스킬":',a)
s=s[:a]+''' elif menu == "인벤토리":
  _label("인벤토리",25)
  _label("아이템을 선택하면 장착하거나 해제합니다.",15)
  _inventory_grid()
  _button("닫기",_close_menu)
 elif menu == "장비":
  _equipment_slots()
  _button("닫기",_close_menu)
 elif menu == "스탯":
  _label("능력치 분배",25)
  _label("Lv.%d  |  남은 포인트: %d" % [level,pending_points])
  for key in STATS:
   _stat_row(key)
  _button("확정",_confirm_pending)
  _button("닫기",_close_menu)
''' + s[b:]
replace(' job = j\n stage = 2',' job = j\n pending_stats = stats.duplicate(true)\n pending_points = points\n stage = 2')
replace(' menu = "" if menu == which else which\n _refresh_ui()',''' menu = "" if menu == which else which
 if menu == "스탯":
  pending_stats = stats.duplicate(true)
  pending_points = points
 _refresh_ui()''')
replace(' attack_cd = 0.45\n for i in mobs.size():',''' var weapon_type := _weapon_type()
 attack_cd = 0.62 if weapon_type == "staff" else (0.57 if weapon_type == "bow" else 0.38)
 combo_index = (combo_index+1)%3 if elapsed-last_attack_time < 0.9 else 0
 last_attack_time = elapsed
 attack_visual = 0.30
 for i in mobs.size():''')
replace('  if diff.length() > 90 or (diff.length() >= 30 and facing.dot(diff.normalized()) < 0.0):','  var reach: float = 215.0 if weapon_type == "bow" or weapon_type == "staff" else (108.0 if weapon_type == "sword" else 72.0)\n  if diff.length() > reach or (diff.length() >= 30 and facing.dot(diff.normalized()) < 0.15):')
replace(' attack_cd = maxf(0.0,attack_cd-delta)',' attack_cd = maxf(0.0,attack_cd-delta)\n attack_visual = maxf(0.0,attack_visual-delta)')
replace(' var direction := 0\n if absf(facing.x)>absf(facing.y):',' var direction := 0\n if absf(facing.x)>absf(facing.y):')
replace(' var sprite_key: String = "player_%d_%d" % [direction,frame]',''' # Keep the body direction and the equipped weapon aligned to movement.
 facing_index = direction
 var sprite_key: String = "player_%d_%d" % [direction,frame]''')
replace('  _draw_person(center,Color("#467bb7"),true)','  _draw_person(center,Color("#467bb7"),true)\n _draw_equipped(center)')
anchor='func _draw_house(p: Vector2) -> void:'
weapons='''func _weapon_type() -> String:
 var index: int = int(equipped["무기"])
 if index < 0:
  return "fist"
 match str(ITEMS[index]["name"]):
  "낡은 철검": return "sword"
  "낡은 단궁": return "bow"
  "초보자의 지팡이": return "staff"
  "낡은 단검": return "dagger"
 return "fist"

func _draw_equipped(center: Vector2) -> void:
 var kind: String = _weapon_type()
 var axis: Vector2 = facing.normalized()
 if axis.length_squared() < 0.5:
  axis = Vector2.DOWN
 var hand := center + Vector2(13,-11) + axis*10.0
 var swing: float = 0.0
 if attack_visual > 0:
  swing = sin((0.30-attack_visual)/0.30*PI)*float(combo_index+1)*5.0
 if kind == "sword":
  draw_line(hand,hand+axis*(28.0+swing),Color("#c7d2d4"),5.0)
  draw_line(hand-axis.rotated(PI/2)*8,hand+axis.rotated(PI/2)*8,Color("#b88c4b"),4.0)
 elif kind == "dagger":
  draw_line(hand,hand+axis*(16.0+swing),Color("#d5dce0"),3.0)
 elif kind == "bow":
  var side: Vector2 = axis.rotated(PI/2)
  draw_arc(hand+axis*5.0,18.0,axis.angle()-1.3,axis.angle()+1.3,14,Color("#a77845"),3.0)
  draw_line(hand-side*16.0,hand+side*16.0,Color("#efe3bb"),1.5)
  if attack_visual > 0:
   draw_line(hand,hand+axis*(30.0+swing),Color("#e9d5a0"),2.0)
 elif kind == "staff":
  draw_line(hand-axis*10.0,hand+axis*(27.0+swing),Color("#785235"),5.0)
  draw_circle(hand+axis*(28.0+swing),6.0,Color("#65c9de"))
 if attack_visual > 0 and kind != "fist":
  var effect_color := Color("#8ed6ff") if kind == "staff" else Color("#f7dfad")
  draw_arc(center+axis*34.0,22.0,axis.angle()-0.7,axis.angle()+0.7,12,effect_color,2.0)

'''
replace(anchor,weapons+anchor)
# Existing data remains compatible. Character creation starts with temporary stats.
replace('func _refresh_ui() -> void:\n _clear_panel()', '''func _refresh_ui() -> void:
 if pending_stats.is_empty():
  pending_stats = stats.duplicate(true)
  pending_points = points
 _clear_panel()''')
# prevent game save from changing during preview stat allocation
p.write_text(s)
print("v0.5 RPG: brown UI, separate equipment/inventory, +/- confirmed stats, weapon rendering and attack variants")
