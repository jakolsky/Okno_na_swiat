import cv2, numpy as np, json
src=cv2.imread('zrodlo/panorama.png'); H,W=src.shape[:2]
def poly(pts): m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(pts,np.int32)],255); return m
def curve(pts):  # y per column, interpolated
    xs,ys=zip(*pts); return np.interp(np.arange(W),xs,ys)
ridge=curve([(0,170),(120,172),(250,182),(400,188),(560,192),(650,180),(720,160),(780,148),(850,142),(930,150),(1000,165),(1060,175),(1200,180),(1400,190),(1600,195),(1977,195)])
crest=curve([(0,425),(220,425),(330,440),(420,465),(480,472),(560,462),(650,448),(750,435),(850,422),(950,415),(1340,425),(1400,412),(1500,398),(1600,385),(1680,378),(1977,378)])
Y=np.arange(H)[:,None]
below_ridge=(Y>=ridge[None,:]).astype(np.uint8)*255
below_crest=(Y>=crest[None,:]).astype(np.uint8)*255
b,g,r=[src[...,i].astype(int) for i in range(3)]
mx=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b)
sky=(((b>r+50)&(b>g+10))|((mn>185)&(mx-mn<60))).astype(np.uint8)*255
tree=poly([(915,0),(1660,0),(1665,80),(1645,170),(1600,240),(1520,262),(1430,282),(1402,330),(1402,532),(1333,532),(1338,322),(1300,272),(1240,232),(1150,215),(1050,200),(990,182),(935,122),(912,60)])
tree=cv2.bitwise_and(tree,cv2.bitwise_not(sky))
tree=cv2.bitwise_and(tree,cv2.bitwise_not(poly([(1720,0),(1977,0),(1977,748),(1700,642),(1668,602),(1670,422),(1650,402),(1630,332),(1626,282),(1650,252),(1682,202),(1682,182),(1640,157),(1625,140)])))
tree=cv2.morphologyEx(tree,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
barn=poly([(948,300),(1030,212),(1062,208),(1322,214),(1348,300),(1342,446),(1195,446),(1195,400),(1100,400),(1100,446),(948,450)])
barn=cv2.bitwise_and(barn,cv2.bitwise_not(tree))
houseL=poly([(0,0),(274,0),(274,76),(112,82),(110,195),(257,238),(260,302),(228,312),(228,420),(217,440),(214,575),(200,582),(198,700),(152,745),(122,795),(0,795)])
houseR=poly([(1720,0),(1977,0),(1977,748),(1872,748),(1862,682),(1760,682),(1700,642),(1668,602),(1670,422),(1650,402),(1630,332),(1626,282),(1650,252),(1682,202),(1682,182),(1640,157),(1632,140)])

def fill_rows(img,mask,left_only=False):
    out=img.copy(); Wd=img.shape[1]
    for y in range(img.shape[0]):
        row=mask[y]>0
        if not row.any(): continue
        x=0
        while x<Wd:
            if not row[x]: x+=1; continue
            a=x
            while x<Wd and row[x]: x+=1
            b=x; L=b-a
            for i in range(L):
                if left_only and a>0:
                    sx=a-1-(i % a); out[y,a+i]=img[y,sx]; continue
                if (i < L/2 and a-1-i>=0) or b+(L-1-i)>=Wd:
                    sx=max(0,a-1-i) if a>0 else min(Wd-1,b+i)
                else:
                    sx=min(Wd-1,b+(L-1-i)) if b<Wd else max(0,a-1-(L-1-i))
                out[y,a+i]=img[y,sx]
    return out
def fill_up(img,ridge_y):
    out=img.copy()
    for x in range(img.shape[1]):
        r=int(ridge_y[x])
        for y in range(r,img.shape[0]):
            sy=max(0,2*r-y-1); out[y,x]=img[sy,x]
    return out
def soft(img,orig,mask):
    bl=cv2.GaussianBlur(img,(9,9),0); m=cv2.dilate(mask,np.ones((5,5),np.uint8))>0
    o=orig.copy(); o[m]=bl[m]; o[mask==0]=orig[mask==0]; return o
def inpaint(img,mask,scale=4,rad=6):
    sm=cv2.resize(img,(W//scale,H//scale),interpolation=cv2.INTER_AREA)
    mm=cv2.resize(mask,(W//scale,H//scale),interpolation=cv2.INTER_NEAREST)
    mm=cv2.dilate(mm,np.ones((3,3),np.uint8))
    f=cv2.inpaint(sm,mm,rad,cv2.INPAINT_TELEA)
    f=cv2.GaussianBlur(cv2.resize(f,(W,H),interpolation=cv2.INTER_CUBIC),(5,5),0)
    out=img.copy(); m=mask>0; out[m]=f[m]; return out
feather=lambda m:cv2.GaussianBlur(m,(3,3),0)
def rgba(img,alpha): return np.dstack([img,alpha])

X0,X1=275,1615
# warstwa 0: niebo i góry (wypełnione pod grzbietem, za drzewem)
treeP=cv2.dilate(poly([(915,0),(1660,0),(1665,80),(1645,170),(1600,240),(1520,262),(1430,282),(1402,330),(1402,532),(1333,532),(1338,322),(1300,272),(1240,232),(1150,215),(1050,200),(990,182),(935,122),(912,60)]),np.ones((7,7),np.uint8))
houses=cv2.dilate(cv2.bitwise_or(houseL,houseR),np.ones((5,5),np.uint8))
far=fill_rows(src, cv2.bitwise_and(cv2.bitwise_or(treeP,houses),cv2.bitwise_not(below_ridge)), True)
far=fill_up(far, ridge)
# warstwa 1: wzgórza, dolina, wioska, las (pod grzbietem); pod łąką/drzewem/stodołą wypełnione
occl1=cv2.bitwise_and(cv2.bitwise_or(cv2.bitwise_or(below_crest,tree),barn), below_ridge)
occl1=cv2.bitwise_or(cv2.bitwise_and(cv2.bitwise_or(cv2.bitwise_or(below_crest,treeP),barn),below_ridge),houses)
mid=fill_rows(src, cv2.bitwise_and(cv2.bitwise_or(treeP,cv2.bitwise_or(barn,houses)),below_ridge), True)
mid=fill_up(mid, crest); mid_a=feather(below_ridge)
# warstwa 2: łąka (bez drzewa i stodoły, które są osobno)
ground_mask=cv2.bitwise_and(below_crest, cv2.bitwise_not(cv2.bitwise_or(tree,barn)))
ground=fill_rows(src, cv2.bitwise_and(cv2.bitwise_or(cv2.dilate(tree,np.ones((5,5),np.uint8)),cv2.bitwise_or(barn,houses)),below_crest))
ground_a=feather(below_crest)
out='img/'
import os
for f in os.listdir(out): os.remove(out+f)
cv2.imwrite(out+'p0_far.jpg', far[:,X0:X1], [cv2.IMWRITE_JPEG_QUALITY,88])
cv2.imwrite(out+'p1_mid.webp', rgba(mid,mid_a)[:,X0:X1], [cv2.IMWRITE_WEBP_QUALITY,88])
cv2.imwrite(out+'p2_ground.webp', rgba(ground,ground_a)[:,X0:X1], [cv2.IMWRITE_WEBP_QUALITY,88])
meta={'W':X1-X0,'H':H,'crest':[round(float(crest[x]),1) for x in range(X0,X1,20)],'sprites':{}}
def sprite(name,mask,x0clip=None):
    ys,xs=np.where(mask>0); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    cv2.imwrite(out+name+'.webp', rgba(src,feather(mask))[y0:y1,x0:x1], [cv2.IMWRITE_WEBP_QUALITY,90])
    meta['sprites'][name]=[int(x0-X0),int(y0),int(x1-X0),int(y1)]
sprite('s_tree',tree); sprite('s_barn',barn); sprite('s_houseL',houseL); sprite('s_houseR',houseR)
json.dump(meta,open('tools/meta.json','w')); print(meta['sprites'])
