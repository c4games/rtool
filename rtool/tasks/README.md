## 资源处理使用文档  
#### 需求  
为了方便说明，现假设需要处理的资源目录结构如下
A--AA--(AAA1,AAA2)
   BB--(BBB1)
   CC  
其中资源文件位于叶子节点目录中，即AAA1，AAA2，BBB1和CC  
项目中常见的资源处理需求如下
1.将AAA1和AAA2中的资源做同一种处理，例如将两个目录中的资源文件合成一张图片，并做PVRTC4压缩，然后加密
2.将BBB1中的资源做另一种处理，例如做RGB565转换
3.将CC中的资源直接复制到包里
路径和命名规则的需求
需求和解决方式：
0.以目录为单位，通过配置文件对不同目录做不同的资源处理操作  
1.父目录配置影响子路目录配置，子目录配置覆盖父目录配置 －－》[]  
2.配置为单一目录时配置项仅对所配置目录生效 －－》['anim/flash']  
3.配置为多个目录时多个目录使用同一配置，生成同一结果,结果输出目录相对结构与输入目录第一项相同 －－》['anim/flash1','anim/flash2']  
4.某些操作是对前面操作的生成文件进行的，配置文件配置于原始资源目录中  
5.先合图后转格式  
6.需要能够调整最终输出资源的目录结构  
7.通过传入更新列表，仅对资源中需要更新的文件进行操作  
8.使用者需要掌握的配置规则越少越好  
9.对于原始资源的变更有处理，例如资源删除 
10.取消index的使用，在动画描述文件汇总加入texture属性用于标记动画所使用的图片 

1.input设置为[]时，配置项满足“父目录配置影响子路目录配置，子目录配置覆盖父目录配置”这一规则，生成资源放置于输出路径下与原始资源目录相对目录结构相同的目录中  
2.input设置为['a']时，配置项仅对相对路径为a的唯一目录生效  
3.input设置为['a','b','c']时，a,b,c三个目录会根据配置项规则生成一份资源，生成资源放置于输出路径下的a目录中  
4.可以通过setting.yaml将需要前置处理操作的输出文件指向某一工作目录，再将后续操作的输入指向该工作目录相同位置；同时设置setting.yaml中的runorder项，调整操作的运行顺序。   
5.目前支持的操作中，合图，拷贝文件，动画处理等为前置操作，转格式，加密为后置操作，其特殊处理在插件部分详细介绍。  
6.最终输出目录结构由BasePostAction处理，使用者可继承该类覆写方法来改变输出目录结构，默认提供两种输出方式。一种是保留原始资源目录的目录结构。第二种是通过映射表将资源放置到指定目录。  
7.使用者可以通过传入diff_dict来指定本次资源处理需要处理的资源目录  

关于python2.x在windows上的中文路径问题
问题描述
python2本身的默认编码格式是ascii，一般可以指定源码编码为utf-8，但是仅对python代码文件生效。因此对于各种python库，一般都需要传入utf-8编码的字符串
python2中字符串有两种，一种是str的对象，以字节码形势存储，另一种是unicode对象，以unicode字符为单位存储
python2中涉及字符串拼接时，如果两个字符串不是相同字符集编码，则会出问题
windows的cmd中使用的并非utf-8，而是cp1252或cp936，cp1252兼容cp936
windows的路径使用\为分割符，有可能会发生错误的转义，尤其时目录名以u或x开头的时候

解决方案：
由os库的walk或listdir遍历生成的路径，是使用系统默认编码的，也就是说在windows上是cp1252编码，因此传入json，yaml，plist，log等库会有问题，需要使用utils.encodePath传入这些库中
当调用第三方工具例如TexturePacker之行时，传递给第三方工具的路径由于要在cmd里运行，因此需要再转换回cp1252编码，这时要对之前编码的路径使用utils.decodePath
有时尽管严格按照上述规则进行后，仍然发生编码问题，这种情况基本上时python内部在字符串操作中，对字符串重新进行了编码，例如传入python结构的字符串，字符串拼接，替换等操作。这种情况先将字符串使用print输出至cmd看一下，如果汉字显示正确，则基本上可以确定属于此种情况。使用sys.stdin.encoding或sys.stdout.encoding对字符串进行encode或decode
将字符串存入python的结构，然后print整个结构，就能看到字符串的字节码，以此判别当前字符串的编码

常见问题：
1.未找到index.json 该文件由合图插件PackupTexture在生成合图的同时产生，因此未找到该文件说明插件没有执行，请检查配置文件。
2.TexturePacker对于同名文件处理会有问题，因此原始资源文件命名需要有一定规则，避免文件同名的情况
