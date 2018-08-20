def singleNumber(nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    res = 0
    for i in nums:
        res ^= i
        print res
    print 'res is',res
    return res
num = [2,2,3,3,4,4,5]
singleNumber(num)