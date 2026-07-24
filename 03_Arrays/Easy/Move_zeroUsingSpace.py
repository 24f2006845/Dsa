class Solution:
    def moveZeros(self, arr):
        # write your code here
        result =[]
        for num in arr:
            if num ==1:
                result.append(1)
        for num in arr:
            if num ==0:
                result.append(0)
        return result
