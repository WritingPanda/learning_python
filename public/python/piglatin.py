def tryAgain():
	response = raw_input('Try another word? Y/N: ')
	response.lower()
	if response == 'y':
		piglatin()
	elif response == 'n':
		quit()
	else:
		print 'That is not a valid input. Please try again'
		tryAgain()

def piglatin():
	pyg = 'ay'

	original = raw_input('Enter a word: ')

	if len(original) > 0 and original.isalpha():
	    word = original.lower()
	    first = word[0]
	    new_word = word[1:] + first + pyg
	    print new_word
	    tryAgain()
	else:
	    print 'That is not a word. Try something different!'
	    piglatin()

piglatin()