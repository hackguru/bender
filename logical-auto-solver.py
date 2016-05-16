#!/usr/bin/env python3

# solving a**2 = k*n+1

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import sys
import math
import sympy
import functools
import shutil
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.mul import Mul
from sympy.core.add import Add
from sympy.logic.boolalg import to_cnf

shouldSubN = True
shouldSolve = True

N = int(input("Number to factorize: "))

n = math.floor(math.log2(float(N)))+1

mainSymbols = "akn"
D = {"{}{}".format(i,j): sympy.Symbol("{}{}".format(i,j)) for i in mainSymbols for j in range(n)}
n_Subs = {D["n{}".format(bit)]: (N >> bit) & 1 for bit in range(n - 1, -1, -1)}
# n is usually? semi-prime so it should be odd
if n_Subs[D["n0"]] == False:
    print("Only odd numbers - well semi-prime - please")
    sys.exit()

def InitialWallaceWeights(iName, i, jName, j, k, toAdd, leftOvers):
	if k>i+j-1 or k<0 :
		raise IndexError("range of index can only be from 0 to {}".format(i+j-1))

	if i<j :
		i,j = j,i

	iIndex = 0
	jIndex = 0
	if k >= i:
		iIndex = i-1
		jIndex = (k % i) + 1
	else:
		iIndex = k

	toReturn = []+toAdd
	if k==i+j-1:
	    return toReturn
	while iIndex>=0 and jIndex<j:
		toReturn.append(parse_expr("{}{}&{}{}".format(iName, iIndex, jName, jIndex)))
		iIndex -= 1
		jIndex += 1

	interim = []+toReturn
	count = len(interim)
	while count>1:
		nextInterim=[]
		for l in range(0,count,3):
			if l+2<count:
				leftOvers.append(((interim[l]^interim[l+1])&interim[l+2])|(interim[l]&interim[l+1]))
				nextInterim.append(interim[l]^interim[l+1]^interim[l+2])
			elif l+1<count:
				leftOvers.append(interim[l]&interim[l+1])
				nextInterim.append(interim[l]^interim[l+1])
			else:
				nextInterim.append(interim[l])
		interim = nextInterim
		count = len(interim)
	return toReturn

leftSideKnowns = {
	D['a0']:True, # we assume a is odd - even can be calculated once we have odd
}
rightSideKnowns = {
	D['n0']:True, # if we substitute n or not it always will be odd so we might as well
}
substitutes = {
}
equations = []
toAddToLeftSide=[]
toAddToRightSide=[]
satEquation = True 
i = 0
while i < 2*n:
	leftSideLeftOvers=[]
	leftSide = sympy.simplify_logic(functools.reduce(lambda x,y:x^y, [False]+InitialWallaceWeights('a',n,'a',n,i,toAddToLeftSide,leftSideLeftOvers)).subs(leftSideKnowns))
	# EXCEPTION - MOVING -1 TO LEFT SIDE OF EQUATION TO SUBTRACT:
	if i==0:
		leftSide ^= 1
	leftSideLeftOvers = [sympy.simplify_logic(leftOverTerm.subs(leftSideKnowns)) for leftOverTerm in leftSideLeftOvers]
	
	rightSideLeftOvers=[]
	rightSide = functools.reduce(lambda x,y:x^y, [False]+InitialWallaceWeights('n',n,'k',n,i,toAddToRightSide,rightSideLeftOvers)).subs(rightSideKnowns).subs(substitutes)
	rightSideLeftOvers = [rightSideTerm.subs(rightSideKnowns).subs(substitutes) for rightSideTerm in rightSideLeftOvers]
	# replacing n digits
	if shouldSubN:
	    rightSide = rightSide.subs(n_Subs)
	    rightSideLeftOvers = [rightSideTerm.subs(n_Subs) for rightSideTerm in rightSideLeftOvers]
	
	toAddToLeftSide = leftSideLeftOvers
	toAddToRightSide = rightSideLeftOvers
	
	equations.append((leftSide,rightSide))
	
	# adding new term to equalitis for new k
	newKkey = 'k{}'.format(len(equations)-1)
	if newKkey in D:
		substitutes[D[newKkey]] = equations[-1][0]^sympy.simplify_logic(equations[-1][1]^D[newKkey])
	else:
		satEquation = sympy.Equivalent(equations[-1][0],sympy.simplify_logic(equations[-1][1])) & satEquation
	print((bcolors.HEADER+"w:{:>2}"+bcolors.ENDC+" {:>"+str(math.floor(shutil.get_terminal_size((80,20))[0]/2)-2-3)+"}").format(i,sympy.pretty(equations[-1][0]))+bcolors.OKGREEN+" = "+bcolors.ENDC+sympy.pretty(equations[-1][1]))
	i += 1 

#print("number of terms in CNF for satisfiability: {}".format(len(to_cnf(satEquation.args))))

if shouldSubN & shouldSolve:
    print("=======Sat Equation=======")
    simplifiedSat = sympy.simplify_logic(satEquation)
    print(simplifiedSat)
    print("=Satisfiability solutions=")
    allModels = list(sympy.satisfiable(simplifiedSat,all_models=True))
    print(", ".join(map(str,[2*functools.reduce(lambda x,y:2*x+y, [0]+[int(model[D[x]]) for x in ["a{}".format(i+1) for i in reversed(range(n-1))]])+1 for model in allModels])))
