#coding=utf-8
# 有可能废弃
pngquant_command_template = "pngquant --verbose --force --output $output -- $input "
pngquant_command_nq_template = "pngquant --nofs --verbose --force --output $output -- $input "
alpha_etc1_command_template = "TexturePacker --trim-mode None --force-squared --sheet $dstname --data $plist --opt ETC1 $srcname --size-constraints POT --disable-rotation --premultiply-alpha --border-padding 0 --shape-padding 0 --padding 0 --extrude 0"
png8_command_template = "TexturePacker --trim-mode None --sheet $dstname --data $plist --opt RGBA8888 $srcname --disable-rotation --border-padding 0 --shape-padding 0 --size-constraints AnySize --width $width --height $height"
pvr_RGBA8888_command_template = "TexturePacker --algorithm Basic --trim-mode None --sheet $dstname --data $plist --opt RGBA8888 $srcname --disable-rotation --border-padding 0 --shape-padding 0 --padding 0 --extrude 0"
# 使用中
etc_command_template = "TexturePacker --trim-mode None --sheet $dstname --data $plist --texture-format $textureformat --opt $opt $srcname --disable-rotation --border-padding 0 --shape-padding 0 --padding 0 --extrude 0 $extra"
tp_command_template = "TexturePacker --trim-mode None --sheet $dstname --data $plist --texture-format $textureformat --opt $opt $srcname --disable-rotation --border-padding 0 --shape-padding 0 --padding 0 --extrude 0 $extra"
tp_2pic_rgb_command_template = "TexturePacker --texture-format $textureformat --trim-mode None --sheet $dstname --data $plist --opt $opt $srcname --size-constraints POT --force-squared --disable-rotation --border-padding 0 --shape-padding 0 --premultiply-alpha --padding 0 --extrude 0 $extra"
alpha_command_template = "TexturePacker --trim-mode None --force-squared --sheet $dstname --data $plist --opt ALPHA $srcname --size-constraints POT --disable-rotation --border-padding 0 --shape-padding 0 --padding 0 --extrude 0"