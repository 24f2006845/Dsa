class Solution:
    def bubbleSort(self,arr):
        n = len(arr)
        for i in range(n):
            isSwap = False
            for j in range(0,n-1):
                if arr[j]>arr[j+1]:
                    arr[j],arr[j+1]= arr[j+1],arr[j]
                    isSwap = True
            if not isSwap:
                break
