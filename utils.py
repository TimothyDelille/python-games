
skull = [
'0000000000000',
'0011111111100',
'0111111111110',
'0111111111110',
'1111001001111',
'1100001000011',
'1100011100011',
'0111111111110',
'0111110111110',
'0001111111000',
'0001101011000',
]

cloud = [
    "00000000000000000000000",
    "00000000000000000000000",
    "000111110000000000000000",
    "011111111101",
    '011111111111'
]


def draw_img(img, x, y, width, color_map, canvas):
    h = len(img)
    w = len(img[0])

    obj = []
    for i in range(h):
        for j in range(w):
            val = img[i][j]
            obj_ = canvas.create_rectangle(
                x + j*width,
                y + i*width,
                x + (j+1)*width,
                y + (i+1)*width,
                fill=color_map[val],
                outline=color_map[val]
            )
            obj.append(obj_)
    return obj
