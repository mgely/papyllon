defremove_array_zeros(x_array):
       #remove zeros for theta devision:
       nn = 0
       for i in x_array:
              if i == 0:
                  x_array[nn]=x_array[nn-1] #find and change zeros from x2_array
              nn+=1
return x_array
