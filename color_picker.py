import gtk, sys
def tohex(c):
   #Convert to hex string
   #little hack to fix bug
   s = [hex(int(c[0]*256))[2:].zfill(2),hex(int(c[1]*256))[2:].zfill(2),hex(int(c[2]*256))[2:].zfill(2)]
   for item in enumerate(s):
      if item[1]=='100':
         s[item[0]]='ff'
   return ''.join(s)
csd = gtk.ColorSelectionDialog('Gnome Color Chooser')
cs = csd.colorsel
cs.set_has_opacity_control(True)
cs.set_current_alpha(65536)
if csd.run()!=gtk.RESPONSE_OK:
   sys.exit()
c = cs.get_current_color()
print(tohex((c.red/65536.0, c.green/65536.0, c.blue/65536.0)))
