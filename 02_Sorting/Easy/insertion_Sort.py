from typing import List

class Solution:
    def insertionSort(self, arr: List[int], n: int) -> List[int]:
       n = len(arr)
       for i in range(1,n):
            key = arr[i]
            j = i-1
            while j>=0 and arr[j]>key :
                arr[j+1] = arr[j]
                j-=1
            arr[j+1] = key
