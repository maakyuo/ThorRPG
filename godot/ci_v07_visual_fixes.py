from pathlib import Path
p=Path("godot/experiment_v02.gd")
s=p.read_text()
# Trees are stable world objects. Draw all of them: no edge-triggered popping.
s=s.replace('''  if screen_pos.x < -130.0*scale or screen_pos.x > s.x+130.0*scale:
   continue
  if screen_pos.y < -210.0*scale or screen_pos.y > s.y+100.0*scale:
   continue
  _draw_forest_tree(screen_pos,int(tree["variant"]),scale)''','''  _draw_forest_tree(screen_pos,int(tree["variant"]),scale)''')
# Larger trees, rendered from complete source sprites.
s=s.replace('var tree_size := Vector2(158.0,208.0)*scale','var tree_size := Vector2(220.0,288.0)*scale')
# Don't render equipment in free-floating world space. Tie hand to player's body pose and facing.
a=s.index('func _draw_equipped(center: Vector2) -> void:')
b=s.index('func _draw_house(',a)
s=s[:a]+'''func _draw_equipped(center: Vector2) -> void:
 var weapon_idx: int=int(equipped.get("무기",-1))
 var shield_idx: int=int(equipped.get("방패",-1))
 if weapon_idx<0 and shield_idx<0: return
 # Hand anchors are local to the character sprite, not to the world.
 # Match body facing and animation. Right/left reverse arm placement.
 var direction: int=facing_index
 var walking: bool=touch_move.length()>0.1 or Input.get_vector("move_left","move_right","move_up","move_down").length()>0.1
 var stride: float=sin(elapsed*10.0)*2.0 if walking else 0.0
 var right_hand := Vector2(13,-4)
 var left_hand := Vector2(-13,-4)
 match direction:
  0:
   right_hand=Vector2(13,-2)
   left_hand=Vector2(-13,-2)
  1:
   right_hand=Vector2(16,-10)
   left_hand=Vector2(-6,-7)
  2:
   right_hand=Vector2(12,-6)
   left_hand=Vector2(-12,-6)
  3:
   right_hand=Vector2(-16,-10)
   left_hand=Vector2(6,-7)
 right_hand.y+=stride
 left_hand.y-=stride
 var attacking: bool=attack_visual>0
 var swing: float=sin((0.30-attack_visual)/0.30*PI)*0.8 if attacking else 0.0
 if weapon_idx>=0:
  var weapon_tex: Texture2D=_item_icon(weapon_idx)
  var grip: Vector2=center+right_hand
  var angle: float=0.0
  if direction==1: angle=-PI*0.35
  elif direction==3: angle=PI*0.35
  elif direction==2: angle=PI
  angle+=swing*(-1.0 if direction==3 else 1.0)
  # Weapon icon's lower end is the grip, which stays at the hand.
  draw_set_transform(grip,angle,Vector2.ONE)
  draw_texture_rect(weapon_tex,Rect2(Vector2(-16,-26),Vector2(32,32)),false)
  draw_set_transform(Vector2.ZERO)
 if shield_idx>=0:
  var shield_tex: Texture2D=_item_icon(shield_idx)
  var shield_grip: Vector2=center+left_hand
  draw_texture_rect(shield_tex,Rect2(shield_grip-Vector2(13,15),Vector2(26,26)),false)

'''+s[b:]
p.write_text(s)
print("Stable trees, enlarged sprites, hand-anchored equipment.")
