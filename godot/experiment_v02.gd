extends Node2D

const WORLD := Vector2(2200, 1500)
const JOBS := ["전사", "마법사", "궁수", "암살자"]
const STATS := ["근력", "민첩", "지능", "체력", "마력"]
const SKILLS := {
 "전사":["돌진 베기","회전 베기","전투의 함성","반격 태세","대지 가르기"],
 "마법사":["화염구","얼음 화살","마력 보호막","바람 칼날","마력 폭발"],
 "궁수":["속사","관통 사격","회피 사격","독화살","매의 눈"],
 "암살자":["기습","출혈 베기","그림자 이동","연속 참격","암살의 마음가짐"]
}
const ITEMS := [
 {"name":"낡은 철검","slot":"무기","job":"전사","atk":8},
 {"name":"초보자의 지팡이","slot":"무기","job":"마법사","magic":8},
 {"name":"낡은 단궁","slot":"무기","job":"궁수","atk":7},
 {"name":"낡은 단검","slot":"무기","job":"암살자","atk":6},
 {"name":"천 상의","slot":"상의","def":2},
 {"name":"천 하의","slot":"하의","def":2},
 {"name":"가죽 장갑","slot":"장갑","def":1},
 {"name":"가죽 신발","slot":"신발","def":1}
]
const MONSTERS := [
 {"name":"토끼","level":1,"hp":25.0,"atk":3.0,"def":0.0,"speed":42.0,"xp":15,"color":"#e8ddc8"},
 {"name":"뿔토끼","level":3,"hp":48.0,"atk":7.0,"def":2.0,"speed":66.0,"xp":30,"color":"#b5a1c5"},
 {"name":"늑대","level":5,"hp":75.0,"atk":11.0,"def":4.0,"speed":92.0,"xp":50,"color":"#73828b"},
 {"name":"고블린","level":10,"hp":145.0,"atk":19.0,"def":8.0,"speed":74.0,"xp":110,"color":"#7caa61"}
]
var name_text := ""
var job := ""
var stage := 0
var player := Vector2(1030,850)
var facing := Vector2.DOWN
var hp := 110.0
var mp := 110.0
var level := 1
var xp := 0
var points := 50
var stats := {"근력":1,"민첩":1,"지능":1,"체력":1,"마력":1}
var equipped := {"무기":-1,"상의":-1,"하의":-1,"장갑":-1,"신발":-1}
var mobs: Array[Dictionary] = []
var menu := ""
var touch_id := -1
var touch_origin := Vector2.ZERO
var touch_move := Vector2.ZERO
var attack_cd := 0.0
var dodge_cd := 0.0
var invuln := 0.0
var save_clock := 0.0
var elapsed := 0.0
var message := ""
var message_time := 0.0
var font: Font
var ui: Control
var panel: PanelContainer
var panel_content: VBoxContainer
var name_entry: LineEdit

func _ready() -> void:
 font = ThemeDB.fallback_font
 _load_game()
 _spawn_mobs()
 _build_ui()
 _refresh_ui()

func _spawn_mobs() -> void:
 mobs.clear()
 var places := [Vector2(540,450),Vector2(720,490),Vector2(1460,520),Vector2(1610,600),Vector2(500,1120),Vector2(650,1220),Vector2(1640,1100),Vector2(1830,1200)]
 for i in places.size():
  var kind: int = i / 2
  var m: Dictionary = MONSTERS[kind].duplicate(true)
  m["pos"] = places[i]
  m["home"] = places[i]
  m["max_hp"] = m["hp"]
  m["alive"] = true
  m["respawn"] = 0.0
  m["cooldown"] = 0.0
  m["hit"] = 0.0
  mobs.append(m)

func _build_ui() -> void:
 ui = Control.new()
 ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 ui.mouse_filter = Control.MOUSE_FILTER_PASS
 add_child(ui)
 var top := HBoxContainer.new()
 top.set_anchors_preset(Control.PRESET_TOP_RIGHT)
 top.anchor_left = 1.0
 top.anchor_right = 1.0
 top.offset_left = -425
 top.offset_top = 8
 top.offset_right = -8
 top.offset_bottom = 52
 ui.add_child(top)
 for label in ["인벤토리","스탯","스킬"]:
  var b := Button.new()
  b.text = label
  b.custom_minimum_size = Vector2(125,43)
  b.pressed.connect(_toggle_menu.bind(label))
  top.add_child(b)
 panel = PanelContainer.new()
 panel.set_anchors_preset(Control.PRESET_CENTER)
 panel.anchor_left = 0.5
 panel.anchor_right = 0.5
 panel.anchor_top = 0.5
 panel.anchor_bottom = 0.5
 panel.offset_left = -270
 panel.offset_right = 270
 panel.offset_top = -225
 panel.offset_bottom = 225
 ui.add_child(panel)
 var scroll := ScrollContainer.new()
 scroll.custom_minimum_size = Vector2(520,430)
 panel.add_child(scroll)
 panel_content = VBoxContainer.new()
 panel_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 panel_content.add_theme_constant_override("separation",9)
 scroll.add_child(panel_content)

func _clear_panel() -> void:
 for child in panel_content.get_children():
  panel_content.remove_child(child)
  child.queue_free()

func _label(t: String, size: int = 19) -> void:
 var l := Label.new()
 l.text = t
 l.add_theme_font_size_override("font_size",size)
 l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
 panel_content.add_child(l)

func _button(t: String, cb: Callable) -> void:
 var b := Button.new()
 b.text = t
 b.custom_minimum_size.y = 43
 b.pressed.connect(cb)
 panel_content.add_child(b)

func _refresh_ui() -> void:
 _clear_panel()
 panel.visible = stage < 3 or menu != ""
 if stage == 0:
  _label("THOR RPG  |  캐릭터 생성",26)
  _label("캐릭터 이름을 입력하세요.")
  name_entry = LineEdit.new()
  name_entry.placeholder_text = "이름 (1~16자)"
  name_entry.max_length = 16
  name_entry.text = name_text
  panel_content.add_child(name_entry)
  _button("다음: 직업 선택",_confirm_name)
 elif stage == 1:
  _label("직업 선택",26)
  _label("한 번 선택하면 이번 캐릭터의 직업으로 저장됩니다.")
  for j in JOBS:
   _button(j,_select_job.bind(j))
  _button("이전",_back_to_name)
 elif stage == 2:
  _label("초기 스탯 분배",26)
  _label("%s  |  %s  |  남은 포인트 %d" % [name_text,job,points])
  for key in STATS:
   _button("%s  %d     [+1]" % [key,stats[key]],_add_stat.bind(key))
  _button("게임 시작",_begin_game)
 elif menu == "인벤토리":
  _label("인벤토리  |  일반 등급 장비",25)
  _label("장비를 누르면 착용 / 해제됩니다.")
  for i in ITEMS.size():
   var item: Dictionary = ITEMS[i]
   var active: bool = int(equipped[str(item["slot"])]) == i
   var suffix: String = " [착용 중]" if active else ""
   var bonus: String = "공격 +%d" % item.get("atk",0) if item.has("atk") else ("마법 +%d" % item.get("magic",0) if item.has("magic") else "방어 +%d" % item.get("def",0))
   _button("%s  |  %s%s" % [item["name"],bonus,suffix],_equip.bind(i))
  _label("장비 등급: 일반 · 희귀 · 영웅 · 전설 · 신화 · 고유",14)
  _button("닫기",_close_menu)
 elif menu == "스탯":
  _label("능력치 분배",25)
  _label("Lv.%d  |  남은 포인트: %d" % [level,points])
  for key in STATS:
   _button("%s  %d    [+1]" % [key,stats[key]],_add_stat.bind(key))
  _label("HP %d / %d   MP %d / %d" % [int(hp),int(_max_hp()),int(mp),int(_max_mp())])
  _label("물리 공격 %d  |  마법 공격 %d  |  방어 %d" % [int(_physical_attack()),int(_magic_attack()),int(_defense())])
  _button("닫기",_close_menu)
 elif menu == "스킬":
  _label("%s 스킬창" % job,25)
  _label("스킬은 이번 실험에서 표시만 지원합니다.")
  for skill in SKILLS[job]:
   _label("◇  %s    Lv.1  [미구현]" % skill,18)
  _button("닫기",_close_menu)

func _confirm_name() -> void:
 var candidate := name_entry.text.strip_edges()
 if candidate.is_empty():
  _label("이름을 입력해야 합니다.",16)
  return
 name_text = candidate
 stage = 1
 _refresh_ui()

func _back_to_name() -> void:
 stage = 0
 _refresh_ui()

func _select_job(j: String) -> void:
 job = j
 stage = 2
 _refresh_ui()

func _begin_game() -> void:
 stage = 3
 hp = _max_hp()
 mp = _max_mp()
 _save_game()
 _refresh_ui()

func _toggle_menu(which: String) -> void:
 if stage != 3:
  return
 menu = "" if menu == which else which
 _refresh_ui()

func _close_menu() -> void:
 menu = ""
 _refresh_ui()

func _add_stat(key: String) -> void:
 if points <= 0:
  return
 var old_max := _max_hp()
 stats[key] += 1
 points -= 1
 if key == "체력":
  hp += _max_hp()-old_max
 if key == "마력":
  mp = minf(mp+10.0,_max_mp())
 _save_game()
 _refresh_ui()

func _equip(index: int) -> void:
 var item: Dictionary = ITEMS[index]
 if item.has("job") and item["job"] != job:
  message = "%s 전용 무기입니다." % item["job"]
  message_time = 2.0
  return
 var slot: String = item["slot"]
 equipped[slot] = -1 if equipped[slot] == index else index
 _save_game()
 _refresh_ui()

func _max_hp() -> float:
 return 100.0 + float(stats["체력"])*10.0

func _max_mp() -> float:
 return 100.0 + float(stats["마력"])*10.0

func _defense() -> float:
 var total := float(stats["체력"])
 for slot in ["상의","하의","장갑","신발"]:
  var idx: int = equipped[slot]
  if idx >= 0:
   total += float(ITEMS[idx].get("def",0))
 return total

func _physical_attack() -> float:
 var weapon := 0.0
 var idx: int = equipped["무기"]
 if idx >= 0:
  weapon = float(ITEMS[idx].get("atk",0))
 var strength := float(stats["근력"])
 return strength + weapon * (1.0+strength*0.005)

func _magic_attack() -> float:
 var base := 0.0
 var idx: int = equipped["무기"]
 if idx >= 0:
  base = float(ITEMS[idx].get("magic",0))
 var intellect := float(stats["지능"])
 return intellect + base * (1.0+intellect*0.005)

func _physics_process(delta: float) -> void:
 elapsed += delta
 if stage != 3:
  queue_redraw()
  return
 attack_cd = maxf(0.0,attack_cd-delta)
 dodge_cd = maxf(0.0,dodge_cd-delta)
 invuln = maxf(0.0,invuln-delta)
 message_time = maxf(0.0,message_time-delta)
 mp = minf(_max_mp(),mp+float(stats["마력"])*0.1*delta)
 if menu == "":
  var move := Input.get_vector("move_left","move_right","move_up","move_down")
  if touch_move.length() > 0.1:
   move = touch_move
  if move.length() > 0.1:
   facing = move.normalized()
   player = (player+move*190.0*(1.0+float(stats["민첩"])*0.001)*delta).clamp(Vector2(32,32),WORLD-Vector2(32,32))
  if Input.is_action_just_pressed("attack"):
   _attack()
  if Input.is_action_just_pressed("dodge"):
   _dodge()
 for i in mobs.size():
  var m: Dictionary = mobs[i]
  if not m["alive"]:
   m["respawn"] -= delta
   if m["respawn"] <= 0:
    m["alive"] = true
    m["hp"] = m["max_hp"]
    m["pos"] = m["home"]
   continue
  m["hit"] = maxf(0.0,float(m["hit"])-delta)
  m["cooldown"] = maxf(0.0,float(m["cooldown"])-delta)
  var diff: Vector2 = player-m["pos"]
  var distance := diff.length()
  if menu == "" and distance < 260 and distance > 42:
   m["pos"] += diff.normalized()*float(m["speed"])*delta
  elif distance <= 42 and m["cooldown"] <= 0 and menu == "":
   m["cooldown"] = 1.5
   if invuln <= 0 and randf() > minf(0.9,0.03+float(stats["민첩"])*0.0002):
    var damage := maxf(1.0,float(m["atk"])*100.0/(100.0+_defense()))
    hp = maxf(0.0,hp-damage)
    invuln = 0.45
    if hp <= 0:
     player = Vector2(1030,850)
     hp = _max_hp()
     message = "쓰러졌습니다. 시작 위치에서 부활합니다."
     message_time = 3.0
 save_clock += delta
 if save_clock >= 12.0:
  save_clock = 0
  _save_game()
 queue_redraw()

func _attack() -> void:
 if attack_cd > 0 or menu != "" or stage != 3:
  return
 attack_cd = 0.45
 for i in mobs.size():
  var m: Dictionary = mobs[i]
  if not m["alive"]:
   continue
  var diff: Vector2 = m["pos"]-player
  if diff.length() > 90 or (diff.length() >= 30 and facing.dot(diff.normalized()) < 0.0):
   continue
  var power := _magic_attack() if job == "마법사" else _physical_attack()
  var damage := maxf(1.0,power*100.0/(100.0+float(m["def"])))
  if randf() < 0.05:
   damage *= 1.5
  m["hp"] -= damage
  m["hit"] = 0.2
  if m["hp"] <= 0:
   m["alive"] = false
   m["respawn"] = 12.0
   xp += int(m["xp"])
   message = "Lv.%d %s 처치! 경험치 +%d" % [m["level"],m["name"],m["xp"]]
   message_time = 2.5
   while xp >= level*100:
    xp -= level*100
    level += 1
    points += 5
    hp = _max_hp()
    mp = _max_mp()
    message = "레벨 업! Lv.%d / 능력치 포인트 +5" % level
   _save_game()

func _dodge() -> void:
 if dodge_cd > 0 or menu != "" or stage != 3:
  return
 dodge_cd = 1.0
 invuln = 0.32
 player = (player+facing*115.0).clamp(Vector2(32,32),WORLD-Vector2(32,32))

func _unhandled_input(event: InputEvent) -> void:
 if stage != 3 or menu != "":
  return
 if event is InputEventScreenTouch:
  var p: Vector2 = event.position
  var s := get_viewport_rect().size
  if event.pressed:
   if p.x < s.x*0.40 and p.y > s.y*0.45:
    touch_id = event.index
    touch_origin = p
    touch_move = Vector2.ZERO
   elif p.x > s.x*0.83 and p.y > s.y*0.62:
    _attack()
   elif p.x > s.x*0.66 and p.y > s.y*0.62:
    _dodge()
  elif event.index == touch_id:
   touch_id = -1
   touch_move = Vector2.ZERO
 elif event is InputEventScreenDrag and event.index == touch_id:
  touch_move = ((event.position-touch_origin)/70.0).limit_length(1.0)

func _draw() -> void:
 var s := get_viewport_rect().size
 var camera := (player-s*0.5).clamp(Vector2.ZERO,WORLD-s)
 draw_rect(Rect2(Vector2.ZERO,s),Color("#80b36b"))
 var start_x := maxi(0,int(camera.x/48.0))
 var start_y := maxi(0,int(camera.y/48.0))
 for x in range(start_x,start_x+int(s.x/48.0)+2):
  for y in range(start_y,start_y+int(s.y/48.0)+2):
   var p := Vector2(x*48,y*48)-camera
   var c := Color("#83b46c") if (x*17+y*13)%5<2 else Color("#79aa62")
   draw_rect(Rect2(p,Vector2(48,48)),c)
   if (x*7+y*11)%4==0:
    draw_line(p+Vector2(19,31),p+Vector2(21,23),Color("#527e48"),2)
    draw_line(p+Vector2(19,31),p+Vector2(15,26),Color("#527e48"),2)
 _draw_house(Vector2(1040,520)-camera)
 for i in 45:
  var x := 200.0+float((i*137)%1750)
  var y := 160.0+float((i*89)%1100)
  if Vector2(x,y).distance_to(Vector2(1040,520)) < 250:
   continue
  _draw_tree(Vector2(x,y)-camera, i)
 for i in 3:
  var npc_pos := Vector2(900+i*105,730+(i%2)*65)-camera
  _draw_person(npc_pos,Color(["#c18a62","#7d89bd","#ba85a2"][i]),false)
  draw_string(font,npc_pos+Vector2(-32,-43),["마을 주민","여행 상인","숲지기"][i],HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
 for m in mobs:
  if not m["alive"]:
   continue
  var p: Vector2 = m["pos"]-camera
  _draw_monster(p,m)
 var center := player-camera
 _draw_person(center,Color("#467bb7"),true)
 if attack_cd > 0.29:
  draw_arc(center,90,atan2(facing.y,facing.x)-0.7,atan2(facing.y,facing.x)+0.7,20,Color("#ffe5a2"),3)
 if invuln > 0:
  draw_arc(center,25,0,TAU,24,Color("#b9e8ff"),2)
 if stage == 3:
  draw_rect(Rect2(8,8,260,67),Color(0.06,0.12,0.10,0.87))
  draw_string(font,Vector2(16,27),"%s  |  %s  Lv.%d" % [name_text,job,level],HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color.WHITE)
  draw_string(font,Vector2(16,46),"HP %d/%d   MP %d/%d" % [int(hp),int(_max_hp()),int(mp),int(_max_mp())],HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color.WHITE)
  draw_string(font,Vector2(16,64),"EXP %d/%d   스탯 포인트 %d" % [xp,level*100,points],HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
  if message_time > 0:
   draw_string(font,Vector2(s.x*0.28,94),message,HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#fff1bd"))
  if menu == "":
   draw_circle(Vector2(88,s.y-83),67,Color(0.07,0.14,0.12,0.48))
   draw_circle(Vector2(s.x-72,s.y-73),49,Color(0.36,0.18,0.14,0.72))
   draw_string(font,Vector2(s.x-94,s.y-66),"공격",HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color.WHITE)
   draw_circle(Vector2(s.x-187,s.y-73),40,Color(0.12,0.24,0.38,0.75))
   draw_string(font,Vector2(s.x-207,s.y-67),"회피",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)

func _draw_house(p: Vector2) -> void:
 draw_rect(Rect2(p+Vector2(-92,-45),Vector2(184,124)),Color("#9a7855"))
 draw_rect(Rect2(p+Vector2(-83,-34),Vector2(166,101)),Color("#d3b78c"))
 draw_colored_polygon(PackedVector2Array([p+Vector2(-112,-44),p+Vector2(0,-132),p+Vector2(112,-44)]),Color("#784f46"))
 draw_rect(Rect2(p+Vector2(-22,15),Vector2(44,64)),Color("#5e4437"))
 draw_rect(Rect2(p+Vector2(-69,-4),Vector2(30,28)),Color("#7cabb2"))
 draw_rect(Rect2(p+Vector2(39,-4),Vector2(30,28)),Color("#7cabb2"))

func _draw_tree(p: Vector2, seed: int) -> void:
 var wobble := sin(elapsed*0.7+seed)*1.5
 draw_circle(p+Vector2(0,12),23,Color(0.15,0.24,0.15,0.23))
 draw_rect(Rect2(p+Vector2(-8,-20),Vector2(16,50)),Color("#78583d"))
 draw_circle(p+Vector2(wobble,-36),31,Color("#346b45"))
 draw_circle(p+Vector2(-17+wobble,-53),24,Color("#498b54"))
 draw_circle(p+Vector2(16+wobble,-54),25,Color("#3c804b"))
 draw_circle(p+Vector2(0+wobble,-70),22,Color("#60a564"))

func _draw_person(p: Vector2, coat: Color, is_player: bool) -> void:
 draw_circle(p+Vector2(0,16),17,Color(0.12,0.20,0.13,0.35))
 var sway := sin(elapsed*7.0)*2.0 if is_player else 0.0
 draw_rect(Rect2(p+Vector2(-10,-7+sway),Vector2(20,25)),coat)
 draw_rect(Rect2(p+Vector2(-8,-24+sway),Vector2(16,17)),Color("#eac39f"))
 draw_rect(Rect2(p+Vector2(-10,-27+sway),Vector2(20,7)),Color("#4a352e"))
 draw_rect(Rect2(p+Vector2(-9,17+sway),Vector2(7,10)),Color("#453b39"))
 draw_rect(Rect2(p+Vector2(2,17-sway),Vector2(7,10)),Color("#453b39"))
 if is_player:
  draw_line(p+facing*12,p+facing*30,Color("#e8e8e8"),4)

func _draw_monster(p: Vector2, m: Dictionary) -> void:
 var kind: int = int(m["level"])
 var c := Color(m["color"])
 if m["hit"] > 0:
  c = Color("#f3eeee")
 draw_circle(p+Vector2(0,14),18,Color(0.12,0.20,0.12,0.3))
 if kind <= 3:
  draw_circle(p,18,c)
  draw_rect(Rect2(p+Vector2(-12,-34),Vector2(7,23)),c)
  draw_rect(Rect2(p+Vector2(5,-34),Vector2(7,23)),c)
  if kind == 3:
   draw_colored_polygon(PackedVector2Array([p+Vector2(-5,-14),p+Vector2(0,-38),p+Vector2(5,-14)]),Color("#d9c28c"))
 elif kind == 5:
  draw_colored_polygon(PackedVector2Array([p+Vector2(-22,12),p+Vector2(-20,-8),p+Vector2(-12,-27),p+Vector2(-3,-13),p+Vector2(9,-28),p+Vector2(22,-8),p+Vector2(20,12)]),c)
 else:
  draw_circle(p,21,c)
  draw_colored_polygon(PackedVector2Array([p+Vector2(-18,-6),p+Vector2(-36,-20),p+Vector2(-23,7)]),c)
  draw_colored_polygon(PackedVector2Array([p+Vector2(18,-6),p+Vector2(36,-20),p+Vector2(23,7)]),c)
 draw_circle(p+Vector2(-7,-4),2,Color("#292c24"))
 draw_circle(p+Vector2(7,-4),2,Color("#292c24"))
 draw_rect(Rect2(p+Vector2(-23,-43),Vector2(46,5)),Color("#29352c"))
 draw_rect(Rect2(p+Vector2(-22,-42),Vector2(44.0*float(m["hp"])/float(m["max_hp"]),3)),Color("#e16e68"))
 draw_string(font,p+Vector2(-30,-49),"Lv.%d %s" % [m["level"],m["name"]],HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color.WHITE)

func _save_game() -> void:
 if stage != 3:
  return
 var data := {"name":name_text,"job":job,"stage":stage,"player_x":player.x,"player_y":player.y,"hp":hp,"mp":mp,"level":level,"xp":xp,"points":points,"stats":stats,"equipped":equipped}
 var file := FileAccess.open("user://thor_rpg_v02.json",FileAccess.WRITE)
 if file:
  file.store_string(JSON.stringify(data))

func _load_game() -> void:
 if not FileAccess.file_exists("user://thor_rpg_v02.json"):
  return
 var file := FileAccess.open("user://thor_rpg_v02.json",FileAccess.READ)
 if not file:
  return
 var data = JSON.parse_string(file.get_as_text())
 if typeof(data) != TYPE_DICTIONARY:
  return
 name_text = str(data.get("name",""))
 job = str(data.get("job",""))
 if name_text.is_empty() or not JOBS.has(job):
  return
 stage = 3
 player = Vector2(float(data.get("player_x",1030)),float(data.get("player_y",850)))
 level = maxi(1,int(data.get("level",1)))
 xp = maxi(0,int(data.get("xp",0)))
 points = maxi(0,int(data.get("points",50)))
 var saved_stats = data.get("stats",{})
 if typeof(saved_stats) == TYPE_DICTIONARY:
  for key in STATS:
   stats[key] = maxi(1,int(saved_stats.get(key,1)))
 var saved_equipment = data.get("equipped",{})
 if typeof(saved_equipment) == TYPE_DICTIONARY:
  for slot in equipped:
   var idx: int = int(saved_equipment.get(slot,-1))
   equipped[slot] = idx if idx >= 0 and idx < ITEMS.size() and ITEMS[idx]["slot"] == slot else -1
 hp = clampf(float(data.get("hp",_max_hp())),1.0,_max_hp())
 mp = clampf(float(data.get("mp",_max_mp())),0.0,_max_mp())
