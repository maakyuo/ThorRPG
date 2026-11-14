from pathlib import Path
from PIL import Image,ImageDraw
import random,math
root=Path("godot/assets");root.mkdir(exist_ok=True,parents=True)
def save(im,name): im.save(root/(name+".png"))
def tree(kind):
 r=random.Random(300+kind); im=Image.new("RGBA",(128,176));d=ImageDraw.Draw(im)
 # shadow
 d.ellipse((25,154,104,170),fill=(17,40,23,65))
 # roots, trunk and bark
 d.polygon([(55,156),(44,165),(63,160),(72,160),(90,166),(78,152),(75,79),(57,79)],fill="#493023")
 d.polygon([(61,151),(64,83),(70,83),(70,154)],fill="#946447")
 for j in range(38):
  x=r.randrange(57,77);y=r.randrange(89,156)
  d.line((x,y,x+r.randrange(-3,4),y+r.randrange(3,13)),fill=r.choice(["#493023","#c18a59","#6c4931"]),width=1)
 if kind==1:
  for tier,(cy,w) in enumerate([(114,35),(89,44),(62,36),(37,25)]):
   for k in range(5):
    yy=cy+k*3
    d.polygon([(64,cy-43),(64-w+k*3,yy+17),(64+w-k*3,yy+17)],fill=["#173d38","#21554b","#347367"][k%3])
   for j in range(120):
    x=r.randrange(64-w,64+w);y=r.randrange(cy-28,cy+18)
    if abs(x-64)<w*(y-(cy-43))/65 and y>cy-40:
     d.rectangle((x,y,x+2,y+2),fill=r.choice(["#408979","#79ad87","#173f38","#2c6257"]))
 else:
  centers=[(37,73,29),(66,52,38),(92,79,28),(52,102,37),(84,105,34),(65,78,43)]
  if kind==2:
   d.rectangle((59,85,69,155),fill="#ddd8bc")
   for y in range(90,150,12): d.line((59,y,66,y+3),fill="#41433c",width=3)
   colors=["#8ba95a","#a5c56e","#668f55","#c4d17c","#3f704d"]
  else: colors=["#315c38","#447e40","#5c9747","#80b351","#a0c466"]
  for cx,cy,rad in centers:
   d.ellipse((cx-rad,cy-rad*.75,cx+rad,cy+rad*.7),fill=colors[0])
   for j in range(270):
    a=r.random()*math.tau;rr=math.sqrt(r.random())
    x=int(cx+math.cos(a)*rad*rr);y=int(cy+math.sin(a)*rad*.72*rr)
    d.rectangle((x,y,x+r.randrange(2,6),y+r.randrange(2,5)),fill=r.choice(colors))
 return im
for i in range(3):save(tree(i),"tree_"+str(i))
def gear(kind):
 r=random.Random(kind+90);im=Image.new("RGBA",(48,48));d=ImageDraw.Draw(im)
 dark="#302c30";iron="#d1d9d7";shine="#f3f5e7";gold="#c6a062";wood="#82553c"
 if kind in (0,3):
  # steel blade and ornate crossguard, grip at lower right
  d.polygon([(7,4),(13,7),(34,30),(30,34),(7,13)],fill=iron,outline=dark)
  d.line((10,8,30,30),fill=shine,width=2)
  d.line((25,37,38,24),fill=gold,width=5)
  d.line((32,39,41,30),fill=wood,width=5)
  d.ellipse((37,35,44,42),fill=gold)
 elif kind==1:
  d.line((26,44,19,4),fill=wood,width=6)
  d.ellipse((12,1,29,17),fill="#55c5d2",outline=gold,width=3)
  d.line((26,37,19,20),fill=gold,width=2)
 elif kind==2:
  d.arc((7,3,37,44),65,290,fill=wood,width=5)
  d.arc((8,4,36,43),65,290,fill=gold,width=2)
  d.line((26,8,25,40),fill=shine,width=1)
  d.line((20,27,34,20),fill=iron,width=3)
 elif kind in (8,9):
  d.polygon([(24,4),(41,11),(39,30),(24,44),(9,30),(7,11)],fill=wood if kind==8 else iron,outline=dark)
  d.polygon([(24,9),(35,14),(33,28),(24,37),(15,28),(13,14)],fill="#a36b45" if kind==8 else "#849da8")
  d.line((24,8,24,38),fill=gold,width=4)
  d.ellipse((18,18,30,30),fill=gold,outline=dark)
 else:
  d.polygon([(12,8),(36,8),(41,23),(34,40),(14,40),(7,23)],fill=wood,outline=gold,width=3)
  for j in range(20):
   x=r.randrange(13,35);y=r.randrange(13,37);d.point((x,y),fill="#d7a777")
 return im
for i in range(10):save(gear(i),"gear_"+str(i))
print("Created",len(list(root.glob("tree_*.png"))),"trees and",len(list(root.glob("gear_*.png"))),"equipment sprites")
