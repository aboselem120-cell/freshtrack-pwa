# Writes the drawn product icons as SVG files (256x256, transparent).
import os, sys
OUT = sys.argv[1]
SHADOW = '''<radialGradient id="sh" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" stop-opacity="0.26"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'''
def svg(defs, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256"><defs>{SHADOW}{defs}</defs>{body}</svg>'
def lg(id, stops, x2=1, y2=0):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"{"" if a is None else f" stop-opacity=\"{a}\""}/>' for o, c, a in [(t + (None,))[:3] for t in stops])
    return f'<linearGradient id="{id}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'
def rg(id, stops, cx=0.4, cy=0.35, r=0.75):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"{"" if a is None else f" stop-opacity=\"{a}\""}/>' for o, c, a in [(t + (None,))[:3] for t in stops])
    return f'<radialGradient id="{id}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'

icons = {}

# Milk carton (gable top), 3/4 view
icons['milk'] = svg(
    lg('front', [(0, '#FFFFFF'), (1, '#E6EBF0')]) + lg('side', [(0, '#C9D2DB'), (1, '#AEB9C4')]) +
    lg('band', [(0, '#1F6FD1'), (1, '#1555A6')]) + lg('bandS', [(0, '#16529C'), (1, '#0F3F7A')]) +
    lg('roofF', [(0, '#F3F6F9'), (1, '#D8DFE6')], 0, 1) + lg('roofS', [(0, '#B7C2CD'), (1, '#9EABB8')], 0, 1),
    '<ellipse cx="128" cy="228" rx="70" ry="10" fill="url(#sh)"/>'
    '<path d="M70 92 L150 92 L150 222 L70 222 Z" fill="url(#front)"/>'
    '<path d="M150 92 L190 78 L190 206 L150 222 Z" fill="url(#side)"/>'
    '<path d="M70 92 L110 50 L150 92 Z" fill="url(#roofF)"/>'
    '<path d="M110 50 L150 36 L190 78 L150 92 Z" fill="url(#roofS)"/>'
    '<path d="M104 44 L144 30 L150 36 L110 50 Z" fill="#E9EEF2"/>'
    '<path d="M70 140 L150 140 L150 192 L70 192 Z" fill="url(#band)"/>'
    '<path d="M150 140 L190 126 L190 178 L150 192 Z" fill="url(#bandS)"/>'
    '<path d="M110 150 C 100 164, 96 172, 110 180 C 124 172, 120 164, 110 150 Z" fill="#FFFFFF"/>'
    '<circle cx="126" cy="166" r="5" fill="#FFFFFF" opacity="0.9"/><circle cx="94" cy="170" r="3.5" fill="#FFFFFF" opacity="0.8"/>'
    '<path d="M76 98 L76 214" stroke="#FFFFFF" stroke-width="4" opacity="0.8" stroke-linecap="round"/>'
)

# Two brown eggs
egg = lambda cx, cy, s, id: (f'<g transform="translate({cx} {cy}) scale({s})">'
    f'<path d="M0 -58 C 32 -58, 46 -6, 44 18 C 42 46, 22 60, 0 60 C -22 60, -42 46, -44 18 C -46 -6, -32 -58, 0 -58 Z" fill="url(#{id})"/>'
    '<ellipse cx="-16" cy="-26" rx="9" ry="16" fill="#FFFFFF" opacity="0.45" transform="rotate(20 -16 -26)"/></g>')
icons['egg'] = svg(
    rg('e1', [(0, '#F6D3AE'), (0.55, '#D9935A'), (1, '#9C5A2C')], 0.38, 0.3, 0.8) + rg('e2', [(0, '#FBE2C6'), (0.55, '#E1A46E'), (1, '#A8663A')], 0.38, 0.3, 0.8),
    '<ellipse cx="128" cy="214" rx="92" ry="12" fill="url(#sh)"/>' + egg(96, 140, 1.05, 'e1') + egg(160, 150, 1.0, 'e2'))

# Yogurt cup with foil lid and spoon
icons['yogurt'] = svg(
    lg('cup', [(0, '#D7DEE6'), (0.3, '#FFFFFF'), (0.45, '#F1F4F7'), (1, '#B9C4CF')]) +
    lg('band', [(0, '#123E8C'), (0.35, '#2E7BE0'), (1, '#0E2F6B')]) +
    rg('foil', [(0, '#FFFFFF'), (0.6, '#D3D9DF'), (1, '#9AA3AC')]) + lg('spoon', [(0, '#9AA3AC'), (0.4, '#F4F6F8'), (1, '#8A939C')]),
    '<ellipse cx="128" cy="222" rx="78" ry="11" fill="url(#sh)"/>'
    '<path d="M62 96 L76 210 C 80 222, 176 222, 180 210 L194 96 Z" fill="url(#cup)"/>'
    '<path d="M66 128 L70 160 C 100 168, 156 168, 186 160 L190 128 C 160 136, 96 136, 66 128 Z" fill="url(#band)"/>'
    '<path d="M100 146 c 8 -10 22 -10 28 0 c 6 -10 20 -10 28 0" stroke="#FFFFFF" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.9"/>'
    '<ellipse cx="128" cy="96" rx="66" ry="16" fill="#A7B0B9"/>'
    '<ellipse cx="128" cy="94" rx="64" ry="14" fill="url(#foil)"/>'
    '<path d="M150 90 C 176 70, 200 66, 214 76 C 206 92, 180 100, 150 96 Z" fill="url(#foil)" stroke="#9AA3AC" stroke-width="1"/>'
    '<ellipse cx="112" cy="94" rx="34" ry="7" fill="#FFFFFF" opacity="0.95"/>'
    '<path d="M146 92 L198 40" stroke="url(#spoon)" stroke-width="8" stroke-linecap="round"/>'
)

# Cheese wedge with holes
icons['cheese'] = svg(
    lg('top', [(0, '#FFE58A'), (1, '#F7C843')], 1, 1) + lg('front', [(0, '#F5C238'), (1, '#E2A417')], 0, 1) + lg('side', [(0, '#E9B127'), (1, '#C98C0E')], 0, 1),
    '<ellipse cx="128" cy="214" rx="96" ry="13" fill="url(#sh)"/>'
    '<path d="M36 128 L196 72 L222 112 L62 168 Z" fill="url(#top)"/>'
    '<path d="M62 168 L222 112 L222 176 L62 210 Z" fill="url(#front)"/>'
    '<path d="M36 128 L62 168 L62 210 L36 172 Z" fill="url(#side)"/>'
    '<g fill="#C68A10" opacity="0.85"><ellipse cx="100" cy="182" rx="10" ry="8"/><ellipse cx="150" cy="160" rx="13" ry="10"/><ellipse cx="196" cy="160" rx="8" ry="7"/><ellipse cx="120" cy="198" rx="5" ry="4"/><ellipse cx="48" cy="160" rx="5" ry="7"/></g>'
    '<g fill="#E9B12A"><ellipse cx="120" cy="124" rx="11" ry="5"/><ellipse cx="166" cy="104" rx="8" ry="4"/><ellipse cx="88" cy="134" rx="6" ry="3"/></g>'
    '<path d="M44 130 L194 78" stroke="#FFF6CC" stroke-width="3" opacity="0.8" stroke-linecap="round"/>'
)

# Butter block half-unwrapped on foil
icons['butter'] = svg(
    lg('bTop', [(0, '#FFF3B0'), (1, '#F8DE6E')], 1, 1) + lg('bFront', [(0, '#F6D85A'), (1, '#E6BE34')], 0, 1) + lg('bSide', [(0, '#E7C440'), (1, '#CFA521')], 0, 1) +
    lg('foil', [(0, '#E9D9A6'), (0.4, '#FFF8DC'), (1, '#BFA968')]) + lg('foilS', [(0, '#CDB878'), (1, '#A8934F')], 0, 1),
    '<ellipse cx="128" cy="210" rx="100" ry="13" fill="url(#sh)"/>'
    '<path d="M28 150 L120 120 L232 146 L140 180 Z" fill="url(#foil)"/>'
    '<path d="M28 150 L140 180 L140 196 L28 164 Z" fill="url(#foilS)"/>'
    '<path d="M140 180 L232 146 L232 160 L140 196 Z" fill="#B49D5B"/>'
    '<path d="M60 110 L136 86 L210 104 L134 130 Z" fill="url(#bTop)"/>'
    '<path d="M60 110 L134 130 L134 170 L60 150 Z" fill="url(#bFront)"/>'
    '<path d="M134 130 L210 104 L210 144 L134 170 Z" fill="url(#bSide)"/>'
    '<path d="M70 112 L134 92" stroke="#FFFBE0" stroke-width="3" stroke-linecap="round" opacity="0.9"/>'
)

# Raw chicken drumstick
icons['chicken'] = svg(
    rg('meat', [(0, '#FFD9CF'), (0.55, '#F2A99A'), (1, '#C96F62')], 0.4, 0.35, 0.8) + lg('bone', [(0, '#FFFFFF'), (1, '#E3DCCF')], 0, 1),
    '<ellipse cx="128" cy="214" rx="96" ry="12" fill="url(#sh)"/>'
    '<path d="M70 60 C 120 40, 178 70, 176 120 C 174 150, 150 160, 140 168 L 108 168 C 70 150, 30 96, 70 60 Z" fill="url(#meat)"/>'
    '<path d="M122 160 L170 196" stroke="url(#bone)" stroke-width="18" stroke-linecap="round"/>'
    '<circle cx="176" cy="192" r="12" fill="url(#bone)"/><circle cx="168" cy="206" r="11" fill="url(#bone)"/>'
    '<path d="M80 74 C 104 62, 138 70, 150 92" stroke="#FFFFFF" stroke-width="6" fill="none" opacity="0.5" stroke-linecap="round"/>'
    '<path d="M96 110 c 10 6 24 6 34 0 M88 128 c 12 6 28 6 40 0" stroke="#D98576" stroke-width="2" fill="none" opacity="0.6"/>'
)

# Steak with marbling and fat cap
icons['meat'] = svg(
    rg('beef', [(0, '#E0444A'), (0.6, '#B3202A'), (1, '#7A0F16')], 0.4, 0.35, 0.8) + lg('fat', [(0, '#FFF6EA'), (1, '#EADBC4')], 0, 1) + lg('edge', [(0, '#9E1B22'), (1, '#6A0C12')], 0, 1),
    '<ellipse cx="128" cy="210" rx="104" ry="13" fill="url(#sh)"/>'
    '<path d="M40 128 C 40 92, 90 70, 140 74 C 196 78, 226 108, 218 140 C 210 170, 160 184, 110 180 C 64 176, 40 156, 40 128 Z" fill="url(#edge)" transform="translate(0 12)"/>'
    '<path d="M40 128 C 40 92, 90 70, 140 74 C 196 78, 226 108, 218 140 C 210 170, 160 184, 110 180 C 64 176, 40 156, 40 128 Z" fill="url(#beef)"/>'
    '<path d="M140 74 C 196 78, 226 108, 218 140 C 214 154, 204 164, 190 170 C 204 150, 206 112, 140 86 Z" fill="url(#fat)"/>'
    '<g stroke="#F5D9D0" stroke-width="2.5" fill="none" opacity="0.75" stroke-linecap="round"><path d="M70 120 c 20 -10 40 6 60 -4"/><path d="M84 146 c 18 -6 30 8 52 0 s 20 -12 30 -2"/><path d="M100 98 c 10 6 22 2 30 10"/><path d="M60 140 c 8 6 14 12 26 12"/></g>'
    '<ellipse cx="96" cy="100" rx="26" ry="8" fill="#FFFFFF" opacity="0.18" transform="rotate(-15 96 100)"/>'
)

# Salmon fillet
icons['fish'] = svg(
    lg('sal', [(0, '#FFB089'), (0.5, '#FF8A5C'), (1, '#E5643A')], 1, 1) + lg('skin', [(0, '#B9C3CC'), (1, '#7E8A96')], 0, 1),
    '<ellipse cx="128" cy="206" rx="104" ry="13" fill="url(#sh)"/>'
    '<path d="M30 140 C 60 96, 160 82, 228 104 L 222 132 C 160 150, 70 170, 34 160 Z" fill="url(#skin)" transform="translate(0 10)"/>'
    '<path d="M30 140 C 60 96, 160 82, 228 104 L 222 132 C 160 150, 70 170, 34 160 Z" fill="url(#sal)"/>'
    '<g stroke="#FFE5D6" stroke-width="4" fill="none" opacity="0.85" stroke-linecap="round">'
    '<path d="M70 118 c 6 12 6 24 0 36"/><path d="M100 108 c 7 14 7 30 0 42"/><path d="M132 102 c 7 14 7 30 0 42"/><path d="M164 100 c 7 12 7 26 0 36"/><path d="M194 102 c 5 10 5 20 0 28"/></g>'
    '<path d="M50 126 C 90 100, 160 92, 214 106" stroke="#FFFFFF" stroke-width="5" fill="none" opacity="0.4" stroke-linecap="round"/>'
)

# Bread loaf
icons['bread'] = svg(
    rg('crust', [(0, '#F2B866'), (0.6, '#C9802E'), (1, '#8E5116')], 0.4, 0.3, 0.8) + lg('side', [(0, '#B46E25'), (1, '#7E4712')], 0, 1),
    '<ellipse cx="128" cy="212" rx="104" ry="13" fill="url(#sh)"/>'
    '<path d="M34 150 L34 176 C 34 192, 222 192, 222 176 L222 150 Z" fill="url(#side)"/>'
    '<path d="M34 150 C 30 96, 70 70, 128 70 C 186 70, 226 96, 222 150 C 222 166, 34 166, 34 150 Z" fill="url(#crust)"/>'
    '<g stroke="#F7D49A" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.9"><path d="M78 96 c 10 14 10 30 4 44"/><path d="M118 86 c 10 16 10 34 4 50"/><path d="M158 88 c 10 16 10 32 4 48"/></g>'
    '<path d="M60 108 C 76 86, 110 78, 140 78" stroke="#FFF0D0" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/>'
)

# Croissant
seg = lambda d, fill: f'<path d="{d}" fill="{fill}" stroke="#A9601A" stroke-width="1.2"/>'
icons['croissant'] = svg(
    rg('c1', [(0, '#F9CB7E'), (0.6, '#D98C35'), (1, '#A75A16')], 0.45, 0.3, 0.8),
    '<ellipse cx="128" cy="200" rx="104" ry="13" fill="url(#sh)"/>' +
    seg('M28 168 C 30 146, 50 132, 70 136 C 76 152, 64 172, 40 178 Z', 'url(#c1)') +
    seg('M228 168 C 226 146, 206 132, 186 136 C 180 152, 192 172, 216 178 Z', 'url(#c1)') +
    seg('M62 140 C 70 112, 96 100, 110 104 C 116 130, 104 160, 72 168 Z', 'url(#c1)') +
    seg('M194 140 C 186 112, 160 100, 146 104 C 140 130, 152 160, 184 168 Z', 'url(#c1)') +
    seg('M104 106 C 110 80, 146 80, 152 106 C 156 140, 140 170, 128 172 C 116 170, 100 140, 104 106 Z', 'url(#c1)') +
    '<g fill="#FFFFFF" opacity="0.35"><ellipse cx="122" cy="102" rx="10" ry="5"/><ellipse cx="86" cy="122" rx="7" ry="4" transform="rotate(-30 86 122)"/><ellipse cx="170" cy="122" rx="7" ry="4" transform="rotate(30 170 122)"/></g>'
)

# Bowl of rice
rice = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="3.6" fill="#FFFFFF" stroke="#DCDCD2" stroke-width="0.8" transform="rotate({r} {x} {y})"/>'
               for x, y, r in [(92,104,20),(108,94,-30),(124,88,10),(140,92,40),(156,100,-20),(170,110,30),(84,118,-10),(100,114,50),(116,106,-40),(132,102,15),(148,110,-60),(164,120,10),(100,128,30),(118,122,-20),(136,118,45),(152,126,-15),(176,124,20),(90,132,-35),(128,132,5),(144,134,30)])
icons['rice'] = svg(
    lg('bowl', [(0, '#1C4E8C'), (0.35, '#3E86D6'), (0.5, '#2B6BB6'), (1, '#123766')]) + rg('mound', [(0, '#FFFFFF'), (0.7, '#F1F0E8'), (1, '#D9D7CC')], 0.4, 0.3, 0.8),
    '<ellipse cx="128" cy="214" rx="90" ry="12" fill="url(#sh)"/>'
    '<path d="M46 132 C 50 186, 90 204, 128 204 C 166 204, 206 186, 210 132 Z" fill="url(#bowl)"/>'
    '<path d="M60 140 C 64 176, 96 194, 128 194" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.35" stroke-linecap="round"/>'
    '<path d="M60 134 C 62 96, 96 80, 128 80 C 160 80, 194 96, 196 134 Z" fill="url(#mound)"/>' + rice +
    '<ellipse cx="128" cy="132" rx="82" ry="10" fill="#0F2E57" opacity="0.6"/><ellipse cx="128" cy="131" rx="82" ry="8" fill="none" stroke="#5B9BE0" stroke-width="2"/>'
)

# Dry spaghetti bundle with paper band
sticks = ''.join(f'<line x1="{56+i*8}" y1="{196-(i%3)*3}" x2="{146+i*8}" y2="{44+(i%2)*4}" stroke="{c}" stroke-width="8" stroke-linecap="round"/>'
                 for i, c in enumerate(['#E8B94A', '#F3CB5F', '#DDAA3A', '#F6D470', '#E9BC4C', '#F0C556', '#D9A535', '#F4CF66', '#E5B444', '#F2C85A']))
icons['pasta'] = svg(
    lg('band', [(0, '#1D5E3A'), (0.4, '#2F8A57'), (1, '#174A2E')], 1, 0),
    '<ellipse cx="128" cy="206" rx="70" ry="10" fill="url(#sh)"/>' + sticks +
    '<path d="M86 130 L170 112 L178 142 L94 160 Z" fill="url(#band)"/>'
    '<path d="M100 140 L160 127" stroke="#FFFFFF" stroke-width="3" opacity="0.8" stroke-linecap="round"/>'
)

# Water bottle
icons['water'] = svg(
    lg('pet', [(0, '#7FB8E8', 0.85), (0.2, '#D8EEFF', 0.6), (0.32, '#FFFFFF', 0.85), (0.45, '#BFE0FA', 0.45), (0.85, '#8CC3EE', 0.6), (1, '#4F93D0', 0.85)]) +
    lg('cap', [(0, '#0F4E9C'), (0.35, '#3A8BE6'), (1, '#0B3A75')]) + lg('label', [(0, '#E8F3FD'), (0.35, '#FFFFFF'), (1, '#C7DCEF')]),
    '<ellipse cx="128" cy="230" rx="44" ry="7" fill="url(#sh)"/>'
    '<path d="M110 50 L146 50 L146 62 C 146 74, 166 84, 166 106 L166 214 C 166 224, 90 224, 90 214 L90 106 C 90 84, 110 74, 110 62 Z" fill="url(#pet)"/>'
    '<rect x="108" y="26" width="40" height="24" rx="4" fill="url(#cap)"/>'
    '<g stroke="#0B3A75" stroke-width="1.5" opacity="0.6"><line x1="114" y1="30" x2="114" y2="46"/><line x1="122" y1="30" x2="122" y2="46"/><line x1="130" y1="30" x2="130" y2="46"/><line x1="138" y1="30" x2="138" y2="46"/></g>'
    '<path d="M90 132 L166 132 L166 176 L90 176 Z" fill="url(#label)"/>'
    '<path d="M104 160 c 10 -12 20 -12 26 -2 c 6 10 16 10 24 -2" stroke="#2E7BE0" stroke-width="4" fill="none" stroke-linecap="round"/>'
    '<path d="M100 98 L100 210" stroke="#FFFFFF" stroke-width="5" opacity="0.7" stroke-linecap="round"/>'
    '<g fill="none" stroke="#7FB8E8" stroke-width="1.5" opacity="0.7"><path d="M90 196 C 110 200, 146 200, 166 196"/><path d="M90 116 C 110 120, 146 120, 166 116"/></g>'
)

# Glass of orange juice with slice and straw
icons['juice'] = svg(
    lg('oj', [(0, '#FFB52E'), (0.5, '#FF9A0A'), (1, '#E07000')], 1, 1) + rg('ojTop', [(0, '#FFD27A'), (1, '#FFA21C')]) +
    lg('glass', [(0, '#FFFFFF', 0.55), (0.18, '#FFFFFF', 0.12), (0.3, '#FFFFFF', 0.6), (0.4, '#FFFFFF', 0.08), (1, '#FFFFFF', 0.45)]) +
    rg('slice', [(0, '#FFF2C4'), (0.75, '#FFC53D'), (1, '#F08A00')], 0.5, 0.5, 0.5),
    '<ellipse cx="128" cy="222" rx="66" ry="10" fill="url(#sh)"/>'
    '<path d="M80 92 L90 206 C 92 216, 164 216, 166 206 L176 92 Z" fill="url(#oj)"/>'
    '<ellipse cx="128" cy="92" rx="48" ry="10" fill="url(#ojTop)"/>'
    '<path d="M74 66 L88 210 C 90 222, 166 222, 168 210 L182 66 Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="2"/>'
    '<ellipse cx="128" cy="66" rx="54" ry="11" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.9"/>'
    '<path d="M86 84 L96 196" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.7"/>'
    '<path d="M150 96 L178 22" stroke="#2F8A57" stroke-width="8" stroke-linecap="round"/><path d="M150 96 L178 22" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.5"/>'
    '<g transform="translate(78 70)"><circle r="26" fill="url(#slice)"/><circle r="20" fill="none" stroke="#FFF5D6" stroke-width="2"/>'
    + ''.join(f'<line x1="0" y1="0" x2="{x}" y2="{y}" stroke="#FFF5D6" stroke-width="1.6"/>' for x, y in [(0,-19),(16,-10),(16,10),(0,19),(-16,10),(-16,-10)]) +
    '</g>'
)

# Coffee cup with crema on saucer
icons['coffee'] = svg(
    lg('cup', [(0, '#D5DCE2'), (0.3, '#FFFFFF'), (0.45, '#F4F6F8'), (1, '#AEB8C2')]) + rg('crema', [(0, '#E9C08A'), (0.5, '#B07438'), (1, '#5A3214')], 0.45, 0.45, 0.6) +
    lg('saucer', [(0, '#FFFFFF'), (1, '#D3D9DE')], 0, 1),
    '<ellipse cx="128" cy="214" rx="100" ry="15" fill="url(#sh)"/>'
    '<ellipse cx="128" cy="198" rx="96" ry="20" fill="#C1C8CE"/><ellipse cx="128" cy="195" rx="94" ry="18" fill="url(#saucer)"/>'
    '<path d="M180 110 c 36 -4 40 48 2 52" fill="none" stroke="#E6EBEF" stroke-width="12" stroke-linecap="round"/>'
    '<path d="M180 110 c 36 -4 40 48 2 52" fill="none" stroke="#B8C2CB" stroke-width="2"/>'
    '<path d="M62 98 C 64 160, 88 192, 128 192 C 168 192, 192 160, 194 98 Z" fill="url(#cup)"/>'
    '<ellipse cx="128" cy="98" rx="66" ry="16" fill="#E7ECF0"/>'
    '<ellipse cx="128" cy="100" rx="58" ry="12" fill="url(#crema)"/>'
    '<path d="M112 98 c 8 -6 24 -6 32 0 c -8 6 -24 6 -32 0 z" fill="#F3D8AE" opacity="0.8"/>'
    '<path d="M76 112 C 80 150, 96 174, 114 182" stroke="#FFFFFF" stroke-width="6" fill="none" opacity="0.8" stroke-linecap="round"/>'
)

# Snack / protein bar in a wrapper, one end open
icons['bar'] = svg(
    lg('wrap', [(0, '#5B2A86'), (0.3, '#8A4CC4'), (0.45, '#B585E6'), (0.6, '#7A3DB5'), (1, '#3E1A60')], 0, 1) +
    lg('choc', [(0, '#7A4A2A'), (1, '#4A2812')], 0, 1) + lg('crimp', [(0, '#C9CFD6'), (0.5, '#FFFFFF'), (1, '#9AA3AC')], 0, 1),
    '<ellipse cx="128" cy="196" rx="108" ry="12" fill="url(#sh)"/>'
    '<g transform="rotate(-14 128 128)">'
    '<rect x="34" y="104" width="150" height="54" rx="6" fill="url(#wrap)"/>'
    '<path d="M34 104 L22 108 L28 116 L20 124 L28 132 L20 140 L28 148 L22 156 L34 158 Z" fill="url(#crimp)"/>'
    '<rect x="184" y="108" width="52" height="46" rx="5" fill="url(#choc)"/>'
    '<g stroke="#8F5A35" stroke-width="2" opacity="0.8"><line x1="200" y1="110" x2="200" y2="152"/><line x1="218" y1="110" x2="218" y2="152"/></g>'
    '<path d="M184 104 L196 100 L190 112 L198 122 L188 130 L196 142 L186 150 L194 160 L184 158 Z" fill="url(#crimp)"/>'
    '<rect x="64" y="118" width="86" height="26" rx="13" fill="#FFFFFF" opacity="0.92"/>'
    '<rect x="76" y="127" width="62" height="8" rx="4" fill="#7A3DB5"/>'
    '<rect x="40" y="110" width="138" height="6" rx="3" fill="#FFFFFF" opacity="0.35"/>'
    '</g>'
)

os.makedirs(OUT, exist_ok=True)
for name, s in icons.items():
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
print(len(icons), 'svgs')
