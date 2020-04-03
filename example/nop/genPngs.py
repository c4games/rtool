import os
import os.path
import random
from PIL import Image,ImageDraw,ImageFont

def genPng(width,height,color,text,textSize,textcolor,path):
	img = Image.new(mode="RGBA",size=(width,height),color=color)
	draw = ImageDraw.Draw(img)
	textLen = len(text)/2
	draw.text((width/2-textSize/2*textLen,height/2-textSize/2*textLen),text,fill=textcolor,font=ImageFont.truetype(font="./SimHei.ttf",size=textSize))
	img.save(os.path.join(path,text+".png"))
	img.close()

def randomColor():
	r = random.randint(0,255)
	g = random.randint(0,255)
	b = random.randint(0,255)
	a = random.randint(0,255)
	return r,g,b,a


if __name__ == "__main__":
	r,g,b,a = randomColor()
	genPng(120,100,(r,g,b,a),"AAA",60,(255-r,255-g,255-b,225-a),"E:\\rtool\\example\\aaa")
	for i in range(0,20):
		r,g,b,a = randomColor()
		genPng(50,50,(r,g,b,a),"C-"+str(i),20,(255-r,255-g,255-b,225-a),"E:\\rtool\\example\\aaa\\ccc")

	r,g,b,a = randomColor()
	genPng(512,1024,(r,g,b,a),"BBB1",80,(255-r,255-g,255-b,225-a),"E:\\rtool\\example\\bbb")
	r,g,b,a = randomColor()
	genPng(512,1024,(r,g,b,a),"BBB2",80,(255-r,255-g,255-b,225-a),"E:\\rtool\\example\\bbb")