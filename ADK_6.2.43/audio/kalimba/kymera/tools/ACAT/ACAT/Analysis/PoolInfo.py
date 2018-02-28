############################################################################
# CONFIDENTIAL
#
# Copyright (c) 2012 - 2017 Qualcomm Technologies International, Ltd.
#
############################################################################
"""
Module used to analyse the pool memory.
"""
import copy
import math
import itertools

from ACAT.Analysis import Analysis
from ACAT.Analysis import DebugLog
from ACAT.Core import CoreTypes as ct
from ACAT.Core import CoreUtils as cu
from ACAT.Core import Arch

CONSTANT_DEPENDENCIES = {
    'one_strict': (
        ('$MEM_MAP_P0_STACK_END', '$MEM_MAP_STACK_END'),
        ('$DM2_RAM_BASE_ADDRESS', '$MEM_MAP_P1_STACK_END'),
        ('$DM1_RAM_BASE_ADDRESS', '$DATA_RAM_START_ADDRESS')
    )
}
VARIABLE_DEPENDENCIES = {
    'strict': ('L_aMemoryPoolControl', 'L_oversize_allocation_count'),
    'Hydra': ('L_mmu_buffer_handles',),
    'other_architecture': (
        '$DM1_ZI_REGION.__Limit', '$DM2_REGION.__Base', '$DM2_REGION.__Limit',
        '$DM1_REGION.__Base', '$DM1_REGION.__Limit'
    )
}
TYPE_DEPENDENCIES = {
    'tPlMemoryPoolControlStruct': (
        'blockSizeWords', 'numBlocksFree', 'pFirstFreeBlock', 'minBlocksFree'
    )
}


class PoolInfo(Analysis.Analysis):
    """
    @brief This class encapsulates an analysis for memory pool usage.
    """

    def __init__(self, **kwarg):
        # Call the base class constructor.
        Analysis.Analysis.__init__(self, **kwarg)
        # Look up the debuginfo once. Don't do it here though; we don't want
        # to throw an exception from the constructor if something goes
        # wrong.
        self._do_debuginfo_lookup = True
        self.pool_count = 0
        self.block_header_size = 0
        self.block_overhead_words = 0
        self.pmalloc_debug_enabled = False
        self.pooldata = None
        self.p_pool = []

    def run_all(self):
        """
        @brief Perform all useful analysis and spew the output to the formatter.
        It outputs the memory pool info, the debug info and the errors that
        have occurred.
        @param[in] self Pointer to the current object
        """
        # Look up the debug information, unless we already have.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False

        self.formatter.section_start('Memory Pool Info')

        def __remove_duplicates(input_list):
            # Remove duplicate entries from the supplied list, maintaining
            # ordering.
            tmp = []
            for element in input_list:
                if not element in tmp:
                    tmp.append(element)
            return tmp

        full_summary = []
        all_info = []
        all_errors = []

        if self.chipdata.is_volatile():
            all_info.append(
                "Skipped block ownership tests: live chip is too slow"
            )

        for pool in range(self.pool_count):
            (summary, info, errors) = self._inspect_pool(pool)
            full_summary.extend(summary)
            all_info.extend(info)
            all_errors.extend(errors)

        full_summary.extend(self._check_oversize_allocations())

        # Remove duplicates from all_info and all_errors
        # (since we may warn multiple times about, say, being attached to a live chip)
        all_info = __remove_duplicates(all_info)
        all_errors = __remove_duplicates(all_errors)

        self.formatter.section_start('Summary')
        self.formatter.output_list(full_summary)
        self.formatter.section_end()

        self.formatter.section_start('Debug info')
        self.formatter.output(
            "pmalloc_debug_enabled = " + str(self.pmalloc_debug_enabled)
        )
        self.formatter.output_list(all_info)
        self.formatter.section_end()

        self.formatter.section_start('Errors')
        if all_errors:
            self.formatter.alert('Memory pool errors found')
            self.formatter.output_list(all_errors)
        else:
            self.formatter.output('No memory pool errors found')
        self.formatter.section_end()

        self.display_configuration()


        self.formatter.section_start('Pool memory usage')
        self.get_watermarks()
        self.formatter.section_end()


        self.formatter.section_end()

        # If this is a live chip a subsequent analysis should read new values
        # from the chip. So set the flag so that debuginfo is looked up.
        if self.chipdata.is_volatile():
            self._do_debuginfo_lookup = True

    def analyse_pool(self, pool):
        """
        @brief Analyse a specific memory pool for consistency.
        @param[in] self Pointer to the current object
        @param[in] pool
        """
        # _inspect_pool does all of the useful work
        (summary, info, errors) = self._inspect_pool(pool)

        self.formatter.section_start('Pool ' + str(pool))
        self.formatter.output_list(summary)
        self.formatter.output_list(info)
        self.formatter.output_list(errors)
        self.formatter.section_end()

        # If this is a live chip a subsequent analysis should read new values
        # from the chip. So set the flag so that debuginfo is looked up.
        if self.chipdata.is_volatile():
            self._do_debuginfo_lookup = True

    def get_block_from_addr(self, address):
        """
        @brief Get information about the pmalloc block associated with a given DM
        address. Returns None if the address is not in a pmalloc pool.
        (You can access the pool variable via block.parent, or read the pool
        number via block.pool if you like.)
        @param[in] self Pointer to the current object
        @param[in] address
        """
        # Look up the debug information, unless we already have.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False

        # Work out which pool
        found_pool = None
        found_block = None
        for pool in range(self.pool_count):
            # Work out the extent of the pool
            start_of_pool = self.p_pool[pool]
            block_size = self.pooldata[pool].get_member(
                'blockSizeWords'
            ).value + self.block_overhead_words
            blocks_total = self.debuginfo.get_dm_const(
                self.pooldata[pool].get_member('numBlocksFree').address,
                0,
            )
            end_of_pool = (start_of_pool + blocks_total * block_size)
            if address >= start_of_pool and address <= end_of_pool:
                found_pool = pool
                found_block = (address - start_of_pool) / (block_size)
                break

        if found_pool is None:
            return None

        # If this is a live chip a subsequent analysis should read new values
        # from the chip. So set the flag so that debuginfo is looked up.
        if self.chipdata.is_volatile():
            self._do_debuginfo_lookup = True

        return self.get_pool(found_pool)[found_block]

    def block_is_free(self, block):
        """
        @brief Takes a block variable (such as might be obtained via get_block_from_addr)
        and works out whether or not it's free. Also takes an address in DM
        and performs the same function on the block containing that address.
        This can be used to validate e.g. references found via
        Analysis.find_references().
        Returns True or False, may throw an exception if 'block' is not an
        address in DM or a block variable.
        @param[in] self Pointer to the current object
        @param[in] block
        """
        if isinstance(block, int):
            blockvar = self.get_block_from_addr(block)
        else:
            blockvar = block
        return blockvar.value[0] != blockvar.pool

    def get_pool(self, pool):
        """
        @brief Get a specific memory pool, split into blocks.
        Returns a nonstandard Variable containing individual blocks of the
        pool.
        Note: 'pool' is the unique pool ID for a pool; if you want a pool in
        DM2 (e.g. L_Mem2Pool2) you'll need to know what that is (e.g. pool=14)
        @param[in] self Pointer to the current object
        @param[in] pool
        """
        # Look up the debug information, unless we already have.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False

        # Get the pool control data.
        # Blocks all have a header, so work out the actual size of each block.
        block_size = self.pooldata[pool].get_member(
            'blockSizeWords'
        ).value + self.block_overhead_words

        # Get initial value of numBlocksFree, i.e. total blocks in the pool
        blocks_total = self.debuginfo.get_dm_const(
            self.pooldata[pool].get_member('numBlocksFree').address, 0
        )
        # What the free ptr was initialised to: first block in the pool;
        # dualcore - first free block
        initial_free_ptr = self.p_pool[pool]

        # Get the pool contents (could be slow on a live chip).
        # This relies on a slightly complicated (but safe) trick: the pool variable
        # (e.g. 'L_MemPool5') has address <initial_free_ptr>, so 'get' that.
        pool_var = self.chipdata.get_var_strict(initial_free_ptr)
        if pool_var.parent is not None and Arch.kal_arch == 4:
            pool_var = self.chipdata.get_var_strict(str(pool_var.parent.name))

        # Because we don't want to modify the real pool variable use deepcopy
        # for the values
        fake_pool_var = ct.Variable(
            name=pool_var.name,
            address=pool_var.address,
            size=pool_var.size,
            value=copy.deepcopy(pool_var.value),
            var_type=pool_var.type,
            debuginfo=None,
            members=[],
            parent=None
        )
        fake_pool_var.array_len = blocks_total

        # Change the Type field to reflect the fact that this fake var is a
        # list of blocks
        fake_pool_var.type_name = fake_pool_var.type_name + \
            '[' + str(block_size) + ']'

        for block_id in range(blocks_total):
            start_addr = fake_pool_var.address + block_size * \
                block_id * Arch.addr_per_word  # contiguous
            # Use deep copy to avoid changing the original values.
            block_var = ct.Variable(
                name=fake_pool_var.name + '[~' + str(block_id) + '~]',
                address=start_addr,
                size=block_size,
                value=fake_pool_var.value[
                    (start_addr - fake_pool_var.address) / Arch.addr_per_word:
                    (
                        (start_addr - fake_pool_var.address) / Arch.addr_per_word
                        + block_size
                    )
                ],
                var_type=None,
                debuginfo=None,
                members=None,
                parent=fake_pool_var
            )
            block_var.type_name = fake_pool_var.type_name
            block_var.pool = pool
            fake_pool_var.members.append(block_var)

        # If this is a live chip a subsequent analysis should read new values
        # from the chip. So set the flag so that debuginfo is looked up.
        if self.chipdata.is_volatile():
            self._do_debuginfo_lookup = True

        return fake_pool_var

    @DebugLog.suspend_log_decorator(0)
    def ret_get_watermarks(self):
        """
        @brief Same as get_watermarks, but it will return values rather than
        print outs.
        @param[in] self Pointer to the current object
        @param[out] List with the heap usage + pools statistic.
        """
        # Look up the debug information.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False
        else:
            # update the pool data
            self.pooldata = self.chipdata.get_var_strict(
                'L_aMemoryPoolControl'
            )

        pools_statistic = {}

        total_size = 0
        current_free = 0
        min_free = 0
        for pool in range(self.pool_count):
            # Get a list of the basic pool data
            block_size = self.pooldata[pool].get_member('blockSizeWords').value
            blocks_total = self.debuginfo.get_dm_const(
                self.pooldata[pool].get_member('numBlocksFree').address, 0
            )
            blocks_free = self.pooldata[pool].get_member('numBlocksFree').value
            blocks_min = self.pooldata[pool].get_member('minBlocksFree').value

            total_size += block_size * blocks_total
            current_free += block_size * blocks_free
            min_free += block_size * blocks_min

            if pools_statistic.get(block_size) is None:
                pools_statistic[block_size] = (blocks_total, blocks_free, blocks_min)
            else:
                pools_statistic[block_size] = tuple(
                    (
                        x + y
                        for x, y in zip(
                            pools_statistic[block_size],
                            (blocks_total, blocks_free, blocks_min)
                        )
                    )
                )

        pools_statistic = sorted(pools_statistic.iteritems())

        return total_size, current_free, min_free, pools_statistic

    def get_watermarks(self):
        """
        @brief Returns the minimum available memory for the total, the free
        and the minimum free memories.
        @param[in] self Pointer to the current object
        """
        total_size, current_free, min_free, pools_statistic = \
            self.ret_get_watermarks()

        output_str = ""
        for pool_statistic in pools_statistic:
            output_str += (
                "pools with size %2d words, total size,   %3d words\n" % (
                    pool_statistic[0],
                    pool_statistic[1][0]
                )
            )
            output_str += (
                "pools with size %2d words, current free, %3d words\n" % (
                    pool_statistic[0],
                    pool_statistic[1][1]
                )
            )
            output_str += (
                "pools with size %2d words, minimum free, %3d words\n" % (
                    pool_statistic[0],
                    pool_statistic[1][2]
                )
            )
            output_str += "\n"

        output_str += (
            "entire pool memory, total size,   " +
            cu.mem_size_to_string(total_size * Arch.addr_per_word) +
            "\n"
        )
        output_str += (
            "entire pool memory, current free, " +
            cu.mem_size_to_string(current_free * Arch.addr_per_word) +
            "\n"
        )
        output_str += (
            "entire pool memory, minimum free, " +
            cu.mem_size_to_string(min_free * Arch.addr_per_word) +
            "\n"
        )
        # use output_raw to keep the spaces.
        self.formatter.output_raw(output_str)

    @DebugLog.suspend_log_decorator(0)
    def clear_watermarks(self):
        """
        @brief Clears the minimum available memory watermark by equating it with the current
        available memory.
        @param[in] self Pointer to the current object
        """
        # Look up the debug information.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False
        else:
            # update the pool data
            self.pooldata = self.chipdata.get_var_strict(
                'L_aMemoryPoolControl'
            )

        for pool in range(self.pool_count):
            blocks_free = self.pooldata[pool].get_member('numBlocksFree').value
            # Wash down the watermark (min available =  current available)
            self.chipdata.set_data(
                self.pooldata[pool].get_member('minBlocksFree').address,
                [blocks_free]
            )

    def display_configuration(self):
        """
        @brief Prints out the pool configuration.
        @param[in] self Pointer to the current object
        """
        # Look up the debug information.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False
        else:
            # update the pool data
            self.pooldata = self.chipdata.get_var_strict(
                'L_aMemoryPoolControl'
            )

        self.formatter.section_start('Pool Configuration')
        formatter_str = "pool nr %d: %5.1f KiB, %3d blocks of size %3d words" + \
            " (0x%08x bytes) at 0x%08x - 0x%08x\n"
        output_str = ""
        for pool in range(self.pool_count):
            blocks_total = self.debuginfo.get_dm_const(
                self.pooldata[pool].get_member('numBlocksFree').address,
                0
            )
            block_size = self.pooldata[pool].get_member('blockSizeWords').value
            pool_size = self.debuginfo.get_var_strict(self.p_pool[pool]).size
            output_str += formatter_str % (
                pool,
                pool_size / 1024.0,
                blocks_total,
                block_size,
                pool_size,
                self.p_pool[pool],
                self.p_pool[pool] + pool_size - 1
            )

        output_str += \
            "* for each block, one word is used for internal tracking data."
        self.formatter.output(output_str)

        self.formatter.section_end()

    ##################################################
    # Private methods
    ##################################################

    def _lookup_debuginfo(self):
        """
        @brief Queries debuginfo for information we will need to get the memory pool usage
        @param[in] self Pointer to the current object
        """
        # Look up the data addresses of the variables we need
        self.pooldata = self.chipdata.get_var_strict(
            'L_aMemoryPoolControl'
        )  # Pool control block

        self.p_pool = []  # Pointer to start of each pool

        # Check for PMALLOC_DEBUG
        # If L_memory_pool_limits exists then PMALLOC_DEBUG is enabled
        try:
            _ = self.debuginfo.get_var_strict(
                'L_memory_pool_limits'
            ).address
            self.pmalloc_debug_enabled = True
        except ct.DebugInfoNoVariable:
            self.pmalloc_debug_enabled = False

        # Blocks all have a header, so work out the actual size of each block (in words).
        # block_header_size needs to be rounded up since get_type_info[5]
        # returns the size in addressable units
        self.block_header_size = math.ceil(
            self.debuginfo.get_type_info('tPlMemoryBlockHeader')[5] /
            float(Arch.addr_per_word)
        )  # Don't use this directly
        self.block_overhead_words = int(self.block_header_size)
        if self.pmalloc_debug_enabled:
            self.block_overhead_words += 1  # For the guard word

        self.pool_count = self.pooldata.array_len

        if Arch.kal_arch != 4:
            for pool in range(self.pool_count):
                # Get initial value of free-block pointer, i.e. the first block
                # in the pool
                self.p_pool.append(
                    self.debuginfo.get_dm_const(
                        self.pooldata[pool].get_member(
                            'pFirstFreeBlock').address,
                        0
                    )
                )
        else:
            # For Crescendo, the initial pFirstFreeBlock is not stored in dm_const
            # So just look up the pool array by name

            try:
                _ = self.debuginfo.get_var_strict("L_MemPool0")
                single_core = True
            except ct.DebugInfoNoVariable:
                single_core = False

            try:
                # First go through the DM1 pools until one fails
                for pool in range(self.pool_count):
                    # For Crescendo, the initial pFirstFreeBlock is not stored in dm_const
                    # So just look up the pool array by name
                    if single_core:
                        poolname = "L_MemPool" + str(pool)
                    else:
                        poolname = "L_P{0:d}MemPool{1:d}".format(
                            self.chipdata.processor, pool
                        )
                    self.p_pool.append(
                        self.debuginfo.get_var_strict(poolname).address
                    )
            except ct.DebugInfoNoVariable:
                # Assume any that are left are in DM2
                dm2_start = pool
                for pool in range(dm2_start, self.pool_count):
                    if single_core:
                        poolname = "L_Mem2Pool" + str(pool - dm2_start)
                    else:
                        poolname = "L_P{0:d}Mem2Pool{1:d}".format(
                            self.chipdata.processor, pool - dm2_start
                        )
                    self.p_pool.append(
                        self.debuginfo.get_var_strict(poolname).address
                    )

    def _inspect_pool(self, pool):
        """
        @brief Examines a memory pool, extracting useful information and noting
        any inconsistencies.
        Input argument is a pool number.
        Returns a tuple containing (pool variable, pool summary, info, errors)
        where each element is itself a tuple of strings.
        @param[in] self Pointer to the current object
        @param[in] pool
        """
        # Look up the debug information, unless we already have.
        if self._do_debuginfo_lookup:
            self._lookup_debuginfo()
            self._do_debuginfo_lookup = False

        # The data we will return
        pool_summary = []
        pool_debug_info = []
        pool_errors = []

        # Our pool variable
        poolvar = self.get_pool(pool)

        # Get a list of the basic pool data
        block_size = self.pooldata[pool].get_member('blockSizeWords').value
        blocks_total = self.debuginfo.get_dm_const(
            self.pooldata[pool].get_member('numBlocksFree').address,
            0
        )
        blocks_free = self.pooldata[pool].get_member('numBlocksFree').value
        blocks_min = self.pooldata[pool].get_member('minBlocksFree').value
        free_ptr = self.pooldata[pool].get_member('pFirstFreeBlock').value

        pool_summary.append(
            "Pool: {0:>3d}  Size: {1:>3d}  Total: {2:>3d}  "
            "Free: {3:>3d}  Min: {4:>3d}".format(
                pool, block_size, blocks_total, blocks_free, blocks_min
            )
        )

        all_block_pointers = [b.address for b in poolvar.members]

        # Is the actual free-list pointer valid?
        if free_ptr == 0:
            pool_debug_info.append(
                "All blocks allocated for pool {0:>2d}".format(pool)
            )

        # Now a quick list of all the pointers to supposedly-free blocks.
        # This is used to make sure that every block which looks free is
        # actually part of the linked-list of free pointers.
        # Could do this:
        # free_block_pointers = [b.value[0] for b in
        # poolvar.members if b.value[0] in all_block_pointers]
        # but this would hide any corruption of the free list.
        #  if a->b->c and 'a' was corrupt, we
        # would still class 'c' as on the free list.
        # (We sort of want to do that for help with some
        # later analysis, but achieve it via the free_list_corruption_detected
        # flag instead). So let's do things properly, following the free-pointer.
        free_list_corruption_detected = False
        free_block_pointers = []
        block_num = -1
        while free_ptr != 0:
            if free_ptr in all_block_pointers:
                block_num = (free_ptr - poolvar.address) / (
                    (
                        block_size + self.block_overhead_words
                    ) * Arch.addr_per_word
                )
            else:
                pool_errors.append(
                    "Free-list pointer out of range, Pool: {0:>2d} Ptr: {1:0>6x}".
                    format(pool, free_ptr)
                )
                pool_errors.append(
                    "Subsequent analysis of pool " + str(pool) +
                    " may be incorrect"
                )
                free_list_corruption_detected = True
                break
            free_block_pointers.append(free_ptr)
            free_ptr = poolvar[block_num].value[0]

        # Remember which block is at the end of the free list
        last_free_block = block_num

        # Go through each block in the pool, checking that the poolID/free-list
        # pointer is plausible.
        for blockid, blockvar in enumerate(poolvar.members):
            # Don't initially know whether the block is free, allocated, or what
            blockvar.free = None
            # To begin with, assume no blocks have owners
            blockvar.owned = False

            # Information about who allocated the block, if it is known.
            block_allocation_data = None

            # There's a corner-case here;
            #  blockvar.value[0] for pool 0 is ambiguous. It will be
            # a NULL pointer if the block is at the end of the
            # free list, or 0 if the block is allocated.
            # Hence the check that this block isn't on the free list,
            # as well as having a header
            # word that matches the pool number.
            # For all other pools, allocated blocks will have a nonzero header
            # word.
            if blockvar.value[0] == pool and not (
                    blockvar.address in free_block_pointers):
                # Allocated block.
                blockvar.free = False
                if self.pmalloc_debug_enabled:
                    block_allocation_data = self.chipdata.cast(
                        blockvar.address, 'tPlMemoryBlockHeader'
                    )
            elif ((blockvar.value[0] in all_block_pointers) or
                  (blockvar.value[0] == 0 and blockid == last_free_block)):
                # A pointer to another block in this pool, OR
                # a pointer to NULL at the end of the free list.
                # Both imply that this block itself is free.
                # If it is, we should have added it to free_block_pointers.
                if blockvar.address in free_block_pointers:
                    blockvar.free = True
                else:
                    pool_errors.append(
                        (
                            "Block looks free, but not on free list. "
                            "Pool: {0:>2d} Block: {1:>3d} Ptr: {2:0>6x}"
                        ). format(
                            pool, blockid, blockvar.address
                        )
                    )
                    if free_list_corruption_detected:
                        # If a->b->c-> ... ->z, and we know the header for
                        # block 'a' was corrupt, the free list is clearly
                        # bogus. There's no point in tediously complaining
                        # about all the other blocks not being on the list.
                        # Mark the block as free so that we don't think it is
                        # 'unowned' later.
                        blockvar.free = True
            else:
                # Block Header looks corrupt.
                pool_errors.append(
                    (
                        "Block header not understood, Pool: "
                        "{0:>2d} Block: {1:>3d} Value: {2:0>6x}"
                    ). format(
                        pool, blockid, blockvar.value[0]
                    )
                )
                pool_errors.append(
                    "Subsequent analysis of pool " + str(pool) +
                    " may be incorrect"
                )

            # Now look at any debug information in the block
            if self.pmalloc_debug_enabled:
                # Check the guard word(s).
                # Since B-131138:
                # When something calls pmalloc, it requests numWords of data. We place a
                # guard word (0xfedcba) at [numWords+1]. If numWords+1 < block size, we
                # then fill in the remaining words with the value 0x012345.
                #
                # The mechanism below also works for older firmware which doesn't have B-131138,
                # since in that case the final word of the block was always
                # just 0xfedcba.
                index = blockvar.size - 1
                guard = blockvar.value[index]
                while (index > 0) and (guard == 0x012345):
                    index -= 1
                    guard = blockvar.value[index]
                if (index == 0) or (guard != 0xfedcba):
                    pool_errors.append(
                        "Guard word(s) overwritten, "
                        "Pool: {0:>2d} Block: {1:>3d} Ptr: {2:0>6x} "
                        "first overwritten pointer: {3:0>6x}".format(
                            pool, blockid, blockvar.address,
                            blockvar.address + index
                        )
                    )
                    actual_allocation_size = 9999
                else:
                    # Work out how much the user actually wanted to allocate.
                    actual_allocation_size = index + 1 - self.block_overhead_words

                # Now we know the actual_allocation_size, we can decode any
                # allocation data
                if not blockvar.free:
                    file_name_ptr = block_allocation_data.get_member('file').value
                    line = block_allocation_data.get_member('line').value
                    if line == 0:
                        # 'file' is actually the value of rlink when we called malloc.
                        # We can look that up to work out roughly where the allocation
                        # took place.
                        try:
                            owner = self.debuginfo.get_source_info(file_name_ptr)
                            owner_hint = (
                                owner.src_file + ', near line ' +
                                str(owner.line_number)
                            )
                        except ct.BundleMissingError:
                            owner_hint = (
                                "No source information."
                                "Bundle is missing."
                            )
                        block_debug_info = (
                            "Ptr: {0:0>6x} size: {1:>3d} allocated from pool: "
                            "{2:>2d} by: {3:s}".format(
                                blockvar.address, actual_allocation_size, pool,
                                owner_hint
                            )
                        )
                    else:
                        try:
                            filename = self.debuginfo.read_const_string(file_name_ptr)
                        except KeyError:
                            filename = "Filename cannot be read!"
                        except ct.BundleMissingError:
                            filename = (
                                "Filename cannot be read! " +
                                "Bundle is missing"
                            )
                        block_debug_info = (
                            "Ptr: {0:0>6x} size: {1:>3d} allocated from pool: "
                            "{2:>2d} by: {3:s}, line {4:d}".format(
                                blockvar.address, actual_allocation_size, pool,
                                filename, line
                            )
                        )

                    pool_debug_info.append(block_debug_info)

        # Check for any allocated blocks with no owners.
        if self.chipdata.is_volatile():
            pool_debug_info.append(
                "Skipped block ownership tests: live chip is too slow"
            )
            return (
                tuple(pool_summary), tuple(pool_debug_info),
                tuple(pool_errors)
            )

        # Search architecture-defined DM1/DM2 ranges

        if Arch.dm_ram_aliased:
            # DM1 and DM2 are the same physical RAM, so only search one of them
            search_range = range(
                Arch.dRegions['DM1RAM'][0], Arch.dRegions['DM1RAM'][1],
                Arch.addr_per_word
            )
        else:
            # DM1 and DM2 are distinct, need to check both
            search_range = itertools.chain(
                range(
                    Arch.dRegions['DM1RAM'][0], Arch.dRegions['DM1RAM'][1],
                    Arch.addr_per_word
                ),
                range(
                    Arch.dRegions['DM2RAM'][0], Arch.dRegions['DM2RAM'][1],
                    Arch.addr_per_word
                )
            )

        for addr in search_range:
            data = self.chipdata.get_data(addr)

            # Users of pmalloc get a pointer to the first word after the block header,
            # so correct for this when searching. I think it's fair to say that addresses
            # which are in the pool but not at the start of a block don't count.
            # (e.g. you couldn't use such a pointer to free the block).
            if (data - Arch.addr_per_word *
                    self.block_header_size in all_block_pointers):
                # Need to avoid picking up the free-list pointers at the start
                # of our own pmalloc block headers,
                # or in the memory pool control block itself. These aren't
                # valid references.
                if ((addr in free_block_pointers) or (addr >= self.pooldata.address and addr < (
                        self.pooldata.address + self.pooldata.size))):
                    continue

                block_num = (data - poolvar.address) / (
                    (
                        block_size + self.block_overhead_words
                    ) * Arch.addr_per_word
                )
                poolvar[block_num].owned = True

        # Now look at MMU buffer handles, if they exist. Sometimes we allocate a buffer and
        # the only reference to it is in a handle.
        # Buffer handles are volatile, so need to look this up every time.
        if Arch.chip_arch == "Hydra":
            buff_handles = self.chipdata.get_var_strict('L_mmu_buffer_handles')
            if Arch.kal_arch == 4:
                try:
                    buff_handles = self.chipdata.get_var_strict(
                        'L_mmu_buffer_handle_list'
                    )
                except ct.DebugInfoNoVariable:
                    pass
            for handle in range(buff_handles.array_len):
                if Arch.kal_arch == 4:
                    # in 32b/8b architectures words are octet addressable, no
                    # need for conversion
                    data = buff_handles[
                        handle
                    ].get_member('buffer_start_p').value
                else:
                    # in 24b/24b architectures words are mmu-words, 16-bit
                    data = (
                        buff_handles[handle].get_member('buffer_start_p').value
                    ) / 2
                if (data - Arch.addr_per_word *
                        self.block_header_size in all_block_pointers):
                    block_num = (data - poolvar[0].address) / (
                        (
                            block_size + self.block_overhead_words
                        ) * Arch.addr_per_word
                    )
                    poolvar[block_num].owned = True
        else:
            # Don't believe we need to consider stuff in the MCU here; there shouldn't be anything
            # that's only referenced from there.
            pass

        # Report any blocks which aren't free and don't have anything pointing
        # to them
        for i, blockvar in enumerate(poolvar.members):
            if (not blockvar.owned) and (not blockvar.free):
                pool_errors.append(
                    "Unowned block, Pool: {0:>2d} Block {1:>3d} Ptr: {2:0>6x}".
                    format(pool, i, blockvar.address)
                )

        return (
            tuple(pool_summary),
            tuple(pool_debug_info),
            tuple(pool_errors))

    def _check_oversize_allocations(self):
        """
        @brief Looks at the recorded oversize-allocation information
        @param[in] self Pointer to the current object
        """
        info = []
        try:
            oversize_count = self.chipdata.get_var_strict(
                'L_oversize_allocation_count'
            ).value
            info.append(
                "Oversize allocation count : {0:>d}".format(oversize_count)
            )
        except BaseException:
            info.append("Oversize allocation not available")

        return info
