"""Continuous paths with controlled follow-through for the existing pose rig.

The drawing keys are waypoints, not separate ease-in/ease-out moves. Bounded
vector Hermite tangents retain body velocity around curved passing poses;
monotone angular and support channels avoid overshooting their extrema.
True holds (repeated poses) and action endpoints have zero tangents.
"""
import bisect, math


def delay_for(bone):
    if bone in ('head', 'neck') or bone.startswith('head_cage'):
        return -.035
    if bone.startswith('cape_'):
        return .060
    if bone in ('chest', 'upper_r', 'upper_l'):
        return -.015
    if bone in ('fore_r', 'fore_l'):
        return .012
    if bone in ('hand_r', 'staff') or bone.startswith('grip_cage'):
        return .025
    if bone == 'hand_l' or bone.startswith('left_grip_cage'):
        return .040
    if bone.startswith(('arm_r_edge_', 'arm_l_edge_')):
        joint = int(bone.rsplit('_', 1)[1]) // 2
        return [-.015, .012, .025 if '_r_' in bone else .040][joint]
    return 0


def tangents(times, values):
    gaps = [b-a for a, b in zip(times, times[1:])]
    secants = [(b-a)/h for a, b, h in zip(values, values[1:], gaps)]
    slopes = [0.0]*len(values)
    for i in range(1, len(values)-1):
        before, after = secants[i-1:i+1]
        if before*after <= 0:
            continue
        left, right = gaps[i-1:i+1]
        w1, w2 = 2*right+left, right+2*left
        slopes[i] = (w1+w2)/(w1/before+w2/after)
    return slopes


class Motion:
    def __init__(self, schedule, world):
        self.curves = {}
        duration = schedule[-1][0]
        for bone in world[schedule[0][1]]:
            delay = delay_for(bone)*min(1, duration/1.3)
            times = []
            for i, (time, pose) in enumerate(schedule):
                # No phase offset at a support/hold boundary or clip endpoint.
                if i in (0, len(schedule)-1) or pose in (schedule[i-1][1], schedule[min(i+1, len(schedule)-1)][1]):
                    times.append(time)
                else:
                    room = min(time-schedule[i-1][0], schedule[i+1][0]-time)
                    times.append(time+max(-room*.2, min(room*.2, delay)))
            values = [list(world[pose][bone]) for _, pose in schedule]
            for i in range(1, len(values)):
                values[i][2] = values[i-1][2]+(values[i][2]-values[i-1][2]+180)%360-180
            components = list(zip(*values))
            slopes = [tangents(times, v) for v in components]
            # A 2D path can pass smoothly around an extremum in one component.
            # Independent monotone X/Y slopes would stop at such corners.
            if bone in ('pelvis', 'chest', 'head', 'neck', 'upper_r', 'upper_l', 'fore_r', 'fore_l', 'hand_r', 'hand_l', 'staff', 'cape_l', 'cape_r'):
                for i in range(1, len(values)-1):
                    h0, h1 = times[i]-times[i-1], times[i+1]-times[i]
                    a = [(values[i][k]-values[i-1][k])/h0 for k in (0, 1)]
                    b = [(values[i+1][k]-values[i][k])/h1 for k in (0, 1)]
                    if min(math.hypot(*a), math.hypot(*b)) < 1e-6:
                        continue
                    v = [(a[k]*h1+b[k]*h0)/(h0+h1) for k in (0, 1)]
                    limit = 1.5*min(math.hypot(*a), math.hypot(*b))
                    factor = min(1, limit/max(1e-8, math.hypot(*v)))
                    slopes[0][i], slopes[1][i] = [x*factor for x in v]
            self.curves[bone] = (times, components, slopes)

    def at(self, t):
        result = {}
        for bone, (times, values, slopes) in self.curves.items():
            i = max(0, min(len(times)-2, bisect.bisect_right(times, t)-1))
            h = times[i+1]-times[i]
            u = max(0, min(1, (t-times[i])/h))
            h00, h10 = 2*u**3-3*u**2+1, u**3-2*u**2+u
            h01, h11 = -2*u**3+3*u**2, u**3-u**2
            result[bone] = tuple(h00*v[i]+h10*h*m[i]+h01*v[i+1]+h11*h*m[i+1] for v, m in zip(values, slopes))
        # The supporting cage follows the sampled anatomical joints as a unit.
        # Independently curving each edge would shear/fold the sleeve mesh.
        def offset(center, xy, angle):
            r = math.radians(angle)
            return (center[0]+xy[0]*math.cos(r)-xy[1]*math.sin(r), center[1]+xy[0]*math.sin(r)+xy[1]*math.cos(r), 0)
        for side in 'rl':
            for limb, names, widths in [('arm', ['upper_', 'fore_', 'hand_'], [12, 10, 8]), ('leg', ['thigh_', 'shin_', 'foot_'], [12, 11, 13])]:
                points = [result[n+side] for n in names]
                for j, (center, width) in enumerate(zip(points, widths)):
                    other = points[j+1] if j < 2 else points[j-1]
                    angle = math.degrees(math.atan2(other[1]-center[1], other[0]-center[0]))+(90 if j < 2 else -90)
                    for z, sign in enumerate((-1, 1)):
                        result[f'{limb}_{side}_edge_{j*2+z}'] = offset(center, (width*sign, 0), angle)
            hand = result['hand_'+side]
            for i, xy in enumerate([(-10, -10), (10, -10), (-10, 10), (10, 10)]):
                prefix = 'grip_cage_' if side == 'r' else 'left_grip_cage_'
                result[prefix+str(i)] = offset(hand, xy, hand[2]+(90 if side == 'l' else 0))
        return result
