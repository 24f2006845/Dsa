from typing import List

class Solution:
    def selectionSort(self, arr: List[int]) -> List[int]:
        n = len(arr)
        for i in range(n):
            min_index = i
            for j in range(i+1,n):
                if arr[j]< arr[min_index]:
                    min_index = j
            arr[i],arr[min_index] = arr[min_index],arr[i]
        pass
