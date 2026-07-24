class Solution:

    def moveZeros(self, arr):
        # write your code here
        j = 0
        n = len(arr)
        for i in range(n):
            if arr[i]!=0:
                arr[j],arr[i]=arr[i],arr[j]
                j+=1
        return arr
