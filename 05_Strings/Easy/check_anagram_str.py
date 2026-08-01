class Solution:
    def frequency(self,s):
        dict ={}
        
        for ch in s:
            count = s.count(ch)
            dict[ch] = count
        return dict

    def isAnagram(self, s1, s2):
        freq1 = self.frequency(s1)
        freq2 = self.frequency(s2)

        if len(s1)==len(s2) and freq1 == freq2:
            return True
        else:
            return False
