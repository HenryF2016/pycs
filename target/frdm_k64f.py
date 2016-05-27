# -----------------------------------------------------------------------------
"""

Target file for FRDM-K64F

NXP development board for Kinetis Chips

"""
# -----------------------------------------------------------------------------

import conio
import cli
import jlink
import cortexm
import soc.kinetis as soc
import mem

# -----------------------------------------------------------------------------

soc_name = 'MK64FN1M0VLL12'
prompt = 'frdm_k64f'

# -----------------------------------------------------------------------------

class target(object):
  """frdm_k64f - NXP development board for Kinetis Chips"""

  def __init__(self, ui, usb_number):
    self.ui = ui
    info = soc.lookup(soc_name)
    self.jlink = jlink.JLink(usb_number, info['cpu_type'], jlink._JLINKARM_TIF_SWD)
    self.cpu = cortexm.cortexm(self, ui, self.jlink, info['cpu_type'], info['priority_bits'])
    self.soc = soc.soc(self.cpu, info)
    self.mem = mem.mem(self.cpu, self.soc)

    self.menu_root = (
      ('cpu', self.cpu.menu, 'cpu functions'),
      ('da', self.cpu.cmd_disassemble, cortexm.help_disassemble),
      ('exit', self.cmd_exit),
      ('go', self.cpu.cmd_go),
      ('halt', self.cpu.cmd_halt),
      ('help', self.ui.cmd_help),
      ('jlink', self.jlink.cmd_jlink),
      ('mem', self.mem.menu, 'memory functions'),
      ('regs', self.cpu.cmd_regs),
      ('soc', self.soc.menu, 'system on chip functions'),
    )

    self.ui.cli.set_root(self.menu_root)
    self.set_prompt()
    self.jlink.cmd_jlink(self.ui, None)

  def set_prompt(self):
    indicator = ('*', '')[self.jlink.is_halted()]
    self.ui.cli.set_prompt('\n%s%s> ' % (prompt, indicator))

  def cmd_exit(self, ui, args):
    """exit the application"""
    self.jlink.jlink_close()
    ui.exit()

# -----------------------------------------------------------------------------