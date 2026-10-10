"""Render a source-grounded damage-system comparison. No game files are changed.

Normal use: python design/docs/build_damage_study.py
Refresh local evidence: add --refresh-evidence (requires the recorded source paths).
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / '原版五职业与Karen伤害体系分析.html'
SNAPSHOT = HERE / '伤害体系源码证据.json'
BASE = Path('C:/Users/17575/AppData/Local/Temp/megumin-damage-v01071-5f8e954d')
KAREN = Path('D:/Godot/Proj/STS2_ShoujoKagekiAijoKaren')
from damage_port_focus import evidence_names, render_report


def key(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).upper()


def build_evidence():
    loc = json.loads((BASE/'localization-extract/localization/zhs/cards.json').read_text(encoding='utf-8-sig'))
    kloc = json.loads((KAREN/'ShoujoKagekiAijoKaren/localization/zhs/cards.json').read_text(encoding='utf-8-sig'))
    index = {}
    for root in [BASE, KAREN/'src/Core']:
        for p in root.rglob('*.cs'):
            index.setdefault(p.stem, []).append(p)
    prior_names = set()
    if SNAPSHOT.exists():
        prior_names.update(json.loads(SNAPSHOT.read_text(encoding='utf-8'))['evidence'])
    names = sorted(prior_names | evidence_names())
    evidence = {}
    for name in names:
        candidates = index.get(name, [])
        if not candidates:
            raise ValueError(f'Missing source: {name}')
        p = next((p for p in candidates if '/MegaCrit.Sts2.Core.' in p.as_posix()), candidates[0])
        raw = p.read_text(encoding='utf-8-sig')
        lines = raw.splitlines()
        # Preserve modest line-numbered excerpts around mechanics, not VFX boilerplate.
        hits = [i for i, line in enumerate(lines) if re.search(
            r'CanonicalStarCost|CanonicalVars|new \w*(?:Var|Var<)|WithMultiplier|History\.|AfterCard|AfterSide|AfterPlayer|'
            r'AfterAuto|OnGlobalMove|OnTurnEndInPromise|ModifyCardPlayCount|GetResultPileTypeForCardPlay|'
            r'GetDisposedShine|UpdateShineCardDisposed|IsOwnerDoomed|DoomKill|Damage\(|DamageCmd|'
            r'BuffFrom|UpgradeValueBy|IsPlayable|Condition\(|RestoreShine|skip < count|shineCards.Skip|'
            r'ValueProp.Un|AfterCurrentHpChanged|TriggerCount|RefillWithContinueAsync|InfiniteReinforcement|'
            r'OnCardRemovedFromPromise|IsInMode|StarsSpent|AfterStarsGained|ExtraDamageFrom|CardKeyword.Exhaust', line)]
        selected = sorted({j for i in hits for j in range(max(0,i-1),min(len(lines),i+4))})[:90]
        if name == 'CardModel':
            start = next(i for i, line in enumerate(lines) if 'protected virtual PileType GetResultPileTypeForCardPlay' in line)
            selected = list(range(start, min(len(lines), start+17)))
        excerpts = '\n'.join(f'{i+1:>4}  {lines[i]}' for i in selected)
        localization = kloc if name.startswith('Karen') else loc
        evidence[name] = dict(path=p.as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                              title=localization.get(key(name)+'.title', name),
                              description=localization.get(key(name)+'.description', ''),
                              excerpts=excerpts)
    payload = dict(date='2026-10-09', original_version='v0.107.1', original_commit='59260271',
                   original_build_date='2026-06-18', karen_head='e5a9115',
                   scope='本地 stable 程序集及匹配中文文本；Karen 当前工作区源码（不假设等于 HEAD）。', evidence=evidence)
    assembly = KAREN/'artifacts/dev-game/stable/game/data_sts2_windows_x86_64/sts2.dll'
    payload['original_assembly'] = dict(path=assembly.as_posix(), sha256=hashlib.sha256(assembly.read_bytes()).hexdigest())
    keyword_path = BASE/'localization-extract/localization/zhs/card_keywords.json'
    keyword_text = json.loads(keyword_path.read_text(encoding='utf-8-sig'))
    payload['keyword_evidence'] = {k: v for k, v in keyword_text.items() if k.split('.')[0] in {'SLY','EXHAUST','ETHEREAL'}}
    SNAPSHOT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return payload



if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--refresh-evidence', action='store_true')
    args = ap.parse_args()
    data = build_evidence() if args.refresh_evidence else json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    render_report(data, OUT)
