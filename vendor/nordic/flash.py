#-----------------------------------------------------------------------------
"""
Flash Driver for Nordic Chips

Notes:

1) Instantiating this driver does not touch the hardware. No reads or writes.
We only access the hardware when the user wants to do something.

2) The SVD file has the UICR region as 4KiB in size. On the chip I've looked
at the actual flash storage is 1KiB, but we maintain the lie. It's not
harmful- just be aware that you may not be able to use the whole region for
storage.

3) The UICR region doesn't erase with a normal page erase, despite what you
might think from reading the reference manual. The "erase all" can be used
to clobber it.

4) According to the datasheet we can't write a code0 region from the SWD debug
interface. So - we don't bother with code 0 regions. I don't have one in this
chip in any case (FICR.CLENR0 = 0xffffffff). In general it looks like the code0
page is deprecated.

5) There are a couple of registers (FICR) that provide flash size and page size
information. I don't read them at startup because I don't want the program to
do any hardware access during initialisation. They should be checked for
consistency with the hard coded page size and region size values.

"""
#-----------------------------------------------------------------------------

import time

import util
import mem

#-----------------------------------------------------------------------------

# NVMC.CONFIG bits
CONFIG_REN = 0 # read enable
CONFIG_WEN = 1 # write enable
CONFIG_EEN = 2 # erase enable

#-----------------------------------------------------------------------------

class flash(object):

  def __init__(self, device):
    self.device = device
    self.hw = self.device.NVMC
    self.init = False
    self.page_size = 1 << 10 # Check FICR.CODEPAGESIZE
    self.pages = []
    self.pages.extend(mem.flash_pages(self.device, 'flash1', self.page_size)) # Check FICR.CODESIZE
    self.pages.extend(mem.flash_pages(self.device, 'UICR', self.page_size))
    # build some memory regions to represent the flash memory
    self.code1 = mem.region(None, self.device.flash1.address, self.device.flash1.size)
    self.uicr = mem.region(None, self.device.UICR.address, self.device.UICR.size)

  def __wait4ready(self):
    """wait for flash operation completion"""
    for i in xrange(5):
      if self.hw.READY.rd() & 1:
        # operation completed
        return
      time.sleep(0.1)
    assert False, 'time out waiting for flash ready'

  def sector_list(self):
    """return a list of flash pages"""
    return self.pages

  def check_region(self, x):
    """return None if region x meets the flash write requirements"""
    if x.adr & 3:
      return 'memory region is not 32-bit aligned'
    if x.size & 3:
      return 'memory region is not a multiple of 32-bits'
    if self.code1.contains(x):
      return None
    if self.uicr.contains(x):
      return None
    return 'memory region is not within flash'

  def firmware_region(self):
    """return the name of the flash region used for firmware"""
    return 'flash1'

  def erase_all(self):
    """erase all (code 1 and uicr) - return non-zero for an error"""
    # erase enable
    self.hw.CONFIG.wr(CONFIG_EEN)
    self.__wait4ready()
    # erase all
    self.hw.ERASEALL.wr(1)
    self.__wait4ready()
    # back to read only
    self.hw.CONFIG.wr(CONFIG_REN)
    self.__wait4ready()
    return 0

  def erase(self, page):
    """erase a flash page - return non-zero for an error"""
    # erase enable
    self.hw.CONFIG.wr(CONFIG_EEN)
    self.__wait4ready()
    # erase the page
    if page.name == 'flash1':
      self.hw.ERASEPAGE.wr(page.adr)
    elif page.name == 'UICR':
      self.hw.ERASEUICR.wr(page.adr)
    else:
      assert False, 'unrecognised flash page name %s' % page.name
    self.__wait4ready()
    # back to read only
    self.hw.CONFIG.wr(CONFIG_REN)
    self.__wait4ready()
    return 0

  def write(self, mr, io):
    """write memory region with data from an io buffer"""
    # write enable
    self.hw.CONFIG.wr(CONFIG_WEN)
    self.__wait4ready()
    # write the data
    self.device.cpu.wrmem32(mr.adr, mr.size >> 2, io)
    self.__wait4ready()
    # back to read only
    self.hw.CONFIG.wr(CONFIG_REN)
    self.__wait4ready()

  def __str__(self):
    return util.display_cols([x.col_str() for x in self.pages])

#-----------------------------------------------------------------------------
