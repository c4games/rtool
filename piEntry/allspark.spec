# -*- mode: python -*-

block_cipher = None


cfg_a = Analysis(['cfg.py'],
             datas= [("/data/work/rtool/rtool/*.yaml","rtool")],
             pathex=['/data/work/rtool/piEntry'],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

uploadgs_a = Analysis(['uploadgs.py'],
             datas= [("/data/work/rtool/rtool/*.yaml","rtool")],
             pathex=['/data/work/rtool/piEntry'],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

MERGE((cfg_a,'cfg','cfg'),(uploadgs_a,'uploadgs','uploadgs'))

pyz = PYZ(cfg_a.pure, cfg_a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          cfg_a.scripts,
          exclude_binaries=True,
          name='cfg',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               cfg_a.binaries,
               cfg_a.zipfiles,
               cfg_a.datas,
               strip=False,
               upx=True,
               name='cfg')


pyz = PYZ(uploadgs_a.pure, uploadgs_a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          uploadgs_a.scripts,
          exclude_binaries=True,
          name='uploadgs',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               uploadgs_a.binaries,
               uploadgs_a.zipfiles,
               uploadgs_a.datas,
               strip=False,
               upx=True,
               name='uploadgs')