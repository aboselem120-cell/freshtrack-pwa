# Second batch of drawn product icons (same style as gen.py), plus neutral
# per-category icons for products that match nothing.
import os, sys
OUT = sys.argv[1]
SHADOW = '<radialGradient id="sh" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.26"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
def svg(defs, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256"><defs>{SHADOW}{defs}</defs>{body}</svg>'
def stops(st):
    out = ''
    for t in st:
        o, c = t[0], t[1]; a = t[2] if len(t) > 2 else None
        out += f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>'
    return out
def lg(id, st, x2=1, y2=0): return f'<linearGradient id="{id}" x1="0" y1="0" x2="{x2}" y2="{y2}">{stops(st)}</linearGradient>'
def rg(id, st, cx=0.4, cy=0.35, r=0.75): return f'<radialGradient id="{id}" cx="{cx}" cy="{cy}" r="{r}">{stops(st)}</radialGradient>'
GLASS = lg('glass', [(0, '#FFFFFF', 0.5), (0.18, '#FFFFFF', 0.1), (0.3, '#FFFFFF', 0.55), (0.42, '#FFFFFF', 0.06), (1, '#FFFFFF', 0.4)])
def jar(fill_id, lid_id, label=''):
    # Generic glass jar: body filled with `fill_id`, metal lid `lid_id`.
    return ('<ellipse cx="128" cy="224" rx="72" ry="10" fill="url(#sh)"/>'
            f'<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#{fill_id})"/>'
            '<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2"/>'
            + label +
            f'<rect x="66" y="58" width="124" height="36" rx="8" fill="url(#{lid_id})"/>'
            '<g stroke="#000" stroke-opacity="0.15" stroke-width="2">' + ''.join(f'<line x1="{x}" y1="62" x2="{x}" y2="90"/>' for x in range(76, 186, 10)) + '</g>'
            '<path d="M70 110 L70 196" stroke="#FFFFFF" stroke-width="6" opacity="0.6" stroke-linecap="round"/>')
LABEL = lambda color='#FFFFFF', text_color='#555': (f'<rect x="76" y="130" width="104" height="52" rx="6" fill="{color}" opacity="0.95"/>'
                                                     f'<rect x="92" y="150" width="72" height="8" rx="4" fill="{text_color}" opacity="0.7"/><rect x="104" y="164" width="48" height="6" rx="3" fill="{text_color}" opacity="0.45"/>')

icons = {}

icons['honey'] = svg(
    GLASS + lg('hon', [(0, '#F7B32B'), (0.5, '#E08E0B'), (1, '#A85E00')], 1, 1) + lg('lid', [(0, '#7A4A12'), (0.4, '#B67A2C'), (1, '#5C360A')]),
    jar('hon', 'lid', '<g transform="translate(128 156)"><path d="M0 -24 L21 -12 L21 12 L0 24 L-21 12 L-21 -12 Z" fill="#FFFFFF" opacity="0.9"/><path d="M0 -14 L12 -7 L12 7 L0 14 L-12 7 L-12 -7 Z" fill="#F2A31E"/></g>')
    + '<g transform="translate(176 46) rotate(30)"><rect x="-5" y="-30" width="10" height="44" rx="5" fill="#C98C3A"/><ellipse cx="0" cy="22" rx="14" ry="12" fill="#B87A2A"/><g stroke="#8E5A18" stroke-width="2"><line x1="-13" y1="18" x2="13" y2="18"/><line x1="-13" y1="25" x2="13" y2="25"/></g></g>')

icons['oil'] = svg(
    lg('oilB', [(0, '#B78F00', 0.9), (0.25, '#F2D24A', 0.85), (0.35, '#FFF1A0', 0.9), (0.5, '#E3BE20', 0.85), (1, '#8C6A00', 0.9)]) + lg('cap', [(0, '#1E5E2E'), (0.4, '#3E9C55'), (1, '#143F1F')]),
    '<ellipse cx="128" cy="232" rx="46" ry="7" fill="url(#sh)"/>'
    '<path d="M114 36 L142 36 L142 70 C 142 86, 164 96, 164 120 L164 216 C 164 228, 92 228, 92 216 L92 120 C 92 96, 114 86, 114 70 Z" fill="url(#oilB)"/>'
    '<rect x="110" y="18" width="36" height="22" rx="4" fill="url(#cap)"/>'
    '<path d="M92 140 L164 140 L164 190 L92 190 Z" fill="#FFFFFF" opacity="0.92"/>'
    '<g transform="translate(128 164)"><path d="M-14 6 C -14 -10, 0 -20, 14 -18 C 14 -2, 2 8, -14 6 Z" fill="#3E9C55"/><circle cx="6" cy="6" r="7" fill="#6B8E23"/></g>'
    '<path d="M102 100 L102 210" stroke="#FFFFFF" stroke-width="5" opacity="0.6" stroke-linecap="round"/>')

def sack(id1, id2, emblem):
    return ('<ellipse cx="128" cy="224" rx="80" ry="11" fill="url(#sh)"/>'
            f'<path d="M64 70 L192 70 L200 212 C 200 222, 56 222, 56 212 Z" fill="url(#{id1})"/>'
            f'<path d="M64 70 L192 70 L188 54 L68 54 Z" fill="url(#{id2})"/>'
            '<g stroke="#000" stroke-opacity="0.12" stroke-width="2">' + ''.join(f'<line x1="{x}" y1="56" x2="{x}" y2="68"/>' for x in range(74, 190, 8)) + '</g>'
            + emblem +
            '<path d="M76 84 L70 204" stroke="#FFFFFF" stroke-width="6" opacity="0.5" stroke-linecap="round"/>')
icons['sugar'] = svg(
    lg('sk', [(0, '#D9DEE4'), (0.3, '#FFFFFF'), (0.5, '#F1F3F6'), (1, '#B8C0C9')]) + lg('sk2', [(0, '#C3CAD2'), (1, '#E6EAEE')], 0, 1),
    sack('sk', 'sk2', '<rect x="80" y="112" width="96" height="64" rx="8" fill="#1F6FD1"/>'
         '<g fill="#FFFFFF"><rect x="104" y="126" width="18" height="18" rx="3"/><rect x="126" y="130" width="18" height="18" rx="3" opacity="0.85"/><rect x="114" y="148" width="18" height="18" rx="3" opacity="0.9"/></g>'))
icons['flour'] = svg(
    lg('fk', [(0, '#D8C9A8'), (0.3, '#F7EEDC'), (0.5, '#EFE3CA'), (1, '#BBA67E')]) + lg('fk2', [(0, '#CDBB95'), (1, '#E9DCC0')], 0, 1),
    sack('fk', 'fk2', '<circle cx="128" cy="144" r="34" fill="#C0392B" opacity="0.9"/>'
         '<g stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"><path d="M128 168 L128 122"/>'
         + ''.join(f'<path d="M128 {y} c -10 -2 -14 -8 -14 -14 M128 {y} c 10 -2 14 -8 14 -14"/>' for y in (160, 148, 136)) + '</g>'))

icons['chips'] = svg(
    lg('bag', [(0, '#C0392B'), (0.3, '#F25C4C'), (0.42, '#FF9A8E'), (0.55, '#E74C3C'), (1, '#8E1F14')]) + lg('crimp', [(0, '#D7DBE0'), (0.5, '#FFFFFF'), (1, '#9AA3AC')], 0, 1) +
    rg('chip', [(0, '#FFE58A'), (0.7, '#F5C238'), (1, '#D9A11A')], 0.4, 0.35, 0.8),
    '<ellipse cx="128" cy="228" rx="78" ry="10" fill="url(#sh)"/>'
    '<path d="M64 44 C 58 90, 56 170, 66 214 L190 214 C 200 170, 198 90, 192 44 Z" fill="url(#bag)"/>'
    '<path d="M60 34 L196 34 L192 50 L64 50 Z" fill="url(#crimp)"/><path d="M64 210 L192 210 L196 226 L60 226 Z" fill="url(#crimp)"/>'
    '<g transform="translate(128 134)"><ellipse rx="42" ry="30" fill="url(#chip)" transform="rotate(-18)"/><ellipse cx="18" cy="14" rx="30" ry="22" fill="url(#chip)" transform="rotate(20 18 14)"/>'
    '<g fill="#D9A11A" opacity="0.5"><circle cx="-12" cy="-6" r="3"/><circle cx="6" cy="-14" r="2.4"/><circle cx="24" cy="18" r="2.6"/></g></g>'
    '<path d="M78 60 C 74 110, 74 160, 80 200" stroke="#FFFFFF" stroke-width="6" opacity="0.4" stroke-linecap="round" fill="none"/>')

def cookie(cx, cy, r):
    chips = ''.join(f'<ellipse cx="{cx+dx*r/40}" cy="{cy+dy*r/40}" rx="{r/7}" ry="{r/9}" fill="#4A2812"/>' for dx, dy in [(-14,-10),(10,-16),(16,6),(-6,10),(-20,8),(2,-2)])
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#ck)"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#B9782E" stroke-width="2"/>' + chips
icons['cookies'] = svg(
    rg('ck', [(0, '#F6C98A'), (0.7, '#D9964A'), (1, '#B06A22')], 0.4, 0.35, 0.8),
    '<ellipse cx="128" cy="210" rx="100" ry="13" fill="url(#sh)"/>' + cookie(96, 150, 50) + cookie(168, 132, 46) + cookie(130, 176, 38))

icons['sauce'] = svg(
    GLASS + lg('tom', [(0, '#E53935'), (0.5, '#C62828'), (1, '#8E1B1B')], 1, 1) + lg('lid', [(0, '#7F0E0E'), (0.4, '#D32F2F'), (1, '#5A0808')]),
    jar('tom', 'lid', '<rect x="72" y="126" width="112" height="60" rx="6" fill="#FFF8E7"/>'
        '<circle cx="128" cy="154" r="18" fill="#E53935"/><path d="M120 138 l8 6 l8 -6" stroke="#2E7D32" stroke-width="4" fill="none" stroke-linecap="round"/>'
        '<path d="M108 178 L148 178" stroke="#2E7D32" stroke-width="4" stroke-linecap="round"/>'))
icons['jam'] = svg(
    GLASS + lg('jm', [(0, '#B0123A'), (0.5, '#8E0E2E'), (1, '#5A0619')], 1, 1) + lg('lid', [(0, '#B0123A'), (0.4, '#E84A6F'), (1, '#6E0A22')]),
    jar('jm', 'lid', '<rect x="76" y="128" width="104" height="56" rx="28" fill="#FFF8E7"/>'
        '<g transform="translate(128 156)"><path d="M0 -14 C 14 -14, 18 0, 0 16 C -18 0, -14 -14, 0 -14 Z" fill="#E53950"/><path d="M-6 -16 l6 4 l6 -4" stroke="#2E7D32" stroke-width="3" fill="none"/></g>')
    + '<path d="M66 90 C 80 104, 92 94, 100 104 C 110 96, 124 108, 140 98 C 154 108, 170 96, 190 90 Z" fill="#FFFFFF"/>'
      '<g fill="#E8424F" opacity="0.9"><path d="M66 90 L 72 98 L 80 90 L 88 98 L 96 90 L 104 98 L 112 90 L 120 98 L 128 90 L 136 98 L 144 90 L 152 98 L 160 90 L 168 98 L 176 90 L 184 98 L 190 90 Z"/></g>')

icons['olives'] = svg(
    lg('bowl', [(0, '#E7E1D3'), (0.35, '#FFFFFF'), (1, '#C9C1AE')]) + rg('ol', [(0, '#B5C76A'), (0.6, '#6E8B1E'), (1, '#3F5410')], 0.35, 0.3, 0.8) + rg('olB', [(0, '#7A6A8E'), (0.6, '#3A2D4A'), (1, '#1C1426')], 0.35, 0.3, 0.8),
    '<ellipse cx="128" cy="214" rx="96" ry="13" fill="url(#sh)"/>'
    '<path d="M38 132 C 42 184, 86 204, 128 204 C 170 204, 214 184, 218 132 Z" fill="url(#bowl)"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="18" ry="13" fill="url(#{g})" transform="rotate({r} {x} {y})"/>' for x, y, r, g in
              [(84,124,-20,'ol'),(116,114,10,'olB'),(150,118,-10,'ol'),(182,126,20,'olB'),(100,136,30,'olB'),(136,134,-25,'ol'),(168,138,15,'ol')]) +
    '<ellipse cx="128" cy="132" rx="90" ry="10" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
    '<path d="M58 146 C 66 178, 96 194, 128 196" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.6" stroke-linecap="round"/>')

icons['cereal'] = svg(
    lg('box', [(0, '#F39C12'), (1, '#D35400')], 0, 1) + lg('side', [(0, '#B9500C'), (1, '#8E3C06')], 0, 1) + rg('bowl', [(0, '#FFFFFF'), (1, '#CFD8DC')]),
    '<ellipse cx="128" cy="230" rx="76" ry="9" fill="url(#sh)"/>'
    '<path d="M64 40 L172 40 L172 222 L64 222 Z" fill="url(#box)"/>'
    '<path d="M172 40 L196 28 L196 210 L172 222 Z" fill="url(#side)"/>'
    '<path d="M64 40 L88 28 L196 28 L172 40 Z" fill="#F8B04A"/>'
    '<rect x="76" y="56" width="84" height="22" rx="4" fill="#FFFFFF" opacity="0.9"/><rect x="88" y="63" width="60" height="8" rx="4" fill="#D35400"/>'
    '<path d="M78 150 C 80 186, 156 186, 158 150 Z" fill="url(#bowl)"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="9" fill="#F5C242" stroke="#C98A12" stroke-width="2"/><circle cx="{x}" cy="{y}" r="3" fill="#C98A12"/>' for x, y in [(96,140),(116,134),(136,138),(150,146),(106,150),(128,150)]) +
    '<path d="M70 50 L70 210" stroke="#FFFFFF" stroke-width="5" opacity="0.35" stroke-linecap="round"/>')

nut = lambda x, y, r: (f'<g transform="translate({x} {y}) rotate({r})"><path d="M0 -26 C 18 -26, 22 -4, 18 10 C 14 24, 0 28, -4 26 C -20 22, -22 4, -18 -10 C -14 -22, -8 -26, 0 -26 Z" fill="url(#nut)"/>'
                       '<path d="M-2 -20 C 6 -6, 6 8, 0 20" stroke="#8A5228" stroke-width="2" fill="none" opacity="0.6"/></g>')
icons['nuts'] = svg(
    rg('nut', [(0, '#E8B27A'), (0.6, '#B5743A'), (1, '#7A4518')], 0.35, 0.3, 0.85),
    '<ellipse cx="128" cy="206" rx="96" ry="13" fill="url(#sh)"/>' + ''.join(nut(x, y, r) for x, y, r in [(84,150,-30),(124,136,20),(166,152,60),(104,176,80),(150,182,-50),(196,170,10),(60,176,40)]))

date = lambda x, y, r: (f'<g transform="translate({x} {y}) rotate({r})"><ellipse rx="34" ry="17" fill="url(#dt)"/>'
                        '<path d="M-24 -4 C -10 -10, 10 -10, 24 -4" stroke="#C8864A" stroke-width="2" fill="none" opacity="0.6"/>'
                        '<ellipse cx="-8" cy="-6" rx="12" ry="4" fill="#FFFFFF" opacity="0.3"/></g>')
icons['dates'] = svg(
    rg('dt', [(0, '#A0562A'), (0.6, '#6B2E10'), (1, '#3E1505')], 0.4, 0.3, 0.8) + lg('plate', [(0, '#FFFFFF'), (1, '#D7DCE0')], 0, 1),
    '<ellipse cx="128" cy="212" rx="104" ry="14" fill="url(#sh)"/>'
    '<ellipse cx="128" cy="184" rx="100" ry="24" fill="#C3C9CF"/><ellipse cx="128" cy="180" rx="98" ry="22" fill="url(#plate)"/>'
    + ''.join(date(x, y, r) for x, y, r in [(92,160,-20),(160,156,15),(124,140,5),(110,176,10),(166,180,-15)]))

icons['icecream'] = svg(
    lg('cone', [(0, '#E0A458'), (1, '#B5762F')]) + rg('s1', [(0, '#FFF3E0'), (0.7, '#F8D7B0'), (1, '#E1B184')]) + rg('s2', [(0, '#FFC1D6'), (0.7, '#F48FB1'), (1, '#D16A8F')]) + rg('s3', [(0, '#A1887F'), (0.7, '#6D4C41'), (1, '#4E342E')]),
    '<ellipse cx="128" cy="232" rx="40" ry="7" fill="url(#sh)"/>'
    '<path d="M86 120 L128 228 L170 120 Z" fill="url(#cone)"/>'
    '<g stroke="#8E5A20" stroke-width="2" opacity="0.6"><path d="M96 130 L150 190"/><path d="M114 126 L160 168"/><path d="M160 130 L106 190"/><path d="M142 126 L96 168"/></g>'
    '<circle cx="104" cy="112" r="28" fill="url(#s1)"/><circle cx="152" cy="112" r="28" fill="url(#s2)"/><circle cx="128" cy="78" r="30" fill="url(#s3)"/>'
    '<g fill="#FFFFFF" opacity="0.5"><ellipse cx="118" cy="66" rx="9" ry="5"/><ellipse cx="94" cy="102" rx="7" ry="4"/><ellipse cx="144" cy="102" rx="7" ry="4"/></g>')

icons['sausage'] = svg(
    lg('sg', [(0, '#E57368'), (0.35, '#C0473C'), (1, '#7E2119')], 0, 1),
    '<ellipse cx="128" cy="204" rx="100" ry="12" fill="url(#sh)"/>'
    + ''.join(f'<g transform="rotate({r} 128 {y})"><rect x="40" y="{y-18}" width="176" height="36" rx="18" fill="url(#sg)"/>'
              f'<rect x="56" y="{y-12}" width="140" height="7" rx="3.5" fill="#FFFFFF" opacity="0.35"/>'
              f'<circle cx="38" cy="{y}" r="5" fill="#9E3A2E"/><circle cx="218" cy="{y}" r="5" fill="#9E3A2E"/></g>' for y, r in [(120,-8),(156,4)]))

icons['cake'] = svg(
    lg('sp', [(0, '#F5D7A1'), (1, '#E0B46E')], 0, 1) + lg('cr', [(0, '#FFFFFF'), (1, '#F3E6EE')], 0, 1) + lg('side', [(0, '#E0B46E'), (1, '#C79446')], 0, 1),
    '<ellipse cx="128" cy="212" rx="100" ry="13" fill="url(#sh)"/>'
    '<path d="M40 120 L196 92 L216 132 L60 160 Z" fill="url(#cr)"/>'
    '<path d="M60 160 L216 132 L216 184 L60 206 Z" fill="url(#sp)"/>'
    '<path d="M40 120 L60 160 L60 206 L40 168 Z" fill="url(#side)"/>'
    '<path d="M60 172 L216 146 L216 154 L60 180 Z" fill="#F7E3EE"/><path d="M60 188 L216 164 L216 170 L60 194 Z" fill="#C2185B" opacity="0.7"/>'
    '<g><circle cx="150" cy="104" r="12" fill="#E53950"/><path d="M150 92 C 152 84, 158 80, 164 80" stroke="#2E7D32" stroke-width="3" fill="none"/></g>'
    '<path d="M48 124 L192 98" stroke="#FFFFFF" stroke-width="3" opacity="0.9" stroke-linecap="round"/>')

# --- neutral icons for products that match nothing ---
icons['grocery'] = svg(
    lg('bag', [(0, '#C9A27A'), (0.3, '#E8C9A2'), (0.5, '#DDBB92'), (1, '#A87E55')]) + lg('top', [(0, '#B58E66'), (1, '#9C744C')], 0, 1),
    '<ellipse cx="128" cy="228" rx="82" ry="10" fill="url(#sh)"/>'
    '<path d="M98 92 C 98 60, 120 52, 132 74" stroke="#2E7D32" stroke-width="10" fill="none" stroke-linecap="round"/>'
    '<path d="M150 96 C 160 66, 186 66, 182 96" fill="#F4B400"/><rect x="148" y="70" width="12" height="30" rx="6" fill="#1F6FD1" transform="rotate(12 154 85)"/>'
    '<path d="M68 96 L188 96 L198 220 L58 220 Z" fill="url(#bag)"/>'
    '<path d="M68 96 L188 96 L186 108 L70 108 Z" fill="url(#top)"/>'
    '<g stroke="#9C744C" stroke-width="3" opacity="0.55"><line x1="72" y1="150" x2="194" y2="150"/><line x1="78" y1="190" x2="196" y2="190"/></g>'
    '<path d="M80 112 L74 210" stroke="#FFFFFF" stroke-width="6" opacity="0.35" stroke-linecap="round"/>')
icons['produce'] = svg(
    lg('bk', [(0, '#A0682C'), (0.4, '#D49A55'), (1, '#7C4A18')]) + rg('ap', [(0, '#FF8A80'), (0.6, '#E53935'), (1, '#9E1B1B')], 0.35, 0.3, 0.8) +
    rg('or', [(0, '#FFD180'), (0.6, '#FB8C00'), (1, '#BF5A00')], 0.35, 0.3, 0.8) + rg('lf', [(0, '#A5D6A7'), (0.6, '#43A047'), (1, '#1B5E20')], 0.35, 0.3, 0.8),
    '<ellipse cx="128" cy="222" rx="96" ry="12" fill="url(#sh)"/>'
    '<path d="M150 110 C 150 60, 196 50, 206 70 C 196 96, 176 104, 150 110 Z" fill="url(#lf)"/>'
    '<circle cx="96" cy="108" r="30" fill="url(#ap)"/><circle cx="150" cy="112" r="28" fill="url(#or)"/><circle cx="122" cy="96" r="24" fill="url(#lf)"/>'
    '<path d="M40 120 L216 120 L196 208 C 192 216, 64 216, 60 208 Z" fill="url(#bk)"/>'
    '<g stroke="#6A3E12" stroke-width="3" opacity="0.6"><path d="M50 146 L206 146"/><path d="M56 172 L200 172"/><path d="M62 196 L194 196"/>'
    + ''.join(f'<path d="M{x} 122 L{x + (x-128)*0.12} 210"/>' for x in range(70, 200, 22)) + '</g>'
    '<rect x="34" y="114" width="188" height="12" rx="6" fill="#B07A3A"/>')
icons['meat-tray'] = svg(
    lg('tray', [(0, '#3A3F44'), (1, '#1F2326')], 0, 1) + rg('mt', [(0, '#E0444A'), (0.6, '#B3202A'), (1, '#7A0F16')]) +
    lg('wrap', [(0, '#FFFFFF', 0.55), (0.3, '#FFFFFF', 0.15), (0.5, '#FFFFFF', 0.45), (1, '#FFFFFF', 0.2)], 1, 1),
    '<ellipse cx="128" cy="204" rx="108" ry="13" fill="url(#sh)"/>'
    '<path d="M30 116 L226 116 L212 186 L44 186 Z" fill="url(#tray)"/>'
    '<path d="M50 128 C 70 108, 120 106, 136 120 C 156 104, 206 110, 206 136 C 206 168, 70 174, 50 156 Z" fill="url(#mt)"/>'
    '<g stroke="#F5D9D0" stroke-width="2.5" fill="none" opacity="0.7"><path d="M70 138 c 20 -8 40 6 56 -2"/><path d="M140 140 c 16 -6 30 6 46 0"/></g>'
    '<path d="M30 116 L226 116 L212 186 L44 186 Z" fill="url(#wrap)"/>'
    '<rect x="150" y="150" width="50" height="26" rx="3" fill="#FFFFFF"/><rect x="156" y="156" width="38" height="5" rx="2" fill="#999"/><rect x="156" y="165" width="26" height="5" rx="2" fill="#C62828"/>')
icons['dairy'] = svg(
    lg('bt', [(0, '#D6DEE6'), (0.3, '#FFFFFF'), (0.45, '#F2F5F8'), (1, '#B3BFCB')]) + lg('cap', [(0, '#1555A6'), (0.4, '#3A8BE6'), (1, '#0F3F7A')]) +
    lg('ch', [(0, '#FFE58A'), (1, '#F2BE32')], 1, 1),
    '<ellipse cx="128" cy="226" rx="90" ry="11" fill="url(#sh)"/>'
    '<path d="M70 70 L106 70 L106 84 C 106 94, 118 100, 118 116 L118 214 C 118 222, 58 222, 58 214 L58 116 C 58 100, 70 94, 70 84 Z" fill="url(#bt)"/>'
    '<rect x="68" y="54" width="40" height="18" rx="4" fill="url(#cap)"/>'
    '<rect x="58" y="140" width="60" height="40" fill="#1F6FD1"/><path d="M88 148 C 80 160, 78 166, 88 172 C 98 166, 96 160, 88 148 Z" fill="#FFFFFF"/>'
    '<path d="M120 170 L200 138 L216 164 L136 196 Z" fill="url(#ch)"/>'
    '<path d="M136 196 L216 164 L216 196 L136 216 Z" fill="#E3A51B"/>'
    '<g fill="#C68A10" opacity="0.8"><ellipse cx="160" cy="198" rx="7" ry="5"/><ellipse cx="196" cy="186" rx="5" ry="4"/></g>'
    '<path d="M66 110 L66 208" stroke="#FFFFFF" stroke-width="5" opacity="0.7" stroke-linecap="round"/>')

os.makedirs(OUT, exist_ok=True)
for name, s in icons.items():
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
print(len(icons), 'svgs')
