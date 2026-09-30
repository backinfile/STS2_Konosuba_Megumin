shader_type canvas_item;
// Geometry-authored cutout mask, evaluated in source-pixel coordinates.
// PNGs are preserved. The gripping hand remains in front of the shared staff.
uniform vec2 keep_head[32];uniform int keep_head_count=0;
uniform vec2 keep_leg[32];uniform int keep_leg_count=0;
bool inside_keep_head(vec2 p){bool hit=false;for(int i=0;i<32;i++){if(i>=keep_head_count)break;int j=i==0?keep_head_count-1:i-1;vec2 a=keep_head[i];vec2 b=keep_head[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;}
bool inside_keep_leg(vec2 p){bool hit=false;for(int i=0;i<32;i++){if(i>=keep_leg_count)break;int j=i==0?keep_leg_count-1:i-1;vec2 a=keep_leg[i];vec2 b=keep_leg[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;}
uniform vec2 source_size;
uniform bool front_only=false;
uniform vec2 front_polygon[64];
uniform int front_count=0;
bool inside_front(vec2 p){bool hit=false;for(int i=0;i<64;i++){if(i>=front_count)break;int j=i==0?front_count-1:i-1;vec2 a=front_polygon[i];vec2 b=front_polygon[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;}
uniform vec2 prop_polygon[64];
uniform int prop_count=0;
uniform vec2 hand_polygon[32];
uniform int hand_count=0;
uniform vec2 leg_left[64];
uniform int leg_left_count=0;
uniform vec2 leg_right[64];
uniform int leg_right_count=0;
uniform vec2 lower_keep[32];
uniform int lower_keep_count=0;
uniform float lower_clip_y=99999.0;
bool inside_left(vec2 p) {
 bool hit=false;
 for(int i=0;i<64;i++){if(i>=leg_left_count)break;int j=i==0?leg_left_count-1:i-1;vec2 a=leg_left[i];vec2 b=leg_left[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;
}
bool inside_right(vec2 p) {
 bool hit=false;
 for(int i=0;i<64;i++){if(i>=leg_right_count)break;int j=i==0?leg_right_count-1:i-1;vec2 a=leg_right[i];vec2 b=leg_right[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;
}
bool inside_lower_keep(vec2 p) {
 bool hit=false;
 for(int i=0;i<32;i++){if(i>=lower_keep_count)break;int j=i==0?lower_keep_count-1:i-1;vec2 a=lower_keep[i];vec2 b=lower_keep[j];if((a.y>p.y)!=(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;
}
bool inside_prop(vec2 p) {
 bool hit=false;
 for(int i=0;i<64;i++) {
  if(i>=prop_count) break;
  int j=(i==0 ? prop_count-1 : i-1);
  vec2 a=prop_polygon[i];vec2 b=prop_polygon[j];
  if((a.y>p.y)!=(b.y>p.y) && p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x) hit=!hit;
 }
 return hit;
}
bool inside_hand(vec2 p) {
 bool hit=false;
 for(int i=0;i<32;i++) {
  if(i>=hand_count) break;
  int j=(i==0 ? hand_count-1 : i-1);
  vec2 a=hand_polygon[i];vec2 b=hand_polygon[j];
  if((a.y>p.y)!=(b.y>p.y) && p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x) hit=!hit;
 }
 return hit;
}
void fragment(){
 vec2 p=UV*source_size;
 if(front_only && !inside_front(p)) COLOR.a=0.0;
 if(inside_prop(p) && !inside_hand(p) && !inside_keep_head(p) && !inside_keep_leg(p)) COLOR.a=0.0;
 if((p.y>lower_clip_y || inside_left(p) || inside_right(p)) && !inside_lower_keep(p)) COLOR.a=0.0;
}
