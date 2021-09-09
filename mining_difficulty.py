# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 10:08:52 2021

@author: prana
"""

# 403,200 - NEW TARGET
# 403,199              | last block
#                      |
#                      |
#                      |
# 401,184 - NEW TARGET | first block (target = 0x000000000000000006f0a8000000000000000000000000000000000000000000)

# 1. Get the timestamps for the first and last block in the target adjustment period
first = 1457133956 # block 401,184
last  = 1458291885 # block 403,199

# 2. Work out the ratio of the actual time against the expected time
actual = last - first     # 1157929 (number of seconds between first and last block)
expected = 2016 * 10 * 60 # 1209600 (number of seconds expected between 2016 blocks)
ratio = float(actual) / float(expected)

# 3. Limit the adjustment by a factor of 4 (to prevent massive changes from one target to the next)

ratio = max(ratio , 0.25)
ratio = min(ratio,4)

# 4. Multiply the current target by this ratio to get the new target
current_target = 0x000000000000000006f0a8000000000000000000000000000000000000000000
new_target = (current_target * ratio)

# 5. Don't let the target go above the maximum target
max_target = 0x00000000ffff0000000000000000000000000000000000000000000000000000
if new_target > max_target:
    new_target = max_target 

# 5. Truncate the target, because the official target is the truncated "bits" format stored in the block header
# This code is a bit rough, because it's working with strings when I should really be working with actual bytes.
new_target = hex(int(new_target)) # convert from decimal to hexadecimal



if len(new_target) % 2!=0:
    new_target = '0' + new_target
    
truncated = new_target.scan(/../).each_with_index.map { |byte, i| byte = i >= 3 ? "00" : byte }.join # set all bytes apart from first 3 to zeros
truncated = [(new_target[i:i+2]) for i in range(0, len(new_target), 2)]

for i in range(0,len(truncated)):
    if i>=3 :
        truncated[i] = "00"
        
truncated = "".join(truncated)
# e.g. 6a4c316c01f354000000000000000000000000000000000 <- full precision
# e.g. 6a4c3000000000000000000000000000000000000000000 <- official target

# 6. Display the full target (with leading zeros)
target = truncated.rjust(64, '0')

print(target)
# 000000000000000006a4c3000000000000000000000000000000000000000000