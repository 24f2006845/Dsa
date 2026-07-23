from typing import List

class Solution:
    def bubbleSort(self, arr: List[int]) -> List[int]:
        n = len(arr)
        for i in range(n-2,-1,-1):
            is_swapped = False
            for j in range(0,i+1):
                if arr[j]>arr[j+1]:
                    arr[j],arr[j+1] = arr[j+1],arr[j]
                    is_swapped = True
            if is_swapped==False:
                break
        
        pass
