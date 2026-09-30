extends Node2D
var rigs:Array[Node2D]=[]
var time:=0.0
var running:=true
var slider:HSlider
var caption:Label
var play:Button
var syncing:=false
func _ready() -> void:
 var scene=load("res://scenes/megumin.tscn")
 for view in [[Vector2(443,856),.42],[Vector2(1104,820),320./1398.]]:
  var rig=scene.instantiate();rig.autoplay=false;add_child(rig)
  rig.position=view[0];rig.scale=Vector2.ONE*view[1];rig.set_process(false)
  rig.player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
  rigs.append(rig)
 _label(Vector2(52,24),"MEGUMIN / CONTINUOUS RIG v3",29)
 _label(Vector2(53,68),"One source anatomy / Fixed-length FK + IK / All VFX off",15)
 _label(Vector2(54,119),"FIXED CAMERA / LARGE VIEW",14)
 _label(Vector2(959,119),"320 px CHARACTER REFERENCE",14)
 _label(Vector2(959,152),"30 fps reference / Realtime playback",16)
 caption=_label(Vector2(54,890),"",19)
 slider=HSlider.new();slider.position=Vector2(52,927);slider.size=Vector2(1080,22);slider.min_value=0.;slider.max_value=5.4;slider.step=.001;add_child(slider)
 slider.value_changed.connect(func(v):
  if not syncing:time=v;_sample())
 play=Button.new();play.text="Pause";play.position=Vector2(1158,916);play.size=Vector2(95,34);add_child(play)
 play.pressed.connect(func():running=not running;play.text="Pause" if running else "Play")
 var replay=Button.new();replay.text="Replay";replay.position=Vector2(1266,916);replay.size=Vector2(100,34);add_child(replay)
 replay.pressed.connect(func():time=0.;running=true;play.text="Pause")
 _sample()
func _label(at:Vector2,text:String,size:int) -> Label:
 var l=Label.new();l.position=at;l.text=text;l.add_theme_font_size_override("font_size",size);add_child(l);return l
func _process(delta:float) -> void:
 if running:time=minf(5.4,time+delta)
 if time>=5.4:running=false;play.text="Play"
 _sample()
func _sample() -> void:
 for rig in rigs:rig.seek_pose(time)
 syncing=true;slider.value=time;syncing=false
 var phase="Prepare / weight shift"
 if time>=.65:phase="Elbow lift"
 if time>=1.6:phase="Raise / chant"
 if time>=2.8:phase="Quick release"
 if time>=3.35:phase="Recover"
 if time>=4.45:phase="Shoulders / head settle"
 if time>=5.:phase="Return to natural idle"
 caption.text="%s  |  %.2f s / 5.40 s"%[phase,time]
func _draw() -> void:
 draw_rect(Rect2(32,108,880,776),Color("101b2b"));draw_rect(Rect2(938,108,470,776),Color("142133"))
 for y in range(200,830,80):draw_line(Vector2(54,y),Vector2(887,y),Color("172638"))
 draw_line(Vector2(54,856),Vector2(886,856),Color("3a5067"))
 draw_line(Vector2(958,820),Vector2(1386,820),Color("40586f"))
