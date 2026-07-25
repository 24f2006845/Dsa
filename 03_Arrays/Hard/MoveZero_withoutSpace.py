
class Solution:

    def moveZeros(self, arr):
        # write your code here
        j=0
        n = len(arr)
        for i in range(n):
            if arr[i]!=0:
                arr[i],arr[j] = arr[j],arr[i]
                j+=1
        return arr
