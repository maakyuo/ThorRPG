extends Node2D

const WORLD := Vector2(1800, 1100)
const SPEED := 190.0
const WOLF_SPEED := 88.0
const ATTACK_RANGE := 83.0
var player := Vector2(900, 550)
var hp := 100.0
var level := 1
var xp := 0
var points := 50
var stats := {"근력":1,"민첩":1,"지능":1,"체력":1,"마력":1}
var wolves: Array[Dictionary] = []
var attack_cd := 0.0
var dodge_cd := 0.0
var invuln := 0.0
var facing := Vector2.DOWN
var touch_move := Vector2.ZERO
var touch_origin := Vector2.ZERO
var touch_id := -1
var message := "Lv.5 늑대를 처치해 보세요"
var message_time := 4.0
var save_clock := 0.0
var font: Font

func _ready() -> void:
	font = ThemeDB.fallback_font
	_load_game()
	if wolves.is_empty():
		for i in 8:
			_spawn_wolf(i)
	queue_redraw()

func _spawn_wolf(i: int) -> void:
	var a := float(i) * TAU / 8.0
	var pos := player + Vector2(cos(a), sin(a)) * (260.0 + float(i % 3) * 100.0)
	pos = pos.clamp(Vector2(50,50), WORLD - Vector2(50,50))
	wolves.append({"pos":pos,"hp":55.0,"alive":true,"respawn":0.0,"hit":0.0,"attack":0.0})

func _physics_process(delta: float) -> void:
	attack_cd = maxf(0.0,attack_cd-delta)
	dodge_cd = maxf(0.0,dodge_cd-delta)
	invuln = maxf(0.0,invuln-delta)
	message_time = maxf(0.0,message_time-delta)
	var move := Input.get_vector("move_left","move_right","move_up","move_down")
	if touch_move.length() > 0.1:
		move = touch_move
	if move.length() > 0.1:
		facing = move.normalized()
		player = (player + move * SPEED * delta).clamp(Vector2(28,28),WORLD-Vector2(28,28))
	if Input.is_action_just_pressed("attack"):
		_attack()
	if Input.is_action_just_pressed("dodge"):
		_dodge()
	for i in wolves.size():
		var w: Dictionary = wolves[i]
		if not w["alive"]:
			w["respawn"] -= delta
			if w["respawn"] <= 0:
				w["alive"] = true
				w["hp"] = 55.0
				w["pos"] = Vector2(randf_range(90,1710),randf_range(90,1010))
			continue
		w["hit"] = maxf(0.0,w["hit"]-delta)
		w["attack"] = maxf(0.0,w["attack"]-delta)
		var diff: Vector2 = player - w["pos"]
		var distance := diff.length()
		if distance < 340 and distance > 39:
			w["pos"] += diff.normalized() * WOLF_SPEED * delta
		elif distance <= 42 and w["attack"] <= 0:
			w["attack"] = 1.25
			if invuln <= 0:
				hp = maxf(0.0,hp-8.0)
				invuln = 0.45
				if hp <= 0:
					player = WORLD * 0.5
					hp = 100.0
					message = "쓰러졌습니다. 초원 중앙에서 부활했습니다."
					message_time = 3.0
	save_clock += delta
	if save_clock > 12:
		save_clock = 0
		_save_game()
	queue_redraw()

func _attack() -> void:
	if attack_cd > 0:
		return
	attack_cd = 0.45
	for i in wolves.size():
		var w: Dictionary = wolves[i]
		if not w["alive"]:
			continue
		var offset: Vector2 = w["pos"]-player
		if offset.length() <= ATTACK_RANGE and (offset.length() < 35 or facing.dot(offset.normalized()) > 0.05):
			w["hp"] -= 12.0 + float(stats["근력"]) * 3.0
			w["hit"] = 0.22
			if w["hp"] <= 0:
				w["alive"] = false
				w["respawn"] = 12.0
				xp += 50
				message = "Lv.5 늑대 처치! 경험치 +50"
				message_time = 2.0
				while xp >= level * 100:
					xp -= level * 100
					level += 1
					points += 5
					hp = 100.0
					message = "레벨 업! Lv.%d / 능력치 포인트 +5" % level
				_save_game()

func _dodge() -> void:
	if dodge_cd > 0:
		return
	dodge_cd = 1.0
	invuln = 0.32
	player = (player + facing * 115.0).clamp(Vector2(28,28),WORLD-Vector2(28,28))

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var p: Vector2 = event.position
		var s := get_viewport_rect().size
		if event.pressed:
			if p.x < s.x * 0.42 and p.y > s.y * 0.42:
				touch_id = event.index
				touch_origin = p
				touch_move = Vector2.ZERO
			elif p.x > s.x * 0.82 and p.y > s.y * 0.60:
				_attack()
			elif p.x > s.x * 0.66 and p.y > s.y * 0.60:
				_dodge()
			elif p.y < 72 and p.x > s.x * 0.75 and points > 0:
				stats["근력"] += 1
				points -= 1
				_save_game()
		elif event.index == touch_id:
			touch_id = -1
			touch_move = Vector2.ZERO
	elif event is InputEventScreenDrag and event.index == touch_id:
		touch_move = ((event.position-touch_origin)/70.0).limit_length(1.0)

func _draw() -> void:
	var s := get_viewport_rect().size
	var camera := player-s*0.5
	camera = camera.clamp(Vector2.ZERO,WORLD-s)
	draw_rect(Rect2(Vector2.ZERO,s),Color("#79a95f"))
	var start_x := int(camera.x/64.0)
	var start_y := int(camera.y/64.0)
	for x in range(start_x,start_x+int(s.x/64.0)+2):
		for y in range(start_y,start_y+int(s.y/64.0)+2):
			var p := Vector2(x*64,y*64)-camera
			var variant := (x*31+y*17) % 5
			draw_rect(Rect2(p,Vector2(64,64)),Color("#77a65e") if variant < 2 else Color("#7eae64"))
			if (x*7+y*13) % 4 == 0:
				draw_line(p+Vector2(18,30),p+Vector2(20,23),Color("#487d42"),2)
				draw_line(p+Vector2(18,30),p+Vector2(15,25),Color("#487d42"),2)
	for w in wolves:
		if not w["alive"]:
			continue
		var p: Vector2 = w["pos"]-camera
		if p.x < -50 or p.x > s.x+50 or p.y < -50 or p.y > s.y+50:
			continue
		draw_ellipse_shadow(p)
		draw_colored_polygon(PackedVector2Array([p+Vector2(-21,-6),p+Vector2(-14,-24),p+Vector2(-3,-13),p+Vector2(7,-25),p+Vector2(21,-7),p+Vector2(18,13),p+Vector2(-18,13)]),Color("#c9d2d0") if w["hit"] > 0 else Color("#68767c"))
		draw_circle(p+Vector2(-7,-4),2,Color("#f0db8c"))
		draw_circle(p+Vector2(8,-4),2,Color("#f0db8c"))
		draw_rect(Rect2(p+Vector2(-23,-35),Vector2(46,5)),Color("#29342b"))
		draw_rect(Rect2(p+Vector2(-22,-34),Vector2(44.0*float(w["hp"])/55.0,3)),Color("#dd6864"))
		draw_string(font,p+Vector2(-21,-40),"Lv.5 늑대",HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
	var center := player-camera
	draw_ellipse_shadow(center)
	draw_rect(Rect2(center+Vector2(-10,-9),Vector2(20,26)),Color("#335c91"))
	draw_rect(Rect2(center+Vector2(-8,-25),Vector2(16,16)),Color("#edc49b"))
	draw_rect(Rect2(center+Vector2(-10,-28),Vector2(20,7)),Color("#42362e"))
	draw_line(center+facing*12,center+facing*32,Color("#dfe6ec"),4)
	if invuln > 0:
		draw_arc(center,24,0,TAU,24,Color("#bde8ff"),2)
	if attack_cd > 0.25:
		draw_arc(center,ATTACK_RANGE,atan2(facing.y,facing.x)-0.8,atan2(facing.y,facing.x)+0.8,20,Color("#f7e8b2"),3)
	draw_rect(Rect2(8,8,205,54),Color(0.08,0.13,0.1,0.82))
	draw_string(font,Vector2(16,26),"Lv.%d   HP %d/100" % [level,int(hp)],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE)
	draw_rect(Rect2(16,31,183,8),Color("#263b2b"))
	draw_rect(Rect2(16,31,183*hp/100.0,8),Color("#e66c69"))
	draw_string(font,Vector2(16,54),"EXP %d/%d   포인트 %d" % [xp,level*100,points],HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color.WHITE)
	if points > 0:
		draw_rect(Rect2(s.x-180,8,172,45),Color("#264f38"))
		draw_string(font,Vector2(s.x-172,27),"근력 +1 (터치)",HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color.WHITE)
		draw_string(font,Vector2(s.x-172,45),"남은 포인트 %d" % points,HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color.WHITE)
	if message_time > 0:
		draw_string(font,Vector2(s.x*0.3,45),message,HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("#fff4ca"))
	draw_circle(Vector2(88,s.y-83),67,Color(0.08,0.16,0.13,0.45))
	draw_circle(Vector2(s.x-73,s.y-73),49,Color(0.36,0.19,0.15,0.7))
	draw_string(font,Vector2(s.x-94,s.y-66),"공격",HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color.WHITE)
	draw_circle(Vector2(s.x-187,s.y-73),40,Color(0.13,0.24,0.38,0.7))
	draw_string(font,Vector2(s.x-207,s.y-67),"회피",HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color.WHITE)

func draw_ellipse_shadow(p: Vector2) -> void:
	draw_circle(p+Vector2(0,16),18,Color(0.16,0.29,0.14,0.4))

func _save_game() -> void:
	var f := FileAccess.open("user://save.json",FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"player_x":player.x,"player_y":player.y,"level":level,"xp":xp,"points":points,"stats":stats}))

func _load_game() -> void:
	if not FileAccess.file_exists("user://save.json"):
		return
	var f := FileAccess.open("user://save.json",FileAccess.READ)
	if not f:
		return
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return
	player = Vector2(float(data.get("player_x",900)),float(data.get("player_y",550)))
	level = maxi(1,int(data.get("level",1)))
	xp = maxi(0,int(data.get("xp",0)))
	points = maxi(0,int(data.get("points",50)))
	var saved = data.get("stats",{})
	if typeof(saved) == TYPE_DICTIONARY:
		for key in stats:
			stats[key] = maxi(1,int(saved.get(key,1)))
