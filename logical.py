#!/usr/bin/env python3

# solving a**2 = k*n+1

import math
import sympy
import functools
import shutil
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.mul import Mul
from sympy.core.add import Add

N = input("Number to factorize: ")

n = math.floor(math.log2(float(N)))+1

mainSymbols = "akn"
D = {"{}{}".format(i,j): sympy.Symbol("{}{}".format(i,j)) for i in mainSymbols for j in range(n)}

def InitialWallaceWeights(iName, i, jName, j, k, toAdd, leftOvers):
	if k>=i+j-1 or k<0 :
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
				nextInterim.append(interim[l]^interim[l+1])
			elif l+1<count:
				leftOvers.append(interim[l]&interim[l+1])
				nextInterim.append(interim[l]^interim[l+1])
			else:
				nextInterim.append(interim[l])
			interim = nextInterim
			count = len(interim)
	#print("Run {}:".format(k))
	#print(toAdd)
	#print(toReturn)
	#print(leftOvers)
	return toReturn

equalities = [
	{
		D['a0']:True, # we assume a is odd - even can be calculated once we have odd
		D['n0']:True, # n is usually? semi-prime so it should be odd
		D['k0']:False,
	},
	{
		D['k1']:False,
    },
	{
		D['k2']:False,
	},
	{
		D['k3']:parse_expr('a1|a2'),
	},
	{
		D['k4']:parse_expr('((a1|~a3)&(a2|a3)&(a3|~a1))^(n1&(a1|a2))'),
	},
	{
	},
]
#p = sympy.Wild('p')
#q = sympy.Wild('q')
updates = {
	#p+q: 2*p*q + ((p+q)%2),
}
equations = []
def reweighAndPrint():
	toPrint = []
	toAddToLeftSide=[]
	toAddToRightSide=[]
	for i in range(len(equalities)):
		leftSideLeftOvers=[]
		leftSide = functools.reduce(lambda x,y:x^y, [False]+InitialWallaceWeights('a',n,'a',n,i,toAddToLeftSide,leftSideLeftOvers))
		# EXCEPTION - MOVING -1 TO LEFT SIDE OF EQUATION TO SUBTRACT:
		if i==0:
			leftSide ^= 1
		#print("left side:")
		#print(leftSide)
		rightSideLeftOvers=[]
		rightSide = functools.reduce(lambda x,y:x^y, [False]+InitialWallaceWeights('n',n,'k',n,i,toAddToRightSide,rightSideLeftOvers))
		#print("right side")
		#print(rightSide)
		for j in equalities[:i+1]:
			leftSide = leftSide.subs(j)
			rightSide = rightSide.subs(j)
		toAddToLeftSide = leftSideLeftOvers
		toAddToRightSide = rightSideLeftOvers
		equations.append((leftSide,rightSide))
	for i,j in enumerate(equations):
		if str(sympy.simplify_logic(j[0])) != str(sympy.simplify_logic(j[1])):
			toPrint.append(("w:{:>2}{:>"+str(math.floor(shutil.get_terminal_size((80,20))[0]/2)-2-2-10)+"}").format(i,sympy.prety(sympy.simplify_logic(j[0])))+" = "+sympy.pretty(sympy.simplify_logic(j[1])))
	print("\n".join(toPrint))
	#print(sympy.simplify_logic(sympy.Equivalent(equations[-1][0],equations[-1][1])))
	#print("Stisafiable models:")
	#print("\n".join(map(str,list(sympy.satisfiable(sympy.Equivalent(equations[-1][0],equations[-1][1]),all_models=True)))))
reweighAndPrint()
