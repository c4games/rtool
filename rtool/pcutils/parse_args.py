#coding=utf-8
import argparse

def parse_args(parser, args_array):

    args = parser.parse_args(args_array)

    input_path = None
    key_value_arguments = {}
    flag_arguments = []

    d = vars(args)
    for k in d:
        if d[k] != None and d[k]!=False:
            if k == 'input_path':
                input_path = d[k]
            elif d[k] == True:
                flag_arguments.append(k)
            else:
                key_value_arguments[k] = d[k]

    return (input_path,flag_arguments,key_value_arguments)


def create_args(input_paths, flag_arguments, key_value_arguments):
    # 2015-09-01 18:31:56 owen
    # 被两个不同的配置文件里分配写入 force-squared 和 force_squared 坑了
    flag_arguments = set([ x.replace('_','-') for x in flag_arguments ])
    args = []
    for k in flag_arguments:
        args.append('--'+k)
    for k,v in key_value_arguments.items():
        args.append('--'+k.replace('_','-'))
        args.append(str(v))
    args.extend(input_paths)
    return args

def parse_texturepacker_args(s):
    parser = argparse.ArgumentParser(description='tp')

    parser.add_argument('input_path',nargs='+')

    parser.add_argument('--auto-sd', action='store_true')
    parser.add_argument('--disable-auto-alias', action='store_true')
    parser.add_argument('--disable-clean-transparency', action='store_true')
    parser.add_argument('--disable-rotation', action='store_true')
    parser.add_argument('--dither-atkinson', action='store_true')
    parser.add_argument('--dither-atkinson-alpha', action='store_true')
    parser.add_argument('--dither-fs', action='store_true')
    parser.add_argument('--dither-fs-alpha', action='store_true')
    parser.add_argument('--dither-none-linear', action='store_true')
    parser.add_argument('--dither-none-nn', action='store_true')
    parser.add_argument('--enable-rotation', action='store_true')
    parser.add_argument('--flip-pvr', action='store_true')
    parser.add_argument('--force-identical-layout', action='store_true')
    parser.add_argument('--force-publish', action='store_true')
    parser.add_argument('--force-squared', action='store_true')
    parser.add_argument('--force-word-aligned', action='store_true')
    parser.add_argument('--gui', action='store_true')
    #parser.add_argument('--help', action='store_true')
    parser.add_argument('--heuristic-mask', action='store_true')
    parser.add_argument('--license-info', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--shape-debug', action='store_true')
    parser.add_argument('--trim-sprite-names', action='store_true')
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--reduce-border-artifacts', action='store_true')
    parser.add_argument('--premultiply-alpha', action='store_true')
    parser.add_argument('--multipack', action='store_true')

    parser.add_argument('--maxrects-heuristics')
    parser.add_argument('--basic-order')
    parser.add_argument('--basic-sort-by')
    parser.add_argument('--activate-license')
    parser.add_argument('--algorithm')
    parser.add_argument('--andengine-magfilter')
    parser.add_argument('--andengine-minfilter')
    parser.add_argument('--andengine-packagename')
    parser.add_argument('--andengine-wraps')
    parser.add_argument('--andengine-wrapt')
    parser.add_argument('--background-color')
    parser.add_argument('--border-padding')
    parser.add_argument('--classfile-file')
    parser.add_argument('--common-divisor-x')
    parser.add_argument('--common-divisor-y')
    parser.add_argument('--content-protection')
    parser.add_argument('--data')
    parser.add_argument('--dpi')
    parser.add_argument('--dxt-mode')
    parser.add_argument('--etc1-quality')
    parser.add_argument('--extrude')
    parser.add_argument('--format')
    parser.add_argument('--header-file')
    parser.add_argument('--height')
    parser.add_argument('--ignore-files')
    parser.add_argument('--inner-padding')
    parser.add_argument('--java-file')
    parser.add_argument('--jpg-quality')
    parser.add_argument('--jxr-color-mode')
    parser.add_argument('--jxr-compression')
    parser.add_argument('--jxr-trim-flexbits')
    parser.add_argument('--max-height')
    parser.add_argument('--max-size')
    parser.add_argument('--max-width')
    parser.add_argument('--mipmap-min-size')
    parser.add_argument('--opt')
    parser.add_argument('--pack-mode')
    parser.add_argument('--padding')
    parser.add_argument('--png-opt-level')
    parser.add_argument('--pvr-quality')
    parser.add_argument('--replace')
    parser.add_argument('--scale')
    parser.add_argument('--scale-mode')
    parser.add_argument('--shape-padding')
    parser.add_argument('--sheet')
    parser.add_argument('--size-constraints')
    parser.add_argument('--texture-format')
    parser.add_argument('--texturepath')
    parser.add_argument('--trim-mode')
    parser.add_argument('--trim-threshold')
    parser.add_argument('--variant')
    parser.add_argument('--webp-quality')
    parser.add_argument('--width')

    """
    问题:
    用 parse_args 来解析 TexturePacker 参数带来的一个问题是无法处理输入文件（image_path）中穿插着其他参数的情况
    比如 TexturePacker 能识别下面的情况

        TexturePacker a.png --format cocos2d b.png

    但是用 parse_args 解析上面的参数会报错

        error: unrecognized arguments: b.png

    不确定这个问题，通过修改 add_argument 或者增加额外的 add_argument 是否能够解决

    使用 parser.parse_known_args 是可以处理这种情况的，但是会把 b.png 放到一个 unknonw arguments 的数组里面


        (args,unknown) = parser.parse_known_args(args)

    也不是一个完美的解决方案

    目前只能假设我们在实际打包的过程中构造TexturePacker参数时，
    不会出现 image_path 中穿插其他参数的情况

    """
    # TODO 有没有参数顺序的问题,某个参数必须在另一个参数后面？

    return parse_args(parser,s)

def parse_pngquant_args(s):
    parser = argparse.ArgumentParser(description='pngquant')

    '''
    usage:  pngquant [options] [ncolors] [pngfile [pngfile ...]]

options:
  --force           overwrite existing output files (synonym: -f)
  --skip-if-larger  only save converted files if they're smaller than original
  --nofs            disable Floyd-Steinberg dithering
  --verbose         print status messages (synonym: -v)


  --output file     output path, only if one input file is specified (synonym: -o)
  --ext new.png     set custom suffix/extension for output filenames
  --quality min-max don't save below min, use fewer colors below max (0-100)
  --speed N         speed/quality trade-off. 1=slow, 3=default, 11=fast & rough
  --posterize N     output lower resolution color (e.g. for ARGB4444 output)


    '''

    parser.add_argument('input_path',nargs='+')

    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('--skip-if-larger', action='store_true')
    parser.add_argument('--nofs', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('-o', '--output')
    parser.add_argument('--ext')
    parser.add_argument('--quality')
    parser.add_argument('--speed')
    parser.add_argument('--posterize')

    return parse_args(parser,s)