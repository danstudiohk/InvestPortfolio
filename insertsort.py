def insertSort(arr):
	print('old: ',arr)
	for i in range(1, len(arr)):
		key = arr[i]
		j = i-1
		while j >=0 and key < arr[j]:
			arr[j+1] = arr[j]
			j -= 1
		arr[j+1]=key
		print('#',i,':',arr)
	print('new: ',arr)

arr = [12, 1, 13, 5, 6] 
insertSort(arr) 