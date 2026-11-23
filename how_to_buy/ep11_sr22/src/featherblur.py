import sys
from PIL import Image, ImageFilter, ImageDraw
def fblur(im, boxes, s, r=14, feather=10):
    bl = im.filter(ImageFilter.GaussianBlur(r*s)); m = Image.new("L", im.size, 0); d = ImageDraw.Draw(m)
    for b in boxes: d.rectangle([int(v*s) for v in b], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather*s)); return Image.composite(bl, im, m)
B={'sr22-0.jpg':[(312,166,398,206)],'sr22-1.jpg':[(212,202,288,231)],'cirrussr-0.jpg':[(348,158,462,192),(301,80,349,102)],'cirrussrgts-0.jpg':[(138,163,247,197)]}
outs=[]
for f,bs in B.items():
    im=Image.open(f).convert('RGB'); s=im.width/600
    im=fblur(fblur(im,bs,s),bs,s,r=8,feather=4); im.save('../ph/'+f,quality=93)
    outs.append(im.crop(tuple(int(v*s) for v in (bs[0][0]-80,bs[0][1]-60,bs[0][2]+80,bs[0][3]+60))).resize((600,300)))
c=Image.new('RGB',(1200,600)); [c.paste(i,((k%2)*600,(k//2)*300)) for k,i in enumerate(outs)]; c.save('../cs9.png')
