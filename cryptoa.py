from copy import copy, deepcopy
import sys

class CspCryptoarithmatic:
    wordDict = {}
    variableSet = set() 
    varDomainDict = {}
    constraintsList = []
    assignmentDict = {} 
    infrencesList = []

    def __init__(self) -> None:
        #get input from user and create a set of variables
        self.wordDict['firstWord'] = sys.argv[1]
        self.wordDict['secondWord'] = sys.argv[2]
        self.wordDict['thirdWord'] = sys.argv[3]

        # craete a set of every char in words from user and create assignment of None for every variable
        for word in self.wordDict.values():
            for char in word:
                self.variableSet.add(char)

        if len(self.variableSet) > 10:
            raise ValueError('More then 10 unique letter, no solution')

        # create domain dictionary containing key: var, value: domain
        for var in self.variableSet:
            self.varDomainDict[str(var)] = [*range(0, 10)]

        #create constraints
        for var1 in self.variableSet:
            for var2 in self.variableSet:
                # remove redundent constraints-alldif constraint is commutative
                if var1 == var2 or self.findRedundentConstraints(var1, var2):
                    continue
                # allDiff constraint
                self.constraintsList.append([(var1, var2), lambda var1, var2: var1 != var2])

        # we will look at the sum as follows:
        # each column is a sum of:  
        # carry_i + var1_i + var2_i = carry_i+1 * 10 + var3_i
        # the carry over the first column is equal to 0, we will add to variable list
        longestWord = len(max(self.wordDict.values()))
        for i in range(longestWord+2):
            self.variableSet.add('carry_'+str(i))
            self.varDomainDict['carry_'+str(i)] = [0] if i==0 else [0,1]
        # number of column is the length of sum word
        # each var in the constraint that is empty will be equal to zero 
        # we will reduce the n-ry constraint to a binary constraint in the following way:
        # 
        # we will create a variable: 
        # SR_i = (var_k, carry_i)  
        # SL_i = (var_i, var_j)
        # 
        # we will create constraint for each variable:
        # (<SR_i, var_k>, SR_i[0]==var_k), 
        # (<SR_i, carr_i+1>, SR_i[1]==carry_i+1), domain: [(0,0),...,(9,0),(0,1),...,(9,1)]
        # (<SL_i, var_i>, SR_i[0]==var_i),
        # (<SL_i, var_j>, SR_i[1]==var_j), domain: [(0,0),...,(9,9)]
        # (<SR_i, SL_i>, SR_i==SL_i), domain: [(0,0),...,(9,9)]
        # 
        for i in range(longestWord+1):
            SR_i_str = 'SR_' + str(i)
            SLV_i_str = 'SLV_' + str(i)
            SL_i_str = 'SL_' + str(i)
            self.variableSet.add(SLV_i_str)
            self.variableSet.add(SL_i_str)
            self.variableSet.add(SR_i_str)

            # determine if char is valid or not
            try:
                charFirstWord = self.wordDict['firstWord'][i]
                domainRangeFirstWord = 10
            except:
                charFirstWord = 'firstWordNoCharAt_' + str(i) 
                domainRangeFirstWord = 1
                self.variableSet.add(charFirstWord)
                self.varDomainDict[charFirstWord] = [0]

            # determine if char is valid or not
            try:
                charSecondWord = self.wordDict['secondWord'][i]
                domainRangeSecondWord = 10
            except:
                charSecondWord = 'secondWordNoCharAt_' + str(i)
                domainRangeSecondWord = 1
                self.variableSet.add(charSecondWord)
                self.varDomainDict[charSecondWord] = [0]

            # set the domain to all possible cartesian in range 
            self.varDomainDict[SLV_i_str] = [(i,j) for i in range(domainRangeFirstWord) for j in range(domainRangeSecondWord)]

            # create SLV_i constraint: equal to left value of SLV_i = (var_i, var_j) 
            self.constraintsList.append([(SLV_i_str, charFirstWord), lambda SLV_i, var_i: SLV_i[0] == var_i])

            # create SLV_i constraint: equal to right value of SLV_i = (var_i, var_j)   
            self.constraintsList.append([(SLV_i_str, charSecondWord), lambda SLV_i, var_j: SLV_i[1] == var_j])

            # set domain to all possible cartesion in range
            self.varDomainDict[SL_i_str] = [(i,j) for i in range(2) for j in range(19)]

            # create SL_i constraont: equal to left value of SL_i = (carry_i, SLV_i)
            self.constraintsList.append([(SL_i_str, 'carry_'+str(i)), lambda SL_i, carry_i: SL_i[0] == carry_i])

            # create SL_i constraint: equal to right value of SL_i = (carry_i, SLV_i)
            self.constraintsList.append([(SL_i_str, SLV_i_str), lambda SL_i, SLV_i: SL_i[1] == SLV_i[0] + SLV_i[1]])

            # create equation constrain
            self.constraintsList.append([(SL_i_str, SR_i_str), lambda sl_i, sr_i: sl_i[0] + sl_i[1] == sr_i[0] + 10*sr_i[1]])

            try:
                char = self.wordDict['thirdWord'][i]
                if self.varDomainDict[charFirstWord] == [0] and self.varDomainDict[charSecondWord] == [0]:
                    self.varDomainDict[SR_i_str] = [(1,1)]
                else:
                    self.varDomainDict[SR_i_str] = [(i,j) for i in range(10) for j in range(2)]
            except:
                raise ValueError('Sum word is shorter then the elements')

            # set the domain to all possible cartesian in range 
            self.varDomainDict[SR_i_str] = [(i,j) for i in range(10) for j in range(2)]

            # create SRV_i constraint: equal to left value of SR_i = (var_k, carry_i+1)  
            self.constraintsList.append([(SR_i_str, char), lambda SR_i, var_k: SR_i[0] == var_k])

            # create SRV_i constraint: equal to right value of SR_i = (var_k, carry_i+1)  
            self.constraintsList.append([(SR_i_str, 'carry_'+str(i+1)), lambda SR_i, carry_i1: SR_i[1] == carry_i1])

            for var in self.variableSet:
                self.assignmentDict[var] = None 

        self.backtrackingSearch()

    def findRedundentConstraints(self, var1, var2) -> list:
        for i in range(len(self.constraintsList)):
            if (var2, var1) == self.constraintsList[i][0]:
                return True
        return False


    def neighborsOf(self, y) -> list:
        neighborsList = []
        
        for i in range(len(self.constraintsList)):
            if y in self.constraintsList[i][0]:
                neighborsList.append(self.constraintsList[i][0])
        return neighborsList

    def revise(self, x, y) -> bool:
        revised = False
        
        print('checking cons:({},{})'.format(x,y))
        for dx in self.varDomainDict[x]:
            constraintXY = self.findConstraint(x, y)
            # if no constranin found
            if not constraintXY:
                continue

            if not any(constraintXY(dx, dy) for dy in self.varDomainDict[y]):
                print('removing item:{}'.format(dx))
                self.varDomainDict[x].remove(dx)
                revised = True
        return revised

    def findConstraint(self, dx, dy):
        for i in range(len(self.constraintsList)):
            if self.constraintsList[i][0] == (dx, dy):
                return self.constraintsList[i][1]

    def ac3(self, assignedVar):
        # queue = []

        # # create arc queue
        # for constraint in self.constraintsList:
        #         if constraint[0][0] == constraint[0][1]: continue
        #         queue.append(deepcopy(constraint[0]))

        queue = self.neighborsOf(assignedVar)
        # while queue is not empty 
        while len(queue) > 0:
            # poping from start of the list(not relying on external python modules)
            x,y = queue.pop(0)

            if self.revise(x, y):
                # if domain empty
                print('revied:{}\n domain:{}'.format(x, self.varDomainDict[x]))
                if len(self.varDomainDict[x]) == 0:
                    self.infrencesList = []
                    return False

                # add neighbors to queue
                for xNeighbors in self.neighborsOf(y):
                    if x in xNeighbors: continue
                    print("addin to queue:{}".format(xNeighbors))
                    queue.append(xNeighbors)
        return True

    def backtrack(self) -> bool:
        if self.assignmentComplete(): return self.assignmentDict
        var = self.minimumRemainingValues()

        for value in self.leastConstrainingValue(var):
            if self.consistent(value):
                self.assignmentDict[var] = value
                ac3Pass = self.ac3(var)
                if ac3Pass:
                    if self.backtrack(): return True
                    self.infrencesList = []
                self.assignmentDict.remove(var)
        self.printState()
        return False
    

    def assignmentComplete(self) -> bool:
        for var in self.variableSet:
            if self.assignmentDict[var] == None: return False
        return True


    def leastConstrainingValue(self, var) -> list:
        # pick the least constraining value 
        sumValuesDict = {}
        for neighbor in self.neighborsOf(var):
            sumValuesDict[neighbor[1]] = len(self.varDomainDict[neighbor[1]])

        return max(sumValuesDict, key = lambda x:sumValuesDict[x])


    def minimumRemainingValues(self):
        minDomain = None
        minVar = None

        for var, domain in self.varDomainDict.items():
            if not minVar:
                minVar = var
                minDomain = len(domain)
                continue
            
            if minDomain > len(domain):
                minVar = var
                minDomain = len(domain)
        return var 


    def consistent(self, value) -> bool:
        for assVal in self.assignmentDict.values():
            if assVal == value:
                return False
        return True



    def printState(self):
        for var in self.variableSet:
            print(var)
        print()

        for k,v in self.varDomainDict.items():
            print(k,v)
        
        print()
        for i in range(len(self.constraintsList)):
            print(self.constraintsList[i])

    def backtrackingSearch(self):
        return self.backtrack()

if __name__ == '__main__':
    CspCryptoarithmatic()

    # # create carry variables
    # for carry in range(len(max(sys.argv[1],
    #                             sys.argv[2],
    #                             sys.argv[3]) + 1)): 
    #     var = 'c' + str(carry)
    #     variableSet.add(var)
    #     varDomainDict[var] = [0, 1]

    # additionEq = (sys.argv[1], sys.argv[2], sys.argv[3])
    # # find the shortest word lenth
    # minLengh = min([len(term) for term in additionEq])

    # # create constraints for equation
    # for i in range(minLengh):
    #     # create constraints for terms addition
    #     if i <= minLengh:
    #         constraintsList.append([
    #             ('c'+str(i), sys.argv[1][i], sys.argv[2][i], sys.argv[3][i], 'c'+str(i)), 
    #          lambda var1, var2, var3, var4, var5: var1 + ((var2 + var3) % 10) == var4 + 10*var5
    #          ])

    #         constraintsList.append([])

    # # constraint for variable if sum of two number is greater then their length
    # if len(sys.argv[3]) > minLengh:
    #     constraintsList.append([(sys.argv[3][0]), lambda var1: var1 == 1])

   