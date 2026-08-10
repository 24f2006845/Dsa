class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        window  = sum(nums[:k])
        left = 0
        right = k-1
        max_sum = window
        while right < len(nums)-1:
            
            window = window - nums[left]
            left+=1
            right+=1
            window = window + nums[right]
            max_sum = max(max_sum , window)
        return max_sum/k
