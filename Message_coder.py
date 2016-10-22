# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 17:39:03 2016

@author: Jiayi ZHENG
"""

# Problem 1 Write a function preceding that takes a single character as an input 
# and returns a code for that character
def preceding(x):
    '''This function takes a single character as an input, 
    and returns a code for that character.'''
    assert type(x)==str and len(x)==1, 'Please input a string of length 1'
    if x == 'a':
        return 'z'
    elif x == 'A':
        return 'Z'
    elif 98<=ord(x)<=122 or 66<=ord(x)<=90:
        return chr(ord(x)-1)
    else:
        return x

# Problem 2 Write a function succeeding that takes a single character as an input 
# and returns a code for that character 
def succeeding(x):
    '''This function takes a single character as an input, 
    and returns a code for that character.'''
    assert type(x)==str and len(x)==1, 'Please input a string of length 1'
    if x == 'z':
        return 'a'
    elif x == 'Z':
        return 'A'
    elif 97<=ord(x)<=121 or 65<=ord(x)<=89:
        return chr(ord(x)+1)
    else:
        return x

# Problem 3 Write a function message_coder that takes two arguments -
# a string and a function - and returns a coded message 
# that uses the function for coding each character in the string.
def message_coder(string, function):
    '''This function takes two arguments: a string and a function,
    and returns a coded message of that string using the function.'''
    result=''    
    for s in string:
        result+=function(s)
    return result
