class Solution:
    def sortColors(self, nums: List[int]) -> None:
     low = 0
     i = 0
     high = len(nums)-1
     while i<=high:
        if nums[i]==0:
            nums[i],nums[low]=nums[low],nums[i]
            i+=1
            low+=1
        elif nums[i]==1:
            i+=1
        else:
            nums[i],nums[high]=nums[high],nums[i]
            high-=1
