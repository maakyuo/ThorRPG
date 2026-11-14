from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
s=s.replace('var facing_index: int = 0','''var facing_index: int = 0
var selected_item: int = -1
var selecting_slot: String = ""
var inventory_page: int = 0
var icon_cache: Dictionary = {}
''')
s=s.replace(' {"name":"가죽 신발","slot":"신발","def":1}',''' {"name":"가죽 신발","slot":"신발","def":1},
 {"name":"나무 방패","slot":"방패","def":3},
 {"name":"철제 방패","slot":"방패","def":5}''')
s=s.replace('"신발":-1}', '"신발":-1,"방패":-1}')
s=s.replace(' for slot in ["상의","하의","장갑","신발"]:', ' for slot in ["상의","하의","장갑","신발","방패"]:')
s=s.replace(' if item.has("job") and item["job"] != job:\n  message = "%s 전용 무기입니다." % item["job"]\n  message_time = 2.0\n  return\n','')
s=s.replace(' equipped[slot] = -1 if equipped[slot] == index else index',''' equipped[slot] = -1 if equipped[slot] == index else index
 if slot == "무기" and equipped[slot] >= 0 and _weapon_type() in ["bow","staff"]:
  equipped["방패"] = -1
 if slot == "방패" and equipped[slot] >= 0 and _weapon_type() in ["bow","staff"]:
  equipped["방패"] = -1
  message = "활과 지팡이는 방패와 동시에 착용할 수 없습니다."
  message_time = 3.0''')
# Fix facing based on sprite atlas orientation: sprites should be explicitly flipped when facing left.
s=s.replace(' if not _sprite(sprite_key,center+Vector2(0,-13),Vector2(65,85)):', ''' if direction == 3 and art.has("player_1_%d" % frame):
  var tex: Texture2D = art["player_1_%d" % frame]
  draw_set_transform(center+Vector2(0,-13),0.0,Vector2(-1,1))
  draw_texture_rect(tex,Rect2(Vector2(-32.5,-42.5),Vector2(65,85)),false)
  draw_set_transform(Vector2.ZERO)
 elif not _sprite(sprite_key,center+Vector2(0,-13),Vector2(65,85)):''')
# Responsive full screen overlay
s=s.replace(' panel.offset_left = -270\n panel.offset_right = 270\n panel.offset_top = -225\n panel.offset_bottom = 225',''' panel.offset_left = -minf(480.0,get_viewport_rect().size.x*0.46)
 panel.offset_right = minf(480.0,get_viewport_rect().size.x*0.46)
 panel.offset_top = -minf(250.0,get_viewport_rect().size.y*0.46)
 panel.offset_bottom = minf(250.0,get_viewport_rect().size.y*0.46)''')
s=s.replace(' scroll.custom_minimum_size = Vector2(520,430)',' scroll.custom_minimum_size = Vector2.ZERO')
s=s.replace(' scroll.add_child(panel_content)',''' scroll.add_child(panel_content)
 scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
 scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED''')
# replace existing inventory and equipment functions
a=s.index('func _inventory_grid() -> void:')
b=s.index('func _clear_panel() -> void:',a)
new='''func _item_icon(index: int) -> Texture2D:
 if icon_cache.has(index):
  return icon_cache[index]
 var item: Dictionary = ITEMS[index]
 var pixels := Image.create(32,32,false,Image.FORMAT_RGBA8)
 pixels.fill(Color.TRANSPARENT)
 var metal := Color("#bfc8ce")
 var dark := Color("#3b302b")
 var gold := Color("#b78b4c")
 var leather := Color("#906343")
 var kind: String = str(item["slot"])
 for y in 32:
  for x in 32:
   var v := Color.TRANSPARENT
   if kind == "무기":
    if index == 2:
     var dx: float = float(x)-16.0
     var dy: float = float(y)-16.0
     if absf(dx*dx+dy*dy-115.0)<30.0 and x<24: v=leather
     if absf(x-15)<1 and y>5 and y<27: v=gold
    elif index == 1:
     if absf(x-16)<2 and y>5 and y<28: v=leather
     if absf(x-16)<4 and y>=4 and y<10: v=Color("#63cbd4")
    else:
     var blade: bool = abs(x+y-31)<=2 and x>8 and y<24
     if blade: v=metal
     if abs(x+y-31)<=3 and x<10 and y>20: v=leather
     if abs(x-y-5)<=1 and x>10 and x<22: v=gold
   elif kind == "방패":
    if y>=5 and y<=27 and abs(x-16)<=int(12.0-float(y-5)*0.35):
     v=leather if index==8 else metal
     if abs(x-16)<2 or y==7: v=gold
   elif kind in ["상의","하의","장갑","신발"]:
    if kind=="상의" and y>7 and y<26 and abs(x-16)<(11 if y>12 else 8): v=leather
    if kind=="하의" and y>8 and y<27 and ((x>7 and x<15) or (x>17 and x<25)): v=leather
    if kind=="장갑" and y>8 and y<26 and ((x>5 and x<14) or (x>18 and x<27)): v=leather
    if kind=="신발" and y>16 and y<27 and ((x>3 and x<14) or (x>18 and x<29)): v=leather
   if v.a>0:
    if x%7==0 or y%9==0: v=v.darkened(0.18)
    pixels.set_pixel(x,y,v)
 var tex := ImageTexture.create_from_image(pixels)
 icon_cache[index]=tex
 return tex

func _inventory_grid() -> void:
 var grid := GridContainer.new()
 grid.columns = 8
 panel_content.add_child(grid)
 var first: int = inventory_page*32
 for i in range(first,mini(first+32,ITEMS.size())):
  var b := Button.new()
  b.icon = _item_icon(i)
  b.expand_icon = true
  b.custom_minimum_size = Vector2(62,58)
  b.tooltip_text = str(ITEMS[i]["name"])
  _style_button(b)
  b.pressed.connect(_select_item.bind(i))
  grid.add_child(b)
 if ITEMS.size()>32:
  _button("이전 페이지",_inventory_prev)
  _button("다음 페이지",_inventory_next)

func _inventory_prev() -> void:
 inventory_page=maxi(0,inventory_page-1)
 _refresh_ui()

func _inventory_next() -> void:
 inventory_page=mini(int(ITEMS.size()/32),inventory_page+1)
 _refresh_ui()

func _select_item(i: int) -> void:
 selected_item=i
 menu="아이템 상세"
 _refresh_ui()

func _equipment_slots() -> void:
 _label("장비 착용 현황",24)
 var grid := GridContainer.new()
 grid.columns=3
 panel_content.add_child(grid)
 for slot in ["무기","방패","상의","하의","장갑","신발"]:
  var index: int = int(equipped.get(slot,-1))
  var b := Button.new()
  b.text=slot
  if index>=0:
   b.icon=_item_icon(index)
   b.expand_icon=true
  b.custom_minimum_size=Vector2(175,60)
  _style_button(b)
  b.pressed.connect(_choose_slot.bind(slot))
  grid.add_child(b)

func _choose_slot(slot: String) -> void:
 selecting_slot=slot
 menu="장비 선택"
 _refresh_ui()

func _select_equipment(index: int) -> void:
 selected_item=index
 menu="아이템 상세"
 _refresh_ui()

func _equip_selected() -> void:
 if selected_item<0: return
 _equip(selected_item)
 menu="장비" if selecting_slot!="" else "인벤토리"
 selecting_slot=""
 _refresh_ui()

func _unequip_slot() -> void:
 equipped[selecting_slot]=-1
 _save_game()
 menu="장비"
 selecting_slot=""
 _refresh_ui()

'''
s=s[:a]+new+s[b:]
s=s.replace('  _label("아이템을 선택하면 장착하거나 해제합니다.",15)','  _label("아이콘을 눌러 상세 정보를 확인하세요.",15)')
anchor=' elif menu == "스탯":'
ui=''' elif menu == "장비 선택":
  _label(selecting_slot+" 장비 선택",24)
  var options := GridContainer.new()
  options.columns=5
  panel_content.add_child(options)
  for i in ITEMS.size():
   if str(ITEMS[i]["slot"]) != selecting_slot: continue
   var b := Button.new()
   b.icon=_item_icon(i)
   b.expand_icon=true
   b.custom_minimum_size=Vector2(76,68)
   b.tooltip_text=str(ITEMS[i]["name"])
   _style_button(b)
   b.pressed.connect(_select_equipment.bind(i))
   options.add_child(b)
  _button("장착 해제",_unequip_slot)
  _button("뒤로",_back_to_equipment)
 elif menu == "아이템 상세":
  if selected_item>=0 and selected_item<ITEMS.size():
   var item: Dictionary=ITEMS[selected_item]
   _label(str(item["name"])+"  |  일반",24)
   var icon := TextureRect.new()
   icon.texture=_item_icon(selected_item)
   icon.custom_minimum_size=Vector2(76,76)
   icon.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
   icon.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
   panel_content.add_child(icon)
   _label("장비 부위: "+str(item["slot"]))
   _label("공격력 +%d   마법 공격 +%d   방어력 +%d" % [int(item.get("atk",0)),int(item.get("magic",0)),int(item.get("def",0))])
   _button("장착 / 해제",_equip_selected)
  _button("뒤로",_back_from_detail)
'''
s=s.replace(anchor,ui+anchor,1)
anchor='func _inventory_prev() -> void:'
s=s.replace(anchor,'''func _back_to_equipment() -> void:
 menu="장비"
 selecting_slot=""
 _refresh_ui()

func _back_from_detail() -> void:
 menu="장비 선택" if selecting_slot!="" else "인벤토리"
 _refresh_ui()

'''+anchor,1)
# Replace line-drawn weapon with pixel-art texture rendered at hand.
a=s.index('func _draw_equipped(center: Vector2) -> void:')
b=s.index('func _draw_house(',a)
s=s[:a]+'''func _draw_equipped(center: Vector2) -> void:
 var idx: int = int(equipped["무기"])
 var axis: Vector2=facing.normalized()
 if axis.length_squared()<0.5: axis=Vector2.DOWN
 var side: Vector2=axis.rotated(PI/2.0)
 var hand: Vector2=center+side*15.0+Vector2(0,-10)
 var swing: float=0.0
 if attack_visual>0:
  swing=sin((0.30-attack_visual)/0.30*PI)*0.85
 if idx>=0:
  var weapon_tex: Texture2D=_item_icon(idx)
  draw_set_transform(hand,axis.angle()-PI/2.0+swing,Vector2.ONE)
  draw_texture_rect(weapon_tex,Rect2(Vector2(-16,-29),Vector2(32,32)),false)
  draw_set_transform(Vector2.ZERO)
 var shield_idx: int=int(equipped.get("방패",-1))
 if shield_idx>=0:
  var shield_hand: Vector2=center-side*16.0+Vector2(0,-9)
  draw_texture_rect(_item_icon(shield_idx),Rect2(shield_hand-Vector2(14,14),Vector2(28,28)),false)

'''+s[b:]
# save backward compatibility shield
s=s.replace(' equipped = data.get("equipped",equipped)',' equipped = data.get("equipped",equipped)\n if not equipped.has("방패"): equipped["방패"]=-1')
p.write_text(s)
print("v0.6 unified equipment and icon UI patch applied")
