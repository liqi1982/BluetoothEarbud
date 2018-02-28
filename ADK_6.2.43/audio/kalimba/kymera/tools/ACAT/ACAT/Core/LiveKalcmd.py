############################################################################
# CONFIDENTIAL
#
# Copyright (c) 2016 - 2017 Qualcomm Technologies International, Ltd.
#
############################################################################
"""
Module used to connect to a Kalcmd simulation.
"""
from . import LiveChip
from . import Arch
from . import CoreUtils as cu


class DmAccessorKalcmd(cu.global_options.kmem.DmAccessor):
    """
    Modified DM memory accessor for kalcmd.
    """
    def __init__(self, kalcmd_object):
        def read_dm_block(address, words_to_fetch):
            """
            Read words from kalsim.
            """
            return kalcmd_object.block_mem_read(
                kalcmd_object.kalcmd2.kalmem_spaces.DM,
                address,
                words_to_fetch
            )

        def write_dm_block(address, values):
            """
            Write words to kalsim.
            """
            kalcmd_object.block_mem_write(
                kalcmd_object.kalcmd2.kalmem_spaces.DM,
                address,
                values
            )

        cu.global_options.kmem.MemoryAccessor.__init__(
            self,
            read_dm_block,
            write_dm_block,
            cu.global_options.kmem.DmMemoryBlock
        )
        self.__dict__['_kalcmd_object'] = kalcmd_object

    def addresses_per_word(self):
        """
        Utility functions called by the base class to allow PM/DM variations
        """
        return self.addr_per_word

    def get_address_width(self):
        """
        Utility functions called by the base class to allow PM/DM variations
        """
        return self.address_width

    def get_data_width(self):
        """
        Utility functions called by the base class to allow PM/DM variations
        """
        return self.data_width


class PmAccessorKalcmd(cu.global_options.kmem.PmAccessor):
    """
    Modified PM memory accessor for kalcmd.
    """
    def __init__(self, kalcmd_object):
        def read_pm_block(address, words_to_fetch):
            """
            Read words from kalsim.
            """
            return kalcmd_object.block_mem_read(
                kalcmd_object.kalcmd2.kalmem_spaces.PM,
                address,
                words_to_fetch
            )

        def write_pm_block(address, values):
            """
            Write words to kalsim.
            """
            kalcmd_object.block_mem_write(
                kalcmd_object.kalcmd2.kalmem_spaces.PM,
                address,
                values
            )

        cu.global_options.kmem.MemoryAccessor.__init__(
            self,
            read_pm_block,
            write_pm_block,
            cu.global_options.kmem.PmMemoryBlock
        )
        self.__dict__['_kalcmd_object'] = kalcmd_object

    def addresses_per_word(self):
        """
        Utility functions called by the base class to allow PM/DM variations
        """
        return self.addr_per_word

    def get_address_width(self):
        """
        Utility functions called by the base class to allow PM/DM variations
        """
        return self.address_width

    def get_data_width(self):
        """
        kalaccess does not expose "pm data width" from dspinfo,
        but it's the same for all current architectures.
        """
        return 32


##################################################
class LiveKalcmd(LiveChip.LiveChip):
    """
    @brief Provide access to chip data on a live chip over SPI
    """

    def __init__(self, kalcmd_object, processor):
        """
        @brief Constructor

        Starts a spi connection to a chip
        @param[in] self Pointer to the current object
        @param[in] kalcmd_object
        @param[in] processor
        """
        LiveChip.LiveChip.__init__(self)

        self._kalcmd_object = kalcmd_object
        self.processor = processor

        self.dm = DmAccessorKalcmd(kalcmd_object)
        self.pm = PmAccessorKalcmd(kalcmd_object)

        cu.debug_log("Initialising connection with Kalcmd")

        kal_arch = self._kalcmd_object.getKalArch()

        kalimba_name = self._kalcmd_object.getKalimbaName()

        # kalarch
        # print self._kalcmd_object.get_version()
        # kal_version = self._kalcmd_object.get_version()
        chip_id = None
        if kalimba_name == "csra68100_audio":
            # Crescendo
            chip_arch = "Hydra"
            chip_revision = 0
            chip_id = 0x46

            self.dm.addr_per_word = 4
            self.dm.address_width = 32
            self.dm.data_width = 32

            self.pm.addr_per_word = 4
            self.pm.address_width = 32
        elif kalimba_name == "QCC3400_audio" or kalimba_name == "QCC512x_audio":
            # Stre
            chip_arch = "Hydra"
            chip_revision = 0
            chip_id = 0x49

            self.dm.addr_per_word = 4
            self.dm.address_width = 32
            self.dm.data_width = 32

            self.pm.addr_per_word = 4
            self.pm.address_width = 32

        elif kalimba_name == "napier_audio":
            chip_arch = "Napier"
            chip_revision = 0
            chip_id = 0

            self.dm.addr_per_word = 4
            self.dm.address_width = 32
            self.dm.data_width = 32

            self.pm.addr_per_word = 4
            self.pm.address_width = 32

        elif kalimba_name == "blue":
            chip_arch = "Bluecore"
            raise Exception("Chip Not supported yet")
        elif kalimba_name == "kas":
            chip_arch = "KAS"
            raise Exception("Chip Not supported yet")

        if chip_id is not None:
            Arch.chip_select(kal_arch, chip_arch, chip_id, chip_revision)
        else:
            Arch.chip_select(kal_arch, chip_arch, chip_id)

    @LiveChip.re_entrant_lock_decorator
    def get_proc_reg(self, reg_name):
        """
        @brief Return the value of the processor register specified in 'reg_name'.
        reg_name is a string containing the reg_name of the register in upper or
        lower case, with or without the prefix 'REGFILE_'
        e.g. "REGFILE_PC", "rMAC", "R10".
        This may raise a number of exceptions, such as KeyError or
        AttributeError.
        @param[in] self Pointer to the current object
        @param[in] reg_name
        """
        reg_name = reg_name.upper()
        if "REGFILE_" in reg_name:
            # replace REGFILE with REG which is recognised by kalcmd
            reg_name = reg_name.replace("REGFILE", "REG")
        elif "REG_" in reg_name:
            # this is the good format for the kalcmd
            pass
        else:
            # kalcmd needs "REG_" prefix
            reg_name = "REG_" + reg_name

        # Get the kalcmd internal reg number
        reg_number = self._kalcmd_object.kalcmd2.kal_regs.__dict__[reg_name]
        return self._kalcmd_object.querryDspReg(reg_number)

    @LiveChip.re_entrant_lock_decorator
    def get_all_proc_regs(self):
        """
        @brief Returns a dictionary containing all processor registers.
        Dictionary maps name to value.
        NB on a running chip there is the obvious risk of tearing.
        Consider stopping the chip if this is an issue.
        @param[in] self Pointer to the current object
        """
        regs = {}
        for reg_name in self._kalcmd_object.kalcmd2.kal_regs.__dict__.keys():
            if reg_name[0] != '_':
                regs[
                    reg_name.replace("REG_", "REGFILE_")
                ] = self.get_proc_reg(reg_name)

        return regs
