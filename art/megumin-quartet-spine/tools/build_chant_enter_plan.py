"""Author a 60 Hz motion specification, without changing any shipped animation."""
from pathlib import Path
import math, json, csv, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.build-deps'))
from PIL import Image
from shapely.geometry import Polygon, Point, MultiPoint
import numpy as np
OUT=ROOT/'chant-enter-plan'; OUT.mkdir(exist_ok=True)
B=json.loads((OUT/'baseline-v5.json').read_text(encoding='utf-8'))
bind=B['frames'][0]['bones']
def xy(n):return [bind[n]['x'],bind[n]['y']]
def add(a,b):return [a[0]+b[0],a[1]+b[1]]
def vector(length,angle):return [length*math.cos(math.radians(angle)),length*math.sin(math.radians(angle))]
def rotate(p,a):return [p[0]*math.cos(math.radians(a))-p[1]*math.sin(math.radians(a)),p[0]*math.sin(math.radians(a))+p[1]*math.cos(math.radians(a))]
def interpolation(keys,x):
    # Monotone cubic Hermite: continuous velocity, no stop at every authored pose.
    xs=[p[0] for p in keys]; ys=[p[1] for p in keys]
    if x<=xs[0]:return ys[0]
    if x>=xs[-1]:return ys[-1]
    h=[b-a for a,b in zip(xs,xs[1:])]; d=[(b-a)/s for a,b,s in zip(ys,ys[1:],h)]
    m=[0.]*len(xs)
    for i in range(1,len(xs)-1):
        if d[i-1]*d[i]>0:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1]
            m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i])
    i=next(i for i in range(len(xs)-1) if xs[i]<=x<xs[i+1]);t=(x-xs[i])/h[i]
    return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h[i]*m[i+1]
upper0=bind['upper_r']['angle']; fold0=bind['fore_r']['angle']-upper0
K={
 'root_x':[(0,0),(6,-3),(12,-8),(20,-3),(30,1),(42,4),(54,6),(62,6),(72,6)],
 'root_y':[(0,0),(6,-1),(12,-5),(18,-5),(30,-4.5),(42,-4),(54,-3.5),(62,-3.5),(72,-3.5)],
 'body_yaw':[(0,0),(6,1),(12,9),(20,26),(30,43),(42,50),(54,50),(72,50)],
 'head_yaw':[(0,0),(3,5),(6,13),(12,27),(20,43),(30,53),(42,55),(72,55)],
 'pelvis_yaw':[(0,0),(8,0),(14,6),(22,21),(32,30),(42,32),(72,32)],
 'lean':[(0,0),(12,-1),(24,-3),(36,-5),(48,-7),(56,-8),(62,-7.5),(72,-7.5)],
 'upper_r':[(0,upper0),(6,-148),(12,-136),(18,-108),(24,-84),(30,-61),(36,-46),(42,-36),(48,-24),(54,-12),(58,-8),(64,-12),(72,-12)],
 'fold_r':[(0,fold0),(6,-24),(12,-26),(18,-25),(24,-13),(30,0),(36,20),(42,38),(48,36),(54,28),(58,24),(64,30),(72,30)],
 'staff_axis':[(0,107.745),(6,95),(12,58),(18,35),(24,18),(30,15),(36,16),(42,18),(48,22),(54,25),(58,24),(64,22),(72,22)],
 'upper_l':[(0,bind['upper_l']['angle']),(8,-77),(16,-81),(24,-85),(32,-84),(42,-80),(52,-80),(62,-81),(72,-81)],
 'fold_l':[(0,bind['fore_l']['angle']-bind['upper_l']['angle']),(8,8),(16,12),(24,20),(32,18),(42,15),(52,15),(62,14),(72,14)],
 'left_step_x':[(0,0),(10,0),(14,2),(18,6),(20,8),(72,8)],
 'left_step_y':[(0,0),(10,0),(14,4),(16,3),(19,1),(20,0),(72,0)],
 'cape':[(0,0),(8,0),(16,-2),(26,-8),(36,-11),(46,-6),(56,3),(64,-1),(70,0),(72,0)],
 'hat':[(0,0),(8,-1),(18,-3),(30,-2),(42,1.2),(52,0),(58,-.7),(66,0),(72,0)],
 'hair':[(0,0),(10,0),(20,-4),(32,-6),(44,-2),(54,2),(64,-.5),(70,0),(72,0)],
 'gaze':[(0,0),(3,1),(72,1)],
 'mouth':[(0,0),(51,0),(54,.3),(57,.6),(60,.3),(63,.45),(66,.2),(70,.15),(72,.15)]
}
# The staff is rigid. Read its existing alpha pixels for a conservative envelope;
# no pixels are edited and no new character artwork is implied by this document.
poly_source=[(27,168),(113,167),(145,357),(169,368),(202,386),(232,409),(253,438),(268,475),(273,515),(269,538),(266,558),(242,605),(273,723),(317,846),(344,938),(398,1144),(471,1306),(475,1350),(394,1363),(377,1347),(384,1245),(352,1164),(319,1065),(281,937),(268,851),(230,735),(195,666),(148,622),(121,596),(128,563),(111,516),(120,471),(143,438),(133,428),(107,451),(84,421),(26,279)]
shape=Polygon(poly_source).difference(Polygon([(465,1298),(480,1298),(480,1368),(426,1368),(429,1350),(457,1349)]))
im=np.array(Image.open(ROOT/'actions-v5/source/clean-reference.png').convert('RGBA'))
ys,xs=np.where(im[:,:,3]>100)
from shapely import contains_xy
inside=contains_xy(shape,xs,ys);xs=xs[inside];ys=ys[inside]
staff_hull=list(MultiPoint(np.stack([xs,ys],axis=1)).convex_hull.exterior.coords)
staff_points=[[(x-310)*320/1320,(886-y)*320/1320] for x,y in staff_hull]
orb_offset=[(184-310)*320/1320,(886-492)*320/1320]
axis0=math.degrees(math.atan2(orb_offset[1],orb_offset[0]));K['staff_axis'][0]=(0,axis0)
def make_pose(f):
    p={n:interpolation(v,f) for n,v in K.items()};p['f']=f;p['t']=f/60
    pelvis=add(xy('pelvis'),[p['root_x'],p['root_y']]);p['pelvis']=pelvis
    p['chest']=add(pelvis,rotate([xy('chest')[0]-xy('pelvis')[0],xy('chest')[1]-xy('pelvis')[1]],p['lean']))
    p['head']=add(pelvis,rotate([xy('head')[0]-xy('pelvis')[0],xy('head')[1]-xy('pelvis')[1]],p['lean']))
    yaw=math.cos(math.radians(p['body_yaw']))
    # Projected shoulder span narrows gradually; head/torso yaw are art targets.
    for side in ['r','l']:
        s0=xy('upper_'+side);c0=xy('chest');local=[(s0[0]-c0[0])*yaw,s0[1]-c0[1]]
        p['shoulder_'+side]=add(p['chest'],rotate(local,p['lean']))
        p['elbow_'+side]=add(p['shoulder_'+side],vector(bind['upper_'+side]['length'],p['upper_'+side]))
        p['wrist_'+side]=add(p['elbow_'+side],vector(bind['fore_'+side]['length'],p['upper_'+side]+p['fold_'+side]))
    p['staff_rotation']=p['staff_axis']-axis0
    p['orb']=add(p['wrist_r'],rotate(orb_offset,p['staff_rotation']))
    p['staff_hull']=[add(p['wrist_r'],rotate(v,p['staff_rotation'])) for v in staff_points]
    p['staff_floor']=min(v[1] for v in p['staff_hull'])
    p['foot_r']=xy('foot_r');p['foot_l']=add(xy('foot_l'),[p['left_step_x'],p['left_step_y']])
    # Draw/record a two-bone leg with fixed segment lengths, same bend side.
    for side in ['r','l']:
        h=add(xy('thigh_'+side),[p['root_x'],p['root_y']]);a=p['foot_'+side];l1=bind['thigh_'+side]['length'];l2=bind['shin_'+side]['length']
        dx,dy=a[0]-h[0],a[1]-h[1];d=math.hypot(dx,dy);p['leg_reach_'+side]=d/(l1+l2)
        sign=1;cosine=max(-1,min(1,(l1*l1+d*d-l2*l2)/(2*l1*d)))
        angle=math.degrees(math.atan2(dy,dx))-sign*math.degrees(math.acos(cosine))
        p['hip_'+side]=h;p['knee_'+side]=add(h,vector(l1,angle))
    # Face keep-out ellipse is deliberately larger than the expression patch.
    p['face']=[p['head'][0]+p['head_yaw']/55*5,p['head'][1]+26,24-p['head_yaw']/55*7,30]
    cx,cy,rx,ry=p['face'];normalized=Polygon([((x-cx)/rx,(y-cy)/ry) for x,y in p['staff_hull']])
    p['face_clearance_ratio']=normalized.distance(Point(0,0))
    p['staff_behind_head']=8<=f<=35
    return p
notes='''保持已认可待机起点；握点、脚底、帽檐不跳位。
瞳孔先向画面右侧移，法杖仅作极小的松动。
视线继续右移，右手只维持原握力。
视线锁定目标，头开始跟随；不要让法杖抢先。
下巴略收，头转量增加，重心开始微沉。
右腿接重，左脚准备松跟；杖身仍在身体左侧。
完成眼神引导，头已领先胸口，杖尾开始离地。
胸口开始右转，右肩轻内收，手腕不抬向脸。
骨盆开始跟转；左脚仍有接地，不滑动。
右膝微屈吸收重心，左脚将离地。
左脚离地前的最后接触帧；杖尾已获得上移空间。
左脚抬起，脚尖离地；握杖手贴近左下方。
重心最低阶段；法杖已倾向右方，从头部后侧通过。
左脚向右前方摆出，脚掌抬高，胸口继续转。
左脚摆动高度峰值，脚尖朝目标调整，右脚保持支撑。
左脚开始下降；右肘向下领动，握点开始走低弧。
髋部跟上胸口，法杖上端从头部后侧向下走。
右手向身体靠近，杖尖投影重叠时由头部遮住。
左脚接近地面；杖杆已经明显倾斜，不能抬过帽檐。
左脚前掌接触，开始接重，左跟尚未完全压实。
左脚全掌落定；后续前送都由这个站稳姿势支撑。
骨盆继续小幅转正，握点降向腰带下方。
右肘沿身体前下方移动，左臂放松下垂让位。
法杖头部继续下降，逐步从下巴下方露出。
右臂投影继续打开，检查袖口与杖杆分离。
握点越过身体左缘，右肩向目标方向滚动。
杖头已处于脸部下方；上臂继续向前摆。
右肘打开，前臂与杖杆一起前送，握点不可滑动。
右臂逐渐伸长，左手降至髋旁，形成轮廓间隙。
接近右臂投影共线；肘尖的可见面开始交接。
右臂投影共线，仅此处转换弯曲投影；肘关节不反折。
右肘从共线进入另一可见面，保持位置和速度连续。
肩、肘、腕组成向右下的长线，胸口已基本转到位。
右手开始向前上方走，法杖倾角只缓慢回升。
肘尖留在手腕下方，避免前臂翻到上臂背面。
左手继续在髋旁放松，与杖尾保留明显空隙。
进入前送中段：杖头领先，肩不耸起。
握点升向胸前高度，右腕只随杖转动。
身体转动减速，手臂继续运动，保留先后关系。
右肘略弯缓冲，左肩随躯干转面，披风仍滞后展开。
前脚稳定接重，后脚保持脚掌固定。
右手继续升高，法杖与视线逐渐同向。
胸口朝向达到目标；右臂仍在完成伸展。
右肘继续向前下方摆，保持肩至腕的顺畅折线。
头停止主转动，头发开始追上。
右手向前推进，杖尾避开自由手和腰部轮廓。
帽尖出现很小的回摆，身体不再跟着左右摇。
左手在髋旁接近放松终点，五指自然打开，不抓杖尾。
右上臂向前抬，腕点接近最终吟唱高度。
前送明显减速；肩线保持低，不能耸肩发力。
法杖角度接近最终值，脸和杖头之间有清晰负空间。
左臂开始回收极小过量，保持专注表情。
身体继续缓冲，禁止做攻击后坐。
右手最后一小段上提；头与身体转面维持终点。
到达第一稳定姿势，表情保持专注。
右手允许很小的前上惯性，手指持续闭合握杖。
躯干前倾到峰值，披风向反方向轻回摆。
头部继续稳定；右臂继续缓冲，不触发释放特效。
右手前送过量达到峰值，开始温和回收。
握点回撤幅度小于动作主行程，法杖仍指向目标。
表情保持专注，躯干前倾开始回收。
右肘恢复最终弯度；左手已经安定。
身体到达最终倾角，主动作将结束。
头部朝向保持，右腕与杖身同步收稳。
握点、肘角和法杖角度到达最终值；后面只收余动。
帽檐与头发回摆幅度进一步减小。
帽尖结束余动，表情保持循环入口状态。
肩、肘、腕完全稳定，只有披风尾端仍轻动。
披风尾端最后一次回正，眼神始终盯住前方。
头发与披风进入接近静止的收尾。
所有附属摆动回到循环起始值，表情保持稳定。
保持入口姿势一帧，检查脚底、握点与衣片遮挡。
进入新吟唱循环的第零帧；由播放状态接入循环，禁止释放伤害。'''.splitlines()
assert len(notes)==73,len(notes)
phase=lambda f:0 if f<=6 else 1 if f<=20 else 2 if f<=32 else 3 if f<=48 else 4 if f<=64 else 5
phases=['目光先行','落脚转体','低弧让脸','单手前送','缓冲入唱','收尾接环']
def layer(f):
    if 8<=f<=35:return '杖在头/帽后、躯干前；右手始终持杖'
    return '右臂和杖在躯干前；左手在髋旁放松'
frames=[]
for f in range(73):
    p=make_pose(f);p.update(note=notes[f],phase=phases[phase(f)],phase_id=phase(f),layer=layer(f),feet='右脚固定；左脚全掌接地' if f<=10 else '右脚固定；左脚腾空' if f<19 else '右脚固定；左前掌接地' if f==19 else '双脚全掌固定',event='播放状态接入 chant_loop@0；无伤害事件' if f==72 else '无',key=f in [0,6,12,14,20,24,30,32,42,48,54,58,64,70,72])
    frames.append(p)
dense=[make_pose(i/4) for i in range(289)]
audit={'scope':'规划几何的数值检查；不代表完成角色贴图、遮挡、美术或游戏内验证。长杖绕头后侧通过，投影重叠依赖指定遮挡。','samples_240hz':len(dense),'min_staff_floor':min(p['staff_floor'] for p in dense),'unmasked_face_overlap_samples':sum(p['face_clearance_ratio']<1 and not p['staff_behind_head'] for p in dense),'planned_head_occlusion_frames':[p['f'] for p in frames if p['face_clearance_ratio']<1],'max_leg_reach_ratio':max(p['leg_reach_'+s] for p in dense for s in ['r','l']),'max_wrist_step_per_frame':max(math.dist(a['wrist_r'],b['wrist_r']) for a,b in zip(frames,frames[1:])),'fixed_grip':True,'arm_lengths_fixed':True,'projected_elbow_zero_frame':30,'old_first_side_frame':47}
out={'title':'惠惠 · 进入吟唱逐帧规划','status':'motion specification / schematic only','fps':60,'duration':1.2,'frame_intervals':72,'pose_samples':73,'coordinate_system':'沿用 v5 Spine 世界坐标；角色站高约320 px；X向右，Y向上，地面Y=0；旋转逆时针为正；朝向是相对原图的美术目标，不是现有3D骨骼测量。','interpolation':'monotone cubic Hermite, weighted harmonic interior tangents, zero endpoint tangents; fixed arm lengths + FK.','keys':K,'phases':phases,'frames':frames,'audit':audit,'staff_hull_local':staff_points,'staff_axis0':axis0}
(OUT/'frame-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'frame-plan.csv').open('w',encoding='utf-8-sig',newline='') as file:
    fields=['帧','秒','阶段','逐帧指令','根X','根Y','头朝向','胸朝向','髋朝向','前倾','右肩X','右肩Y','右肘X','右肘Y','右腕X','右腕Y','右上臂角','右肘投影折角','左腕X','左腕Y','法杖轴角','杖包络最低Y','左脚前移','左脚抬高','脚底接触','帽滞后角','发滞后角','披风滞后角','嘴开合','遮挡','事件']
    w=csv.writer(file);w.writerow(fields)
    for p in frames:w.writerow([p['f'],round(p['t'],4),p['phase'],p['note'],*[round(p[k],3) for k in ['root_x','root_y','head_yaw','body_yaw','pelvis_yaw','lean']],*[round(n,3) for k in ['shoulder_r','elbow_r','wrist_r'] for n in p[k]],round(p['upper_r'],3),round(p['fold_r'],3),*[round(n,3) for n in p['wrist_l']],*[round(p[k],3) for k in ['staff_axis','staff_floor','left_step_x','left_step_y']],p['feet'],*[round(p[k],3) for k in ['hat','hair','cape','mouth']],p['layer'],p['event']])
print(json.dumps(audit,indent=2,ensure_ascii=False))
