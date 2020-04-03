import os
import os.path

root ="E:\\rtool\\example_result"

for p,_,fns in os.walk(root):
	for fn in fns:
		if ".pkm" in fn:
			name,_ = os.path.splitext(fn)
			os.rename(os.path.join(p,fn),os.path.join(p,name+".png"))