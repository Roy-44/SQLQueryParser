def isAttribute(attribute, tablesInUse):
    if "." not in attribute:
        return False

    table = attribute.split(".")[0].strip()
    tableAttribute = attribute.split(".")[1].strip()

    if table == "Customers" and (tableAttribute == "Name" or tableAttribute == "Age") and table in tablesInUse:
        return True

    if table == "Orders" and \
            (tableAttribute == "CustomerName" or tableAttribute == "Product" or tableAttribute == "Price") and \
            table in tablesInUse:
        return True

    return False


def isSelectParseableAux(selectAttributes, tablesInUse):
    if len(selectAttributes) == 1:
        return isAttribute(selectAttributes[0].strip(), tablesInUse)

    currentAttribute = selectAttributes[0].strip()
    selectAttributes.pop(0)

    return isAttribute(currentAttribute, tablesInUse) and isSelectParseableAux(selectAttributes, tablesInUse)

def isSelectParseable(selectAttributes, tablesInUse):
    firstWord = selectAttributes.split()[0].strip()
    if firstWord == "DISTINCT":
        if len(selectAttributes.split("DISTINCT")) < 2:
            return False

        selectAttributes = selectAttributes.split("DISTINCT")[1].strip()

    if len(selectAttributes) == 0:
        return False

    selectAttributes = selectAttributes.split(",")

    if len(selectAttributes) == 1 and selectAttributes[0].strip() == "*":
        return True

    return isSelectParseableAux(selectAttributes, tablesInUse)


def isTable(table, tablesInUse):
    if table == "Customers" or table == "Orders":
        if table not in tablesInUse:
            tablesInUse.append(table)
        return True

    return False


def isFromParseableAux(fromTables, tablesInUse):
    if len(fromTables) == 1:
        return isTable(fromTables[0].strip(), tablesInUse)

    currentTable = fromTables.pop(0).strip()

    return isTable(currentTable, tablesInUse) and isFromParseableAux(fromTables, tablesInUse)


def isFromParseable(fromTables, tablesInUse):
    fromTables = fromTables.split(",")
    if len(fromTables) < 1:
        return False

    return isFromParseableAux(fromTables, tablesInUse)


def isConstant(constant, tablesInUse):
    if constant.startswith("\"") and constant.endswith("\""):
        return True

    if constant.startswith("'") and constant.endswith("'"):
        return True
    
    if constant.isnumeric():
        return True
    
    return isAttribute(constant, tablesInUse)


def splitByRel(whereConditions, rel):
    return whereConditions.split(rel)


def isAtributesAreSameType(constant1, constant2):
    if (constant1.split(".")[1] == "Name" or constant1.split(".")[1] == "CustomerName" or
            constant1.split(".")[1] == "Product") \
            and (constant2.split(".")[1] == "Name" or constant2.split(".")[1] == "CustomerName"
                 or constant2.split(".")[1] == "Product"):
        return True
    elif (constant1.split(".")[1] == "Age" or constant1.split(".")[1] == "Price") and\
        (constant2.split(".")[1] == "Age" or constant2.split(".")[1] == "Price"):
        return True
    return False

def isSameType(constant1, constant2, tableInUse):
    if isAttribute(constant1,tableInUse) and isAttribute(constant2,tableInUse):
        return isAtributesAreSameType(constant1,constant2)
    if isAttribute(constant1, tableInUse):
        if (constant1.split(".")[1] == "Name" or constant1.split(".")[1] == "CustomerName" or
            constant1.split(".")[1] == "Product")\
                and (constant2.startswith("\"") and constant2.endswith("\"")
                     or constant2.startswith("'")and constant2.endswith("'")):
            return True
        if (constant1.split(".")[1] == "Age" or constant1.split(".")[1] == "Price") and constant2.isnumeric():
            return True
    elif isAttribute(constant2, tableInUse):
        if (constant2.split(".")[1] == "Name" or constant2.split(".")[1] == "CustomerName" or
            constant2.split(".")[1] == "Product")\
                and (constant1.startswith("\"") and constant1.endswith("\"")
                     or constant1.startswith("'")and constant1.endswith("'")):
            return True
        if (constant2.split(".")[1] == "Age" or constant2.split(".")[1] == "Price") and constant1.isnumeric():
            return True
    if constant1.isnumeric() and constant2.isnumeric():
        return True
    if ((constant1.startswith("\"") and constant1.endswith("\"")) or
        (constant1.startswith("'") and constant1.endswith("'"))) and\
            ((constant2.startswith("\"") and constant2.endswith("\"")) or
             (constant2.startswith("'") and constant2.endswith("'"))):
        return True
    return False

def isSimpleCondition(whereConditions, tablesInUse):
    relStartIndex = whereConditions.find("<>")
    if relStartIndex != -1:
        constantsList = splitByRel(whereConditions, "<>")
    else:
        relStartIndex = whereConditions.find("<=")
        if relStartIndex != -1:
            constantsList = splitByRel(whereConditions, "<=")
        else:
            relStartIndex = whereConditions.find(">=")
            if relStartIndex != -1:
                constantsList = splitByRel(whereConditions, ">=")
            else:
                relStartIndex = whereConditions.find("<")
                if relStartIndex != -1:
                    constantsList = splitByRel(whereConditions, "<")
                else:
                    relStartIndex = whereConditions.find(">")
                    if relStartIndex != -1:
                        constantsList = splitByRel(whereConditions, ">")
                    else:
                        relStartIndex = whereConditions.find("=")
                        if relStartIndex != -1:
                            constantsList = splitByRel(whereConditions, "=")
                        else:
                            return False

    if len(constantsList) < 2:
        return False

    if isConstant(constantsList[0].strip(), tablesInUse) and isConstant(constantsList[1].strip(), tablesInUse) and \
        isSameType(constantsList[0].strip(), constantsList[1].strip(), tablesInUse):
        return True

    return False


def getConditionCloseIndex(whereConditions, bracketsStartIndex):
    bracketsCounter = 0
    index = -1
    for ch in whereConditions:
        index = index + 1
        if ch == "(":
            bracketsCounter = bracketsCounter + 1
        elif ch == ")":
            bracketsCounter = bracketsCounter - 1

        if bracketsCounter == 0:
            return index

    return False


def getANDOrORFinishIndex(whereConditions, conditionCloseIndex):
    simplifiedString = whereConditions[conditionCloseIndex:].strip()
    if simplifiedString.startswith("AND "):
        return whereConditions.find("AND ") + 4

    if simplifiedString.startswith("OR "):
        return whereConditions.find("OR ") + 3

    return False

def getNextOperatorIndex(conditionsStringToCheck):
    orIndex = conditionsStringToCheck.find("OR")
    andIndex = conditionsStringToCheck.find("AND")

    if orIndex < 0 or andIndex < 0:
        return max(orIndex, andIndex)

    return min(orIndex, andIndex)


def getoperatorsStartIndexesList(whereConditions):
    operatorsStartIndexesList = []
    passedIndexes = 0
    conditionsStringToCheck = whereConditions[:]
    while conditionsStringToCheck.find("OR") != -1 or conditionsStringToCheck.find("AND") != -1:
        nextOperatorIndex = getNextOperatorIndex(conditionsStringToCheck)
        operatorsStartIndexesList.append(nextOperatorIndex + passedIndexes)
        if conditionsStringToCheck[nextOperatorIndex] == 'O':
            conditionsStringToCheck = conditionsStringToCheck[nextOperatorIndex + 2:]
            passedIndexes += nextOperatorIndex + 2
        else:
            conditionsStringToCheck = conditionsStringToCheck[nextOperatorIndex + 3:]
            passedIndexes += nextOperatorIndex + 3

    return operatorsStartIndexesList


def isWhereParseable(whereConditions, tablesInUse):
    if whereConditions.startswith("(") and whereConditions.endswith(")"):
        isValidCondition = isWhereParseable(whereConditions[1:-1].strip(), tablesInUse)

        if isValidCondition:
            return True

    operatorsStartIndexesList = getoperatorsStartIndexesList(whereConditions)
    if len(operatorsStartIndexesList) == 0:
        return isSimpleCondition(whereConditions.strip(), tablesInUse)

    for index in operatorsStartIndexesList:
        if whereConditions[index] == 'O':
            isValidCondition = isWhereParseable(whereConditions[0:index].strip(), tablesInUse) and\
                               isWhereParseable(whereConditions[index + 2:].strip(), tablesInUse)
        else:
            isValidCondition = isWhereParseable(whereConditions[0:index].strip(), tablesInUse) and\
                               isWhereParseable(whereConditions[index + 3:].strip(), tablesInUse)

        if isValidCondition:
            return True

    return False

def main():
    query = input().strip()
    tablesInUse = []

    if not query.endswith(";"):
        print("Parsing failed because ';' is missing")
        return

    selectAttributes = query.split("SELECT")[1].split("FROM")[0].strip()
    fromTables = query.split("FROM")[1].split("WHERE")[0].strip()
    whereConditions = query.split("WHERE")[1].split(";")[0].strip()

    isFromValid = isFromParseable(fromTables, tablesInUse)
    isSelectValid = isSelectParseable(selectAttributes, tablesInUse)
    isWhereValid = isWhereParseable(whereConditions, tablesInUse)

    if isSelectValid == False:
        print("Parsing <attribute_list> failed")

    if isFromValid == False:
        print("Parsing <table_list> failed")

    if isWhereValid == False:
       print("Parsing <condition> failed")

    if isSelectValid and isFromValid and isWhereValid:
       print("Valid Query")


if __name__ == '__main__':
    main()