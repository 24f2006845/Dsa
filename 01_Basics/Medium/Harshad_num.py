# helper.py

class Solution:
    def Sum_Of_Digit(self,num):
        sum = 0
        if(num == 0):
            return 0
        else:
            while num > 0:
                digit = num%10
                sum += digit
                num //= 10 
        return sum 



    def checkHarshad(self, n):
        # write your code here
        harshad_check_num = self.Sum_Of_Digit(n)
        if(harshad_check_num ==0):
            return "Not Harshad Number"
        if(n % harshad_check_num == 0):
            return "Harshad Number"
        else:
            return "Not Harshad Number"
