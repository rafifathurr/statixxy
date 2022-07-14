# -*- mode: python -*-

"""
http://stackoverflow.com/questions/2598669/...
ghostscript-whats-are-the-differences-between-linux-and-windows-variants
On Windows you have two executables, gswin32c.exe and gswin32.exe 
    instead of gs only. The first one is to run Ghostscript on the 
    commandline ("DOS box"), the second one will open two GUI windows: 
    one to render the output, another one which is console-like and 
    shows GS stdout/stderr or takes your command input if you run GS in 
    interactive mode.
"""

block_cipher = None


a = Analysis(['launch.py'],
             pathex=[
                 'C:/Windows/WinSxS/x86_microsoft-windows-m..namespace-downlevel_31bf3856ad364e35_10.0.18362.1_none_3da3af2845f54b85',
                 'C:/Windows/WinSxS/x86_microsoft-windows-m..namespace-downlevel_31bf3856ad364e35_10.0.18362.1_none_b1d1ec2d5a8d1113',
                 'C:/Windows/WinSxS/x86_microsoft-windows-m..namespace-downlevel_31bf3856ad364e35_10.0.18362.1_none_e78143cd9eb12740',
                 'D:/sofa_dev_win/sofa4packaging/sofastats',
             ],
             binaries=[
                ('D:/sofa_dev_win/dependencies/wkhtmltopdf.exe', '.'),  ## the docs for 3.4 show the structure as (binary, subfolder) where '.' means the main folder
                ('D:/sofa_dev_win/dependencies/convert.exe', '.'),  ## need portable version
                ('D:/sofa_dev_win/dependencies/gswin64c.exe', '.'),
                ('D:/sofa_dev_win/dependencies/gsdll64.dll', '.'),
             ],
             datas=[
                ('D:/sofa_dev_win/dependencies/delegates.xml', '.'), 
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['start'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher, level=9)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,  ## because this is a onedir approach the binaries are being collected in COLLECT not put in the EXE itself
          name='sofastats',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon='D:\sofa_dev_win\packaging\sofa_32x32.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='sofastats')
