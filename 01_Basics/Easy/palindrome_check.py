class Solution:
    def isPalindrome(self, x: int) -> bool:
        rev = 0 
        num = x
        while(num > 0):
            digit = num%10
            rev = ((rev *10) + digit)
            num = num // 10
        if(x == rev):
            return True
        else:
            return False
        pass
