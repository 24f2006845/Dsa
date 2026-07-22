def greatestElementInarr(arr):
    greatest_element = max(arr)
    index = arr.index(greatest_element)
    print(f"Max element = {greatest_element} found at index {index}")

n = int(input())
arr = list(map(int, input().split()))

greatestElementInarr(arr)
