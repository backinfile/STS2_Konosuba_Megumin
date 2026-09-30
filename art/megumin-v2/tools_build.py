import json,math,pathlib
from scipy.spatial import Delaunay
ROOT=pathlib.Path(__file__).parent
# Geometry-only cuts. The PNG files remain byte-identical to generated originals.
parts=[]
def part(name,pts,group,z=0,texture='master',mesh=False,uv=None):
    pts=[list(p) for p in pts]
    if mesh:
        def inside(x,y):
            c=False;j=len(pts)-1
            for i in range(len(pts)):
                xi,yi=pts[i];xj,yj=pts[j]
                if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:c=not c
                j=i
            return c
        p=pts+[[x,y] for y in range(int(min(p[1] for p in pts))+30,int(max(p[1] for p in pts)),55) for x in range(int(min(p[0] for p in pts))+30,int(max(p[0] for p in pts)),55) if inside(x,y)]
        tri=Delaunay(p).simplices
        tris=[t.tolist() for t in tri if inside(sum(p[k][0] for k in t)/3,sum(p[k][1] for k in t)/3)]
    else:p=pts;tris=[]
    parts.append(dict(name=name,vertices=p,uv=uv or p,triangles=tris,group=group,z=z,texture=texture))
part('cape_left',[(449,491),(454,516),(416,542),(384,577),(362,613),(351,642),(354,665),(375,689),(390,729),(409,751),(433,763),(445,777),(468,827),(478,866),(450,947),(406,1036),(427,1100),(365,1107),(294,1085),(251,1059),(245,1037),(223,1035),(165,1041),(105,1022),(72,988),(57,948),(49,933),(21,925),(8,896),(5,852),(0,824),(0,766),(0,719),(11,686),(52,669),(114,661),(185,660),(235,667),(259,696),(299,673),(340,634),(371,589),(413,537),(441,488)],'cape',-5,mesh=True)
part('cape_lower',[(590,879),(632,879),(650,918),(666,983),(690,1085),(705,1110),(480,1110),(480,1073),(502,1035),(538,976),(566,929)],'cape',-6,mesh=True)
part('cape_right',[(719,692),(741,758),(772,831),(813,909),(850,995),(823,990),(801,1000),(783,1017),(771,1023),(769,965),(766,916),(757,868),(736,790)],'cape',-5,mesh=True)
# Hidden cape backing reconstructed only by UV remapping an intact cloth patch.
# It fills artwork occluded by the original arms; no PNG pixels are painted or changed.
part('cape_occlusion_fill',[(435,507),(517,520),(653,515),(701,638),(731,748),(753,832),(765,970),(751,1022),(711,1015),(660,1015),(600,1008),(545,1020),(413,1045),(404,1030),(450,944),(478,866),(471,826),(445,777),(434,760),(398,728),(363,687),(350,645),(367,597),(400,549)],'cape',-7,mesh=True)
parts[-1]['uv']=[[210+(x-350)/420*100,780+(y-500)/580*170] for x,y in parts[-1]['vertices']]
# The lower body is cut directly from the master with a stable sole anchor.
part('leg_left',[(494,808),(633,847),(593,937),(546,1045),(493,1141),(407,1242),(413,1269),(390,1310),(348,1313),(343,1370),(333,1452),(322,1499),(277,1508),(243,1503),(241,1470),(264,1417),(280,1376),(280,1323),(291,1279),(278,1267),(285,1245),(298,1210),(325,1205),(352,1124),(400,1049),(450,952),(477,867)],'legs',0)
part('leg_right',[(616,843),(736,831),(745,883),(745,939),(756,1020),(779,1105),(800,1205),(818,1208),(837,1244),(843,1275),(825,1291),(815,1330),(839,1376),(847,1405),(885,1425),(904,1451),(907,1465),(858,1473),(811,1468),(766,1445),(765,1418),(759,1386),(760,1317),(746,1298),(727,1291),(722,1268),(721,1245),(695,1158),(676,1052),(655,951),(640,907)],'legs',1)
# Matched source torso patch. Source y=440/610/680 maps to master y=520/680/735.
uv=[(506,411),(625,405),(653,420),(680,451),(692,506),(694,559),(713,606),(717,672),(641,662),(552,645),(521,614),(534,578),(520,552),(505,503),(496,472),(506,448)]
def map_y(y): return y+70
verts=[(x+15*max(0,min(1,(640-y)/200)),map_y(y)) for x,y in uv]
part('occlusion_torso',verts,'torso',2,texture='base',uv=uv)
part('skirt',[(547,659),(630,655),(699,670),(719,705),(736,752),(756,792),(768,856),(754,871),(739,881),(705,882),(667,878),(622,876),(593,872),(550,867),(510,856),(469,872),(443,860),(432,843),(418,822),(413,807),(439,779),(463,749),(499,710)],'skirt',4)
part('head_and_collar',[(249,296),(260,256),(286,235),(308,220),(346,178),(383,137),(456,109),(493,108),(541,126),(592,160),(623,164),(648,191),(670,240),(722,242),(786,243),(841,254),(859,267),(850,293),(818,327),(773,359),(690,396),(693,429),(680,465),(699,507),(681,532),(654,532),(628,520),(603,511),(578,512),(547,504),(513,512),(488,531),(454,549),(417,566),(422,536),(436,505),(460,476),(478,456),(440,454),(398,454),(350,455),(304,451),(285,440),(288,425),(326,392),(365,357),(397,332),(404,307),(338,314),(301,326),(276,321),(264,310)],'head',5)
# Independent articulated arm pieces. Shoulder, elbow and wrist pivots are documented in the rig.
part('arm_left_upper',[(476,516),(501,517),(518,528),(524,544),(519,561),(501,574),(481,580),(457,598),(444,620),(458,654),(451,698),(432,744),(415,739),(397,718),(388,688),(362,662),(355,642),(365,610),(387,578),(414,558),(446,540)],'left_upper',6)
part('arm_left_forearm',[(441,602),(459,599),(477,604),(491,586),(514,569),(541,550),(558,522),(568,515),(573,520),(572,537),(566,552),(588,543),(597,544),(599,552),(592,559),(570,572),(590,570),(598,573),(598,581),(591,588),(567,596),(550,602),(573,619),(577,627),(572,633),(563,630),(540,618),(526,627),(506,634),(482,636),(470,636),(455,646),(439,652)],'left_forearm',7)
part('arm_right_upper',[(650,522),(676,520),(698,545),(714,571),(739,590),(753,604),(753,636),(746,653),(727,667),(707,656),(693,640),(683,609),(671,589),(650,570)],'right_upper',6)
part('arm_right_forearm',[(730,595),(760,601),(790,595),(822,581),(837,583),(844,600),(836,626),(827,658),(819,688),(811,717),(795,719),(773,703),(750,685),(727,666),(718,647),(721,619)],'right_forearm',7)
part('right_wrist',[(817,595),(840,574),(856,553),(875,548),(895,551),(907,564),(906,579),(913,592),(905,609),(888,619),(867,620),(854,625),(838,632),(811,648)],'grip',9)
part('staff_top',[(875,0),(990,0),(1024,129),(1024,355),(944,443),(919,509),(907,554),(883,553),(887,527),(894,483),(901,430),(892,379),(883,345),(888,329),(918,318),(950,302),(981,264),(986,220),(967,193),(943,169),(916,181),(883,168),(872,135)],'grip',8)
part('staff_orb',[(882,183),(1005,185),(1003,305),(879,309)],'grip',8)
part('staff_lower',[(883,611),(902,617),(897,655),(870,810),(851,906),(830,1040),(810,1177),(789,1185),(798,1101),(816,1005),(832,909),(851,811),(866,713)],'grip',8)
# Complete imagegen staff replaces the clipped master prop. Orb-diameter registration,
# then -4 degree shaft alignment; original images are never resampled.
parts=[p for p in parts if not p['name'].startswith('staff_')]
def staff_map(x,y):
 a=math.radians(-4);dx=(x-679)*.83;dy=(y-280)*.83
 return (949+dx*math.cos(a)-dy*math.sin(a),244+dx*math.sin(a)+dy*math.cos(a))
for name,y0,y1,z in [('staff_complete_top',0,700,8),('staff_complete_lower',700,1536,-2)]:
 uv=[(0,y0),(1024,y0),(1024,y1),(0,y1)]
 part(name,[staff_map(*p) for p in uv],'grip',z,texture='staff',uv=uv)
(ROOT/'assets/rig_geometry.json').write_text(json.dumps({'canvas':[1024,1536],'origin':[575,1508],'parts':parts},indent=2))

# Native Animation resources: timeline channels are ordinary, editable property tracks.
props=['breath','body_lean','head_tilt','left_upper','left_forearm','right_upper','right_forearm','grip_tilt','cape_strength','cast_power','blast_power','hit_flash','collapse','relaxed_amount','dead_amount']
base={p:0 for p in props};base['cape_strength']=1
states={
'Idle':(3.,True,[(0,{}),(.75,{'breath':1,'left_upper':1.4,'left_forearm':-1,'right_forearm':.8,'head_tilt':-.5}), (1.5,{'breath':0}), (2.25,{'breath':-1,'left_upper':-1,'right_forearm':-.8,'head_tilt':.4}),(3,{})]),
'Cast':(2.6,False,[(0,{}),(.3,{'body_lean':-2,'left_upper':8,'left_forearm':-20,'right_upper':-3,'grip_tilt':-5,'cast_power':.2}),(.85,{'body_lean':-3,'head_tilt':-2,'left_upper':27,'left_forearm':-57,'right_upper':-9,'right_forearm':-3,'grip_tilt':-7,'cast_power':.8,'cape_strength':1.9}),(1.8,{'body_lean':-3,'head_tilt':-2,'left_upper':28,'left_forearm':-55,'right_upper':-10,'right_forearm':-4,'grip_tilt':-6,'cast_power':1.,'cape_strength':2.2}),(2.2,{'body_lean':-1,'left_upper':13,'left_forearm':-25,'right_upper':-4,'grip_tilt':-3,'cast_power':.4}), (2.6,{})]),
'Attack':(1.9,False,[(0,{}),(.28,{'body_lean':-5,'head_tilt':-3,'left_upper':19,'left_forearm':-38,'right_upper':-12,'right_forearm':-5,'grip_tilt':-13,'cast_power':.6,'cape_strength':2.} ),(.54,{'body_lean':-7,'left_upper':25,'left_forearm':-51,'right_upper':-14,'right_forearm':-9,'grip_tilt':-15,'cast_power':1.,'cape_strength':2.8}),(.72,{'body_lean':7,'head_tilt':-4,'left_upper':-47,'left_forearm':33,'right_upper':-13,'right_forearm':-5,'grip_tilt':70,'cast_power':.4,'blast_power':1.,'cape_strength':4.}),(.86,{'body_lean':5,'head_tilt':-3,'left_upper':-43,'left_forearm':30,'right_upper':-12,'right_forearm':-5,'grip_tilt':67,'blast_power':.85,'cape_strength':3.8}),(1.1,{'body_lean':2,'left_upper':-30,'left_forearm':21,'right_upper':-8,'right_forearm':-3,'grip_tilt':44,'blast_power':.25,'cape_strength':2.7}),(1.45,{'body_lean':-2,'left_upper':-8,'left_forearm':6,'right_upper':-3,'grip_tilt':10,'cape_strength':1.8}),(1.9,{})]),
'Hit':(.66,False,[(0,{}),(.08,{'body_lean':-9,'head_tilt':-6,'left_upper':13,'left_forearm':-10,'right_upper':12,'grip_tilt':-6,'hit_flash':1.,'cape_strength':2.5}),(.19,{'body_lean':-7,'head_tilt':-3,'left_upper':10,'right_upper':7,'hit_flash':.25,'cape_strength':2.}),(.4,{'body_lean':2,'head_tilt':1,'left_upper':-3,'right_upper':-2}),(.66,{})]),
'Relaxed':(4.8,False,[(0,{}),(.28,{'collapse':.2,'body_lean':5,'head_tilt':8,'left_upper':-12,'left_forearm':30,'grip_tilt':8}),(.65,{'collapse':1.,'relaxed_amount':1.}),(1.7,{'collapse':1.,'relaxed_amount':1.,'breath':.5}),(2.7,{'collapse':1.,'relaxed_amount':1.,'breath':-.5}),(3.6,{'collapse':1.,'relaxed_amount':1.}),(4.1,{'collapse':.2,'body_lean':3,'relaxed_amount':.2}),(4.8,{})]),
'Dead':(1.6,False,[(0,{}),(.3,{'collapse':.3,'body_lean':-12,'head_tilt':-10,'right_upper':9,'grip_tilt':-20}),(.85,{'collapse':1.,'dead_amount':1.}),(1.6,{'collapse':1.,'dead_amount':1.})])
}
for name,(length,loop,keys) in states.items():
 txt='[gd_resource type="Animation" format=3]\n\n[resource]\nresource_name = "%s"\nlength = %s\n'%(name,length)
 if loop:txt+='loop_mode = 1\n'
 for i,p in enumerate(props):
  ts=', '.join(str(t) for t,_ in keys);values=', '.join(str(float(base[p] | 0)) if False else str(float(v.get(p,base[p]))) for _,v in keys)
  txt+=f'tracks/{i}/type = "value"\ntracks/{i}/path = NodePath(".:{p}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = true\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array({ts}),\n"transitions": PackedFloat32Array({", ".join("1" for k in keys)}),\n"update": 0,\n"values": [{values}]\n}}\n'
 if name=='Idle': txt=txt.replace('/interp = 1','/interp = 2')
 if name=='Attack':
  i=len(props)
  txt+=f'tracks/{i}/type = "method"\ntracks/{i}/path = NodePath(".")\ntracks/{i}/enabled = true\ntracks/{i}/keys = {{\n"times": PackedFloat32Array(0.72),\n"transitions": PackedFloat32Array(1),\n"values": [{{"method": &"_emit_attack_impact", "args": []}}]\n}}\n'
 (ROOT/'animations'/f'{name}.tres').write_text(txt)
print(len(parts),'parts,',sum(len(x['vertices']) for x in parts),'vertices')
