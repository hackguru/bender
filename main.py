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
# adding all squares to equal themselves because they are binary
substitutes = {i**2:i for i in D.values()}

def InitialWallaceWeights(iName, i, jName, j, k):
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

    toReturn = []
    while iIndex>=0 and jIndex<j:
        toReturn.append("{}{}*{}{}".format(iName, iIndex, jName, jIndex))
        iIndex -= 1
        jIndex += 1

    return toReturn

equalities = [
    {
        D['a0']:1, # we assume a is odd - even can be calculated once we have odd
        D['n0']:1, # n is usually? semi-prime so it should be odd
        D['k0']:0,
        D['k1']:0,
        D['k2']:0,
    },
    {
        parse_expr('a1+a2'):parse_expr('2*a1*a2+((a1+a2)%2)'),
        parse_expr('k3'):parse_expr('(a1+a2)%2'),
    },
    {
        parse_expr('a2+a3'):parse_expr('2*a2*a3+((a2+a3)%2)'),
        parse_expr('k4 + n1*((a1 + a2)%2)'): parse_expr('2*k4*n1*((a1+a2)%2)+((k4 + n1*((a1 + a2)%2))%2)'),
        parse_expr('k4'):parse_expr('(((a2+a3)%2)+(n1*((a1+a2)%2)))%2'),
    },
]
#p = sympy.Wild('p')
#q = sympy.Wild('q')
updates = {
    #p+q: 2*p*q + ((p+q)%2),
}

leftSide = [parse_expr('+'.join(InitialWallaceWeights('a',n,'a',n,i))).subs(substitutes) for i in range(2*n-1)]
# moving one to left side and deduct
leftSide[0] = leftSide[0]-1
rightSide = [parse_expr('+'.join(InitialWallaceWeights('n',n,'k',n,i))).subs(substitutes) for i in range(2*n-1)]

def moveUpTwos(equ,index):
    argsToGoUp = list(filter(lambda x: x==2 or (type(x) is Mul and 2 in x.args), equ[index].args if equ[index].func is Add else (equ[index],)))
    if len(argsToGoUp) > 0:
        if index+1 >= len(equ):
            equ.append(parse_expr("0"))
        equ[index+1] = functools.reduce(lambda x,y: x + y/2, [equ[index+1]] + argsToGoUp) 
        equ[index] = functools.reduce(lambda x,y: x-y, [equ[index]] + argsToGoUp)

def reweighAndPrint(left,right):
    toPrint = []
    for j in equalities:
        for i in range(min(len(left), len(right))):
            left[i] = left[i].subs(j)
            moveUpTwos(left,i)
            right[i] = right[i].subs(j)
            moveUpTwos(right,i)
    for i in range(min(len(left),len(right))):
        if str(left[i]) != str(right[i]):
            toPrint.append(("w:{:>2}{:>"+str(math.floor(shutil.get_terminal_size((80, 20))[0]/2)-2-2)+"}").format(i,str(sympy.expand(left[i])))+" = "+str(sympy.expand(right[i])))
    print("\n".join(toPrint))

reweighAndPrint(leftSide, rightSide)
