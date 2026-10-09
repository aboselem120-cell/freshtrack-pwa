# Third batch of drawn product icons (same style as gen.py / gen2.py).
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
    return ('<ellipse cx="128" cy="224" rx="72" ry="10" fill="url(#sh)"/>'
            f'<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#{fill_id})"/>'
            '<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2"/>'
            + label +
            f'<rect x="66" y="58" width="124" height="36" rx="8" fill="url(#{lid_id})"/>'
            '<g stroke="#000" stroke-opacity="0.15" stroke-width="2">' + ''.join(f'<line x1="{x}" y1="62" x2="{x}" y2="90"/>' for x in range(76, 186, 10)) + '</g>'
            '<path d="M70 110 L70 196" stroke="#FFFFFF" stroke-width="6" opacity="0.6" stroke-linecap="round"/>')
icons = {}

# Chocolate tablet, partly unwrapped
icons['chocolate'] = svg(
    lg('ch', [(0, '#7B4A2A'), (1, '#4A2812')], 1, 1) + lg('foil', [(0, '#C9CFD6'), (0.4, '#FFFFFF'), (1, '#9AA3AC')], 1, 1) + lg('wrap', [(0, '#8E1B2C'), (0.4, '#C62842'), (1, '#6A1020')], 1, 1),
    '<ellipse cx="128" cy="212" rx="100" ry="12" fill="url(#sh)"/>'
    '<g transform="rotate(-12 128 128)">'
    '<rect x="40" y="70" width="176" height="110" rx="6" fill="url(#ch)"/>'
    + ''.join(f'<rect x="{46+c*42}" y="{76+r*34}" width="36" height="28" rx="3" fill="#5E3519" stroke="#8A5530" stroke-width="2"/>' for c in range(4) for r in range(3)) +
    '<path d="M124 64 L222 64 L222 186 L124 186 L136 160 L124 136 L138 112 L124 88 Z" fill="url(#foil)"/>'
    '<path d="M150 64 L222 64 L222 186 L150 186 Z" fill="url(#wrap)"/>'
    '<rect x="162" y="110" width="48" height="30" rx="15" fill="#FFFFFF" opacity="0.9"/><rect x="172" y="121" width="28" height="8" rx="4" fill="#C62842"/>'
    '</g>')

# Wrapped candies
candy = lambda x, y, r, id: (f'<g transform="translate({x} {y}) rotate({r})"><path d="M-46 -16 L-26 0 L-46 16 Z" fill="url(#{id})"/><path d="M46 -16 L26 0 L46 16 Z" fill="url(#{id})"/>'
                             f'<ellipse rx="30" ry="22" fill="url(#{id})"/><ellipse cx="-8" cy="-8" rx="10" ry="5" fill="#FFFFFF" opacity="0.5"/></g>')
icons['candy'] = svg(
    rg('c1', [(0, '#FF9AB8'), (0.6, '#E91E63'), (1, '#9C1040')]) + rg('c2', [(0, '#9AD8FF'), (0.6, '#1E88E5'), (1, '#0D47A1')]) + rg('c3', [(0, '#FFE58A'), (0.6, '#FBC02D'), (1, '#C68A00')]),
    '<ellipse cx="128" cy="206" rx="100" ry="12" fill="url(#sh)"/>' + candy(92, 120, -20, 'c1') + candy(164, 112, 25, 'c2') + candy(128, 170, 5, 'c3'))

# Spice jar with shaker top
icons['spices'] = svg(
    GLASS + lg('sp', [(0, '#C0391B'), (0.5, '#E2571E'), (1, '#8E2A10')], 1, 1) + lg('cap', [(0, '#3A3F44'), (0.4, '#6B737B'), (1, '#1F2326')]),
    '<ellipse cx="128" cy="226" rx="56" ry="9" fill="url(#sh)"/>'
    '<rect x="80" y="76" width="96" height="140" rx="12" fill="url(#sp)"/>'
    '<rect x="80" y="76" width="96" height="140" rx="12" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2"/>'
    '<rect x="88" y="124" width="80" height="52" rx="6" fill="#FFF8E7"/>'
    '<g transform="translate(128 150)"><path d="M-14 8 C -16 -8, -4 -18, 10 -16 C 14 0, 4 12, -14 8 Z" fill="#2E7D32"/><path d="M-12 8 L 8 -12" stroke="#1B5E20" stroke-width="2"/></g>'
    '<rect x="76" y="40" width="104" height="40" rx="8" fill="url(#cap)"/>'
    '<g fill="#1F2326">' + ''.join(f'<circle cx="{x}" cy="52" r="3"/>' for x in range(98, 164, 12)) + '</g>'
    '<path d="M90 90 L90 204" stroke="#FFFFFF" stroke-width="5" opacity="0.6" stroke-linecap="round"/>')

# Salt shaker
icons['salt'] = svg(
    GLASS + lg('cap', [(0, '#8A939C'), (0.35, '#F4F6F8'), (1, '#6E777F')]) + lg('salt', [(0, '#F4F6F8'), (1, '#DDE2E7')], 0, 1),
    '<ellipse cx="128" cy="226" rx="56" ry="9" fill="url(#sh)"/>'
    '<path d="M86 96 L170 96 L178 210 C 178 220, 78 220, 78 210 Z" fill="url(#salt)"/>'
    '<path d="M86 96 L170 96 L178 210 C 178 220, 78 220, 78 210 Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="2"/>'
    '<g fill="#FFFFFF">' + ''.join(f'<rect x="{x}" y="{y}" width="5" height="5" transform="rotate(30 {x} {y})"/>' for x, y in [(100,150),(120,170),(140,140),(156,180),(110,196),(146,200),(130,120)]) + '</g>'
    '<path d="M84 98 C 84 54, 172 54, 172 98 Z" fill="url(#cap)"/>'
    '<g fill="#5B636B">' + ''.join(f'<circle cx="{x}" cy="{y}" r="3"/>' for x, y in [(116,72),(128,68),(140,72),(122,82),(134,82)]) + '</g>'
    '<path d="M94 110 L90 204" stroke="#FFFFFF" stroke-width="5" opacity="0.7" stroke-linecap="round"/>')

# Ketchup squeeze bottle
icons['ketchup'] = svg(
    lg('kb', [(0, '#8E1B1B'), (0.3, '#E53935'), (0.42, '#FF8A80'), (0.55, '#D32F2F'), (1, '#6A0F0F')]) + lg('cap', [(0, '#1F2326'), (0.4, '#4A5056'), (1, '#0E1012')]),
    '<ellipse cx="128" cy="230" rx="52" ry="8" fill="url(#sh)"/>'
    '<path d="M86 80 C 80 100, 78 150, 82 214 C 84 226, 172 226, 174 214 C 178 150, 176 100, 170 80 Z" fill="url(#kb)"/>'
    '<path d="M94 48 L162 48 L170 82 L86 82 Z" fill="url(#cap)"/><path d="M118 22 L138 22 L142 48 L114 48 Z" fill="url(#cap)"/>'
    '<rect x="92" y="126" width="72" height="56" rx="8" fill="#FFF8E7"/>'
    '<circle cx="128" cy="150" r="14" fill="#E53935"/><path d="M122 138 l6 5 l6 -5" stroke="#2E7D32" stroke-width="3" fill="none"/>'
    '<rect x="108" y="168" width="40" height="5" rx="2.5" fill="#8E1B1B" opacity="0.6"/>'
    '<path d="M96 96 C 92 140, 92 180, 96 208" stroke="#FFFFFF" stroke-width="6" opacity="0.5" stroke-linecap="round" fill="none"/>')

# Vinegar / soy sauce: dark glass bottle
icons['vinegar'] = svg(
    lg('vb', [(0, '#1B0F08', 0.95), (0.3, '#5A3014', 0.92), (0.4, '#9A5A2A', 0.9), (0.55, '#3E200C', 0.92), (1, '#120904', 0.95)]) + lg('cap', [(0, '#7F0E0E'), (0.4, '#D32F2F'), (1, '#5A0808')]),
    '<ellipse cx="128" cy="232" rx="42" ry="7" fill="url(#sh)"/>'
    '<path d="M116 52 L140 52 L140 92 C 140 106, 162 114, 162 136 L162 216 C 162 228, 94 228, 94 216 L94 136 C 94 114, 116 106, 116 92 Z" fill="url(#vb)"/>'
    '<rect x="112" y="30" width="32" height="26" rx="4" fill="url(#cap)"/>'
    '<path d="M94 150 L162 150 L162 196 L94 196 Z" fill="#F5EFE0"/>'
    '<rect x="106" y="164" width="44" height="6" rx="3" fill="#5A3014"/><rect x="114" y="178" width="28" height="5" rx="2.5" fill="#9A5A2A"/>'
    '<path d="M104 132 L102 212" stroke="#FFFFFF" stroke-width="5" opacity="0.4" stroke-linecap="round"/>')

# Legumes: bag of lentils/chickpeas with window
icons['legumes'] = svg(
    lg('bag', [(0, '#B9C4CF', 0.95), (0.3, '#FFFFFF', 0.95), (1, '#9AA7B4', 0.95)]) + rg('pea', [(0, '#F7DDA8'), (0.7, '#D9AE5E'), (1, '#A87A30')], 0.35, 0.3, 0.8),
    '<ellipse cx="128" cy="226" rx="78" ry="10" fill="url(#sh)"/>'
    '<path d="M66 60 L190 60 L198 214 C 198 222, 58 222, 58 214 Z" fill="url(#bag)"/>'
    '<path d="M66 60 L190 60 L188 46 L68 46 Z" fill="#2E7D32"/>'
    '<g>' + ''.join(f'<circle cx="{x}" cy="{y}" r="10" fill="url(#pea)"/>' for x, y in
                     [(90,130),(110,124),(130,130),(150,124),(170,130),(80,152),(100,148),(120,152),(140,148),(160,152),(178,150),(90,174),(110,170),(130,174),(150,170),(170,174),(84,196),(104,194),(124,198),(144,194),(164,196),(182,192)]) + '</g>'
    '<rect x="70" y="70" width="116" height="40" rx="6" fill="#2E7D32"/><rect x="84" y="84" width="72" height="10" rx="5" fill="#FFFFFF" opacity="0.9"/>'
    '<path d="M76 74 L70 206" stroke="#FFFFFF" stroke-width="6" opacity="0.5" stroke-linecap="round"/>')

# Tortilla / flatbread stack
icons['tortilla'] = svg(
    rg('tt', [(0, '#FBEBC8'), (0.7, '#EBCB8E'), (1, '#C9A25C')], 0.45, 0.4, 0.7),
    '<ellipse cx="128" cy="204" rx="104" ry="16" fill="url(#sh)"/>'
    + ''.join(f'<ellipse cx="128" cy="{y}" rx="100" ry="30" fill="url(#tt)" stroke="#C9A25C" stroke-width="2"/>' for y in (176, 164, 152, 140)) +
    '<g fill="#B5833C" opacity="0.55">' + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.6}"/>' for x, y, r in [(90,134,6),(120,128,4),(150,140,7),(176,132,4),(104,148,4),(140,124,5),(70,142,3)]) + '</g>')

# Frozen food box with snowflake and frost
snow = '<g stroke="#FFFFFF" stroke-width="5" stroke-linecap="round">' + ''.join(f'<line x1="0" y1="0" x2="0" y2="-26" transform="rotate({a})"/>' for a in range(0, 360, 60)) + \
       ''.join(f'<path d="M-7 -18 L0 -12 L7 -18" fill="none" transform="rotate({a})"/>' for a in range(0, 360, 60)) + '</g>'
icons['frozen'] = svg(
    lg('box', [(0, '#4FC3F7'), (1, '#0288D1')], 0, 1) + lg('side', [(0, '#0277BD'), (1, '#01579B')], 0, 1),
    '<ellipse cx="128" cy="222" rx="96" ry="11" fill="url(#sh)"/>'
    '<path d="M40 100 L176 100 L176 206 L40 206 Z" fill="url(#box)"/>'
    '<path d="M176 100 L216 84 L216 190 L176 206 Z" fill="url(#side)"/>'
    '<path d="M40 100 L80 84 L216 84 L176 100 Z" fill="#B3E5FC"/>'
    f'<g transform="translate(108 152)">{snow}</g>'
    '<path d="M40 100 C 60 110, 70 96, 90 106 C 110 96, 130 110, 150 100 C 160 106, 170 100, 176 100" stroke="#E1F5FE" stroke-width="6" fill="none"/>'
    '<path d="M48 112 L48 198" stroke="#FFFFFF" stroke-width="5" opacity="0.4" stroke-linecap="round"/>')

# Pizza slice
icons['pizza'] = svg(
    lg('crust', [(0, '#F2B866'), (1, '#B9762A')], 0, 1) + lg('cheese', [(0, '#FFE08A'), (1, '#F6B93B')], 0, 1),
    '<ellipse cx="128" cy="214" rx="72" ry="10" fill="url(#sh)"/>'
    '<path d="M44 64 C 90 40, 166 40, 212 64 L128 214 Z" fill="url(#cheese)"/>'
    '<path d="M40 60 C 90 32, 166 32, 216 60 L210 76 C 166 54, 90 54, 46 76 Z" fill="url(#crust)"/>'
    '<g fill="#C62828">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in [(100,90,13),(150,92,12),(126,128,12),(116,170,8)]) + '</g>'
    '<g fill="#E57373" opacity="0.6">' + ''.join(f'<circle cx="{x-3}" cy="{y-3}" r="{r*0.4}"/>' for x, y, r in [(100,90,13),(150,92,12),(126,128,12)]) + '</g>'
    '<g fill="#2E7D32">' + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="6" ry="3" transform="rotate({a} {x} {y})"/>' for x, y, a in [(132,96,30),(110,118,-20),(146,130,50),(124,150,10)]) + '</g>'
    '<path d="M150 150 C 156 164, 152 176, 146 184" stroke="#F6B93B" stroke-width="6" fill="none" stroke-linecap="round"/>')

# French fries in a red carton
icons['fries'] = svg(
    lg('fry', [(0, '#FFE08A'), (1, '#F2B33D')], 1, 0) + lg('box', [(0, '#B71C1C'), (0.35, '#E53935'), (0.5, '#FF6F60'), (0.65, '#D32F2F'), (1, '#8E1414')]),
    '<ellipse cx="128" cy="228" rx="68" ry="9" fill="url(#sh)"/>'
    + ''.join(f'<rect x="{x}" y="{y}" width="14" height="110" rx="3" fill="url(#fry)" transform="rotate({a} {x+7} {y+110})" stroke="#D9982A" stroke-width="1.5"/>'
              for x, y, a in [(80,40,-14),(98,30,-6),(116,24,0),(134,28,5),(152,34,10),(168,44,16),(106,46,-2),(142,48,4)]) +
    '<path d="M68 110 L188 110 L176 222 L80 222 Z" fill="url(#box)"/>'
    '<path d="M68 110 C 100 130, 156 130, 188 110" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.6"/>'
    '<circle cx="128" cy="168" r="18" fill="#FFFFFF" opacity="0.9"/><path d="M120 168 l6 6 l10 -12" stroke="#E53935" stroke-width="4" fill="none" stroke-linecap="round"/>')

# Shrimp
icons['shrimp'] = svg(
    lg('sh1', [(0, '#FFB199'), (0.5, '#FF7F5C'), (1, '#E0532E')], 1, 1),
    '<ellipse cx="128" cy="210" rx="96" ry="12" fill="url(#sh)"/>'
    '<path d="M70 150 C 60 96, 110 54, 160 64 C 200 72, 214 110, 196 140 C 190 128, 176 120, 162 124 C 168 104, 150 88, 128 96 C 104 104, 96 130, 108 156 Z" fill="url(#sh1)"/>'
    '<g stroke="#FFFFFF" stroke-width="5" opacity="0.7" fill="none" stroke-linecap="round"><path d="M100 92 C 108 104, 108 116, 100 128"/><path d="M126 74 C 134 86, 134 98, 128 106"/><path d="M156 70 C 162 80, 162 92, 158 100"/><path d="M182 84 C 186 94, 186 104, 182 112"/></g>'
    '<path d="M70 150 L44 166 L62 176 L52 196 L84 172 L108 156 Z" fill="#E0532E"/>'
    '<path d="M196 140 C 210 146, 222 140, 226 128" stroke="#E0532E" stroke-width="3" fill="none"/><path d="M190 136 C 204 150, 222 154, 232 146" stroke="#E0532E" stroke-width="2" fill="none"/>'
    '<circle cx="186" cy="118" r="4" fill="#3E2723"/>')

# Tofu block
icons['tofu'] = svg(
    lg('top', [(0, '#FFFFFF'), (1, '#F1EDE2')], 1, 1) + lg('front', [(0, '#F3EFE3'), (1, '#DED7C4')], 0, 1) + lg('side', [(0, '#E1DAC7'), (1, '#C8BFA8')], 0, 1),
    '<ellipse cx="128" cy="212" rx="96" ry="12" fill="url(#sh)"/>'
    '<path d="M48 104 L140 80 L208 100 L116 126 Z" fill="url(#top)"/>'
    '<path d="M48 104 L116 126 L116 196 L48 174 Z" fill="url(#front)"/>'
    '<path d="M116 126 L208 100 L208 170 L116 196 Z" fill="url(#side)"/>'
    '<g fill="#D9D1BC" opacity="0.7">' + ''.join(f'<circle cx="{x}" cy="{y}" r="2"/>' for x, y in [(70,130),(90,150),(80,170),(140,140),(170,150),(190,130),(156,170)]) + '</g>'
    '<path d="M58 106 L136 86" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>')

# Spread jar (peanut butter / tahini / chocolate spread) with knife
icons['spread'] = svg(
    GLASS + lg('pb', [(0, '#C98A4B'), (0.5, '#A8692E'), (1, '#6E3F14')], 1, 1) + lg('lid', [(0, '#5D3A1A'), (0.4, '#9C6B3C'), (1, '#3E240E')]) + lg('knife', [(0, '#9AA3AC'), (0.5, '#F4F6F8'), (1, '#8A939C')]),
    jar('pb', 'lid', '<rect x="72" y="126" width="112" height="58" rx="6" fill="#FFF8E7"/>'
        '<g transform="translate(128 154)"><ellipse rx="22" ry="13" fill="#C98A4B"/><path d="M-10 -2 C -4 -8, 4 -8, 10 -2 C 4 4, -4 4, -10 -2 Z" fill="#8E5A28"/></g>') +
    '<g transform="rotate(35 190 60)"><rect x="184" y="10" width="12" height="70" rx="6" fill="url(#knife)"/><rect x="182" y="78" width="16" height="44" rx="5" fill="#3E2723"/></g>')

# Instant noodle cup
icons['noodles'] = svg(
    lg('cup', [(0, '#C62828'), (0.35, '#EF5350'), (0.5, '#FF8A80'), (0.65, '#E53935'), (1, '#8E1414')]) + rg('lid', [(0, '#FFFFFF'), (0.6, '#E0E4E8'), (1, '#AEB6BE')]),
    '<ellipse cx="128" cy="226" rx="70" ry="10" fill="url(#sh)"/>'
    '<path d="M62 76 L80 212 C 82 224, 174 224, 176 212 L194 76 Z" fill="url(#cup)"/>'
    '<path d="M70 132 L186 132 L182 168 L74 168 Z" fill="#FFFFFF" opacity="0.92"/>'
    '<g stroke="#F2B33D" stroke-width="4" fill="none" stroke-linecap="round"><path d="M88 150 c 8 -10 16 10 24 0 s 16 10 24 0 s 16 10 24 0"/></g>'
    '<ellipse cx="128" cy="76" rx="68" ry="16" fill="url(#lid)"/>'
    '<path d="M150 70 C 172 50, 196 46, 210 56 C 202 72, 178 80, 150 76 Z" fill="url(#lid)" stroke="#AEB6BE" stroke-width="1"/>'
    '<path d="M80 92 L94 204" stroke="#FFFFFF" stroke-width="5" opacity="0.4" stroke-linecap="round"/>')

# Pickles jar
icons['pickles'] = svg(
    GLASS + lg('br', [(0, '#C5D86D', 0.85), (1, '#8DAA2E', 0.9)], 1, 1) + lg('lid', [(0, '#1B5E20'), (0.4, '#43A047'), (1, '#0F3D12')]) +
    lg('pk', [(0, '#3E6B12'), (0.4, '#6B9A2A'), (1, '#2E5410')]),
    '<ellipse cx="128" cy="224" rx="72" ry="10" fill="url(#sh)"/>'
    '<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#br)"/>'
    + ''.join(f'<rect x="{x}" y="104" width="26" height="100" rx="13" fill="url(#pk)" transform="rotate({a} {x+13} 154)"/>' for x, a in [(70,-6),(100,4),(130,-3),(160,7)]) +
    '<g fill="#C5D86D" opacity="0.6">' + ''.join(f'<circle cx="{x}" cy="{y}" r="2.5"/>' for x, y in [(80,130),(86,170),(112,120),(116,180),(142,140),(146,190),(172,128),(176,168)]) + '</g>'
    '<path d="M66 92 C 60 100, 58 110, 58 120 L58 200 C 58 214, 198 214, 198 200 L198 120 C 198 110, 196 100, 190 92 Z" fill="url(#glass)" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="2"/>'
    '<rect x="66" y="58" width="124" height="36" rx="8" fill="url(#lid)"/>'
    '<g stroke="#000" stroke-opacity="0.15" stroke-width="2">' + ''.join(f'<line x1="{x}" y1="62" x2="{x}" y2="90"/>' for x in range(76, 186, 10)) + '</g>'
    '<path d="M70 110 L70 196" stroke="#FFFFFF" stroke-width="6" opacity="0.6" stroke-linecap="round"/>')

# Popcorn tub
pop = lambda x, y, r: f'<g transform="translate({x} {y})"><circle r="{r}" fill="url(#pc)"/><circle cx="{r*0.5}" cy="{-r*0.4}" r="{r*0.7}" fill="url(#pc)"/><circle cx="{-r*0.5}" cy="{-r*0.3}" r="{r*0.65}" fill="url(#pc)"/></g>'
icons['popcorn'] = svg(
    rg('pc', [(0, '#FFFFFF'), (0.7, '#FFF3C4'), (1, '#E9C46A')]),
    '<ellipse cx="128" cy="228" rx="68" ry="9" fill="url(#sh)"/>'
    + ''.join(pop(x, y, r) for x, y, r in [(84,92,14),(108,76,15),(132,70,16),(156,78,15),(176,92,13),(96,104,13),(124,96,14),(150,100,14),(70,108,11),(186,108,11)]) +
    '<path d="M66 106 L190 106 L176 222 L80 222 Z" fill="#FFFFFF"/>'
    + ''.join(f'<path d="M{66+i*24.8} 106 L{78.8+i*24.8} 106 L{82+i*19.2} 222 L{80+i*19.2} 222 Z" fill="#E53935"/>' for i in range(5)) +
    '<path d="M66 106 L190 106" stroke="#B71C1C" stroke-width="3"/>'
    '<rect x="100" y="146" width="56" height="34" rx="6" fill="#FFFFFF" opacity="0.95"/><rect x="110" y="158" width="36" height="8" rx="4" fill="#E53935"/>')

# Sandwich (triangle, layered)
icons['sandwich'] = svg(
    lg('br', [(0, '#F8E3B6'), (1, '#E8C687')], 0, 1) + lg('crust', [(0, '#C98A3E'), (1, '#9C6420')], 0, 1),
    '<ellipse cx="128" cy="214" rx="100" ry="12" fill="url(#sh)"/>'
    '<path d="M40 176 L216 176 L128 64 Z" fill="url(#crust)"/>'
    '<path d="M50 172 L206 172 L128 74 Z" fill="url(#br)"/>'
    '<path d="M36 182 C 70 168, 90 194, 128 180 C 166 194, 186 168, 220 182 L216 190 L40 190 Z" fill="#43A047"/>'
    '<path d="M40 188 L216 188 L216 200 L40 200 Z" fill="#E57373"/>'
    '<path d="M40 198 L216 198 L208 206 L48 206 Z" fill="#FFD54F"/>'
    '<path d="M40 204 L216 204 L216 214 C 216 220, 40 220, 40 214 Z" fill="url(#crust)"/>'
    '<path d="M64 166 L128 86" stroke="#FFFFFF" stroke-width="4" opacity="0.5" stroke-linecap="round"/>')

os.makedirs(OUT, exist_ok=True)
for name, s in icons.items():
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
print(len(icons), 'svgs')
