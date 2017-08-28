#   ######################################
#   |     CSDL - CSV Parser v1.0.0       |
#   |      Written by Joe Bremner        |
#   |              Dell                  |
#   ######################################

from modgrammar import *
import argparse

grammar_whitespace_mode = 'optional'

commandParser = argparse.ArgumentParser(description='Convert a CSDL schema to CSV to be opened as a spreadsheet.')
commandParser.add_argument('filename', metavar='F', type=str, help='The name of the schema file.')
args = commandParser.parse_args()

print("Running...")
testFile = open(args.filename)
fileString = testFile.read()


### remove_comments()
# - takes string as input
# - returns input with removed comments
# - included this to counteract infinite left-recursion bug with Modgrammar
##
def remove_comments(fileString):
    newString = ''
    insideComment = False
    for i in range(0, len(fileString)):
        # print(fileString[i:i+4])
        if fileString[i:i+4] == '<!--':
            insideComment = True
        elif fileString[i-3:i] == '-->':
            insideComment = False

        if insideComment == False:
            newString += fileString[i]

    return newString


newFileString = remove_comments(fileString)
print(newFileString)
print("XML comments removed.")

# Grammar #

### PropertyValue (CSDL)
# - grammar consists of 5 total tokens
# - token [1] indicates the string content of the property value
# - token [3] indicates the boolean value of the property value
##
class PropertyValue (Grammar):
    grammar = ('<PropertyValue Property="', WORD('A-Za-z0-9'), '" Bool="', WORD('a-z'), '"/>')


### Annotation (CSDL)
# - grammar consists of 7 total tokens
# - token [1] indicates the term of the annotation (ex. OData.Permissions)
# - token [3] indicates the data type of the annotation (ex. EnumMember)
# - token [5] indicates the value of the annotation (ex. OData.Permission/Read)
##
class Annotation (Grammar):
    grammar = ('<Annotation Term="', WORD('A-Za-z0-9.'), '"', OPTIONAL(WORD('A-Za-z')), OPTIONAL('="'), OPTIONAL(WORD('A-Za-z0-9/. ()[],-\;')), OPTIONAL('"'), '/>')


### Record (CSDL)
# - grammar consists of 3 total tokens
# - token [1] indicates an exhaustive list of the record's property values and annotations
##
class Record (Grammar):
    grammar = ('<Record>', REPEAT(OR(PropertyValue, Annotation)), '</Record>')


### NestedAnnotation (CSDL)
# - grammar consists of 5 total tokens
# - token [1] indicates the term of the annotation
# - token [3] indicates an exhaustive list of the annotation's records
##
class NestedAnnotation (Grammar):
    grammar = ('<Annotation Term="', WORD('A-Za-z0-9.'), '">', REPEAT(Record), '</Annotation>')


### Property (CSDL)
# - grammar consists of 7 total tokens
# - token [1] indicates the name of the property (ex. Manufacturer)
# - token [3] indicates the type of the property (ex. Edm.String)
# - token [5] *may* indicate the "Nullable" keyword being set to "False"; otherwise set to None
# - token [7] indicates an exhaustive list of the property's annotations and XML comments
##
class Property (Grammar):
    grammar = ('<Property Name="', WORD('A-Za-z0-9'), '" Type="', WORD('A-Za-z0-9._'), '"', OPTIONAL(L('Nullable="false"')), '>', REPEAT(Annotation), '</Property>')


### StatusProperty (CSDL)
# - grammar consists of 1 total token
##
class StatusProperty (Grammar):
    grammar = ('<Property Name="Status" Type="Resource.Status" Nullable="false"/>')


### NavigationProperty (CSDL)
# - grammar consists of 7 total tokens
# - token [1] indicates the name of the property (ex. Manufacturer)
# - token [3] indicates the type of the property (ex. Edm.String)
# - token [5] *may* indicate the "Nullable" keyword being set to "False"; otherwise set to None
# - token [7] indicates an exhaustive list of the property's annotations
##
class NavigationProperty (Grammar):
    grammar = ('<NavigationProperty Name="', WORD('A-Za-z0-9'), '" Type="', WORD('A-Za-z0-9.()_'), '"', OPTIONAL(L('Nullable="false"')), '>', REPEAT(OR(Annotation, NestedAnnotation)), '</NavigationProperty>')


### EnumMember (CSDL)
# - grammar consists of 3 total tokens
# - token [1] indicates the enumeration member
##
class EnumMember (Grammar):
    grammar = ('<Member Name="', WORD('A-Za-z0-9'), '"/>')


### Entity (CSDL)
# - grammar consists of 9 total tokens
# - token [1] indicates the name of the entity (ex. RackPDU)
# - token [3] indicates the base type of the entity (ex. RackPDU.RackPDU; Resource.v1_0_0.ReferenceableMember)
# - token [5] *may* indicate the "Abstract" keyword being set to "True"; otherwise set to None
# - token [7] indicates an exhaustive list of the entity's properties and XML comments
##
class Entity (Grammar):
    grammar = ('<EntityType Name="', WORD('A-Za-z0-9'), '" BaseType="', WORD('A-Za-z0-9._'), '"', OPTIONAL(L('Abstract="true"')), '>', REPEAT(OR(Property, NavigationProperty, StatusProperty, Annotation, NestedAnnotation)), '</EntityType>')


### Enumeration (CSDL)
# - grammar consists of 5 total tokens
# - token [1] indicates the name of the enumeration
# - token [3] indicates an exhaustive list of the enumeration's members and XML comments
class Enumeration (Grammar):
    grammar = ('<EnumType Name="', WORD('A-Za-z0-9'), '">', REPEAT(EnumMember), '</EnumType>')


### edmx:Include (CSDL)
# - grammar consists of 4 total tokens
# - token [1] indicates the namespace of the edmx:Include tag
# - token [3] *may* indicate the alias of the edmx:Include tag
##
class Include (Grammar):
    grammar = ('<edmx:Include Namespace="', WORD('A-Za-z0-9:/._\-'), OPTIONAL('" Alias="'), OPTIONAL(WORD('A-Za-z0-9')), '"/>')


### edmx:Reference (CSDL)
# - grammar consists of 5 total tokens
# - token [1] indicates the URI of the edmx:Reference tag
# - token [3] indicates an exhaustive list of the edmx:Reference tag's edmx:Include tags
##
class Reference (Grammar):
    grammar = ('<edmx:Reference Uri="', WORD('A-Za-z0-9:/._\-'), '">', REPEAT(Include), '</edmx:Reference>')


### Schema (CSDL)
# - grammar consists of 7 total tokens
# - token [1] indicates the XML namespace
# - token [3] indicates the namespace corresponding to the schema
# - token [5] indicates an exhaustive list of the schema's entities, enumerations and XML comments
##
class Schema (Grammar):
    grammar = ('<Schema xmlns="', WORD('A-Za-z0-9:/.-'), '" Namespace="', WORD('A-Za-z0-9._'), '">', REPEAT(OR(Entity, Enumeration)), '</Schema>')


### edmx:DataServices (CSDL)
# - grammar consists of 3 total tokens
# - token [1] indicates an exhaustive list of the edmx:DataServices tag's schemas
##
class DataServices (Grammar):
    grammar = ('<edmx:DataServices>', REPEAT(Schema), '</edmx:DataServices>')


### edmx:Edmx (CSDL)
# - grammar consists of 7 total tokens
# - token [1] indicates the XML namespace of the edmx:Edmx tag
# - token [3] indicates the version of the edmx:Edmx tag
# - token [5] indicates an exhaustive list of the edmx:Edmx tag's edmx:Reference tags, edmx:DataServices tags, and XML comments
##
class Edmx (Grammar):
    grammar = ('<edmx:Edmx xmlns:edmx="', WORD('A-Za-z0-9:/._\-'), '" Version="', WORD('0-9.'), '">', REPEAT(OR(Reference, DataServices)), '</edmx:Edmx>')


### CSDL File
# - grammar consists of 6 total tokens
# - token [1] indicates the version of the CSDL file
# - token [3] indicates the encoding of the CSDL file
# - token [5] indicates an exhaustive list of the CSDL file's edmx:Edmx tag(s) as well as XML comments
##
class CsdlFile (Grammar):
    grammar = ('<?xml version="', WORD('0-9.'), '" encoding="', WORD('A-Za-z0-9\-'), '"?>', Edmx)


### generate_spaces()
# - takes numSpaces as input
# - returns string of numSpaces spaces
##
def generate_spaces(numSpaces):
    spaceString = ''
    for i in range(0, numSpaces):
        spaceString += ' '
    return spaceString


### generate_bullet()
# - takes numSpaces as input
# - same as generate_spaces, but includes a bullet
##
def generate_bullet(numSpaces):
    spaceString = ''
    for i in range(0, numSpaces - 2):
        spaceString += ' '
    spaceString += '- '
    return spaceString


print("Grammar classes defined.")
csdlParser = CsdlFile.parser()
print("Parsing file...")
result = csdlParser.parse_string(newFileString)

schemaDict = {}
dataServices = result[5][5].get_all(DataServices)

schemaDict['Namespace'] = dataServices[0][1][1][3]
schemaDict['Entities'] = [] # entity list
schemaDict['Enumerations'] = [] # enum list
entities = dataServices[0][1][1][5].get_all(Entity)
enums = dataServices[0][1][1][5].get_all(Enumeration)

print("Storing data...")

# store entities
i = 0
while i < len(entities):
    current = {} # entity dict
    current['Name'] = entities[i][1].string
    current['BaseType'] = entities[i][3].string
    current['Properties'] = [] # property list
    current['NavigationProperties'] = [] # nav property list
    properties = entities[i][7].get_all(Property)

    # store properties
    j = 0
    while j < len(properties):
        current2 = {'Name': None,
                    'Type': None,
                    'Description': None,
                    'LongDescription': None,
                    'Permissions': None,
                    'MinValue': None,
                    'MaxValue': None,
                    'Units': None,
                    'Notes': None,
                    'EnumValues': []} # property dict
        current2['Name'] = properties[j][1].string
        current2['Type'] = properties[j][3].string
        annotations = properties[j][7].get_all(Annotation)

        # store annotations
        k = 0
        while k < len(annotations):
            if annotations[k][1].string == 'OData.Permissions':
                current2['Permissions'] = annotations[k][5].string
            elif annotations[k][1].string == 'OData.Description':
                current2['Description'] = annotations[k][5].string
            elif annotations[k][1].string == 'OData.LongDescription':
                current2['LongDescription'] = annotations[k][5].string
            elif annotations[k][1].string == 'Validation.Minimum':
                current2['MinValue'] = annotations[k][5].string
            elif annotations[k][1].string == 'Validation.Maximum':
                current2['MaxValue'] = annotations[k][5].string
            elif annotations[k][1].string == 'Measures.Unit':
                current2['Units'] = annotations[k][5].string
            else:
                current2['Notes'] = annotations[k][5].string
            k += 1
        current['Properties'].append(current2)
        j += 1

    # store nav properties
    navProperties = entities[i][7].get_all(NavigationProperty)
    j = 0
    while j < len(navProperties):
        current2 = {'Name': None,
                    'Type': None,
                    'Permissions': None,
                    'Description': None,
                    'LongDescription': None,
                    'Notes': None,
                    'AssociatedObject': None} # nav property dict
        current2['Name'] = navProperties[j][1].string
        current2['Type'] = navProperties[j][3].string
        annotations2 = navProperties[j][7].get_all(Annotation)

        # store annotations
        k = 0
        while k < len(annotations2):
            if annotations2[k][1].string == 'OData.Permissions':
                current2['Permissions'] = annotations2[k][5].string
            elif annotations2[k][1].string == 'OData.Description':
                current2['Description'] = annotations2[k][5].string
            elif annotations2[k][1].string == 'OData.LongDescription':
                current2['LongDescription'] = annotations2[k][5].string
            elif annotations2[k][1].string == 'OData.AutoExpand':
                k += 1
                continue
            else:
                current2['Notes'] = annotations2[k][5].string
            k += 1

        current['NavigationProperties'].append(current2)
        j += 1

    schemaDict['Entities'].append(current)
    i += 1

# store enums
i = 0
while i < len(enums):
    current = {} # enum dict
    current['Name'] = enums[i][1].string
    current['Members'] = [] # enum member list
    members = enums[i][3].get_all(EnumMember)

    # store enum members
    j = 0
    while j < len(members):
        current2 = members[j][1].string
        current['Members'].append(current2)
        j += 1

    schemaDict['Enumerations'].append(current)
    i += 1

# convert NoneType values to empty strings
for i in range(0, len(schemaDict['Entities'])):
    for k, v in schemaDict['Entities'][i].items():
        if v == None:
            schemaDict['Entities'][i][k] = ''
    for j in range(0, len(schemaDict['Entities'][i]['Properties'])):
        for k, v in schemaDict['Entities'][i]['Properties'][j].items():
            if v == None:
                schemaDict['Entities'][i]['Properties'][j][k] = ''
    for j in range(0, len(schemaDict['Entities'][i]['NavigationProperties'])):
        for k, v in schemaDict['Entities'][i]['NavigationProperties'][j].items():
            if v == None:
                schemaDict['Entities'][i]['NavigationProperties'][j][k] = ''

# store nav property objects and enums in proper places
for i in range(0, len(schemaDict['Entities'])):
    for j in range(0, len(schemaDict['Entities'][i]['NavigationProperties'])):
        for k in range(0, len(schemaDict['Entities'])):
            if schemaDict['Entities'][i]['NavigationProperties'][j]['Name'] == schemaDict['Entities'][k]['Name']:
                schemaDict['Entities'][i]['NavigationProperties'][j]['AssociatedObject'] = schemaDict['Entities'][k]

    for j in range(0, len(schemaDict['Entities'][i]['Properties'])):
        for k in range(0, len(schemaDict['Enumerations'])):
            longFormType = schemaDict['Namespace'].string + '.' + schemaDict['Enumerations'][k]['Name']
            if schemaDict['Entities'][i]['Properties'][j]['Type'] == longFormType:
                for l in range(0, len(schemaDict['Enumerations'][k]['Members'])):
                    schemaDict['Entities'][i]['Properties'][j]['EnumValues'].append(schemaDict['Enumerations'][k]['Members'][l])


print("Converting to comma-separated values...")
fileCursor = 0
f = open(str(schemaDict['Entities'][0]['Name']) + '.csv', 'w+')
currentNumSpaces = 0
bulletCounter = 0
f.write(schemaDict['Entities'][0]['Name'] + ',' + schemaDict['Entities'][0]['BaseType'] + ',,- Auto-Generated Spreadsheet -\n\n')
f.write('Property Name,Type,Permissions,Description,Long Description,Min,Max,Units,Notes,Enumeration Values\n')

### write_entity()
#
##
def write_entity(entity, numSpaces):
    global fileCursor
    global currentNumSpaces
    global bulletCounter

    currentNumSpaces += 4
    entityCsv = open('current' + str(fileCursor) + '.csv', 'w+') # creates newly-named file each time to ensure no redundancy
    fileCursor += 1
    bulletCounter += 1

    for i in range(0, len(entity['Properties'])):
        if bulletCounter <= 1:
            entityCsv.write(generate_spaces(currentNumSpaces))
        elif bulletCounter >= 1:
            entityCsv.write(generate_bullet(currentNumSpaces))
        entityCsv.write(entity['Properties'][i]['Name'] + ',' +
                        entity['Properties'][i]['Type'] + ',' +
                        entity['Properties'][i]['Permissions'] + ',' +
                        entity['Properties'][i]['Description'] + ',' +
                        entity['Properties'][i]['LongDescription'] + ',' +
                        entity['Properties'][i]['MinValue'] + ',' +
                        entity['Properties'][i]['MaxValue'] + ',' +
                        entity['Properties'][i]['Units'] + ',' +
                        entity['Properties'][i]['Notes'] + ',' +
                        '/'.join(entity['Properties'][i]['EnumValues']) + '\n')

    for i in range(0, len(entity['NavigationProperties'])):
        if bulletCounter <= 1:
            entityCsv.write(generate_spaces(currentNumSpaces))
        elif bulletCounter >= 1:
            entityCsv.write(generate_bullet(currentNumSpaces))
        entityCsv.write(entity['NavigationProperties'][i]['Name'] + ',' +
                        entity['NavigationProperties'][i]['Type'] + ',' +
                        entity['NavigationProperties'][i]['Permissions'] + ',' +
                        entity['NavigationProperties'][i]['Description'] + ',' +
                        entity['NavigationProperties'][i]['LongDescription'] + ',,,,' +
                        entity['NavigationProperties'][i]['Notes'] + '\n')
        if entity['NavigationProperties'][i]['AssociatedObject'] != '': # recursive step
            entityCsv.write(write_entity(entity['NavigationProperties'][i]['AssociatedObject'], currentNumSpaces))

    currentNumSpaces -= 4
    bulletCounter -= 1

    entityCsv.seek(0)
    return entityCsv.read()

f.write(write_entity(schemaDict['Entities'][0], 0)) # NOTE: auto-assumes element [0] is primary element of schemaDict
f.close()

print('Success! Output is available as local file ' + schemaDict['Entities'][0]['Name'] + '.csv.')