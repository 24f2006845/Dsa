class Solution:
    def sortArrayByParity(self, nums: List[int]) -> List[int]:
        n = len(nums)
        j=0
        for i in range(n):
           
           if nums[i]%2==0:
              nums[i],nums[j]=nums[j],nums[i]
              j+=1
        
            

        return nums
