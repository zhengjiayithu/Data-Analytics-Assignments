# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 16:58:50 2016

@author: Jiayi ZHENG
"""

def word_distribution(text_string, word_list=None, case=0, proportion=0):
    from operator import itemgetter
    #check the arguments
    assert case==0 or case==1, "The argument 'case' must be 0 or 1"
    assert proportion==0 or proportion==1, "The argument 'proportion' must be 0 or 1"
    # Empty word_list    
    new_words = []
    word_dict_1 = {}
    word_dict = {}
    # Split text_string    
    try:
        words = text_string.split()
    except:
        print("The argument 'text_string' should be a string")
        raise Exception
    for word in words:
        if word[-1].isalpha():
            new_words.append(word)
        else:
            new_words.append(word[:-1])
#==============================================================================
#     """
#     Here I didn't take into consideration the situation that a word ends with number.
#     Correct solution:    
#     """
#     def remove_punctuation(word):
#     if word and ((word[-1] >= 'a' and word[-1]<='z') or (word[-1] >= 'A' and word[-1]<='Z')):
#         return word
#     elif word:
#         return word[:-1]
#     else:
#         return word
#==============================================================================
    # Count the words
    for word in new_words:
        word_dict_1[word]=word_dict_1.get(word,0)+1
    # Deal with the 'case' argument - convert string into lower case when case=0
    if case==0:
        word_dict_2 = {k.lower(): word_dict_1.get(k.lower(),0)+word_dict_1.get(k.capitalize(),0) for k in word_dict_1.keys()}
        if word_list != None:
            word_list = [x.lower() for x in word_list]
    else:
        word_dict_2 = word_dict_1
    # Deal with the 'proportion' argument
    if proportion==0:
        word_dict = word_dict_2
    else:
        total=sum(word_dict_2.values())
        for word in word_dict_2.keys():
            word_dict[word]=100*word_dict_2.get(word)/total
    # Deal with the 'case' argument - delete words that do not start with
    # an uppercase letter when case=1
    if case==1:
        word_dict_copy = dict(word_dict)
        for word in word_dict_copy.keys():
            if not word[0].isupper():
                del word_dict[word]
    # Deal with the 'word_list' argument
    if word_list == None:
        result = word_dict
    # an empty list
    elif len(word_list)==0:
        return {}        
    # an unempty list            
    else:            
        result={word: word_dict.get(word,0) for word in word_list}
    # Return the result              
    return result
    
#==============================================================================
# # Solution:
# #Write a function to remove punctuation if the last character is not a letter of the alphabet
# #Note that we're making an assumption here that the last char should be a..z or A..Z
# # 123a will be counted as a word in our program
# # as also will be 123
# #Note that we're treating an empty word_list as equivalent to None. 
# def remove_punctuation(word):
#     if word and ((word[-1] >= 'a' and word[-1]<='z') or (word[-1] >= 'A' and word[-1]<='Z')):
#         return word
#     elif word:
#         return word[:-1]
#     else:
#         return word
#     
# def word_distribution(text_string,case=0,word_list=None,proportion=0):
#     word_count = 0
#     word_dict = dict()
#     for word in text_string.split():
#         word = remove_punctuation(word)  #Remove punctuation at end of word
#         if not word: continue #Ignore non-words (empty strings)
#         if not case: word = word.lower() #if case=0, make the word lower
#         word_count +=1 #keep track of total number of words (this must come after the case check)
#         if case and not (word[0] >='A' and word[0]<='Z'): continue #if case=1 ignore non-uppercase words
#         if word_list and not case: word_list = [x.lower() for x in word_list] #if case=0, make word_list lower
#         if word_list and not word in word_list: continue #if word_list, ignore non word_list words
#         if word in word_dict: #Update word occurrence count
#             word_dict[word]+=1
#         else:
#             word_dict[word]=1
#     if word_list: #if word_list, add back missing words
#         for word in word_list:
#             if not word in word_dict: word_dict[word] = 0
#     if proportion: #if proportion, calculate proportions
#         word_dict = {key:word_dict[key]/word_count for key in word_dict.keys()}
#         
#     return word_dict    #return the word dict
#==============================================================================
