# ******************************************************************

# *******************************************************************
# ** Name:          SYPHTMLReportWriter.py
# ** Version:       v0.1 - in development
# ** Purpose:       A standard SYP library to allow other Pyhton scripts to access
#                    and create specific SYP reports.
# ** Returns:       None 
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          July 2017
# ** Revisions:     
# ** WishList:		- Logo
#                   - CSS?
#                   - Images and <A> links
# ******************************************************************

# # # imports # # #

import os


# ******************************************************************
# ** Type:          CLASS       
# ** Name:          SYPHTMLReport()
# ** Purpose:       
# ** Author:        Matthew KELLY
# ** Date:          18/07/2017
# ** Revisions:     
# ******************************************************************
class SYPHTMLReport():

    def __init__(self):

        self.__sHeading1 = "South Yorkshire Police Case Report"
        self.__sHeading2 = ""
        self.__dictTables = {}


    # ******************************************************************
    # ** Type:          ROUTINE
    # ** Name:          BuildInformationDict()
    # ** Purpose:       Adds H1 and H2 headings as directed by parameters
    # ** Parameters:    sHeading - H1 heading
    #                   sSubHeading - optional H2 heading
    # ** Returns:       None
    # ** Author:        Matthew KELLY
    # ** Date:          July 2017
    # ** Revisions:     none
    # ******************************************************************
    def AddHeadings(self, sHeading, sSubHeading=""):

        self.__sHeading1 = "<H1>" + sHeading + "</H1>"
        self.__sHeading2 = "<H2>" + sSubHeading + "</H2>"


    # ******************************************************************
    # ** Type:          ROUTINE
    # ** Name:          AddTable()
    # ** Purpose:       
    # ** Parameters:    sTableName - Name of intended table for storage into Table dictionary
    # ** Returns:       None
    # ** Author:        Matthew KELLY
    # ** Date:          July 2017
    # ** Revisions:     none
    # ******************************************************************
    def AddTable(self, sTableName):
        
        if sTableName in self.__dictTables.keys():
            # return or throw an error. Log!
            print("Error! Table of that name already exists.")
        else:
            self.__dictTables[sTableName] = "<TABLE id=" + sTableName + ">"


    # ******************************************************************    
    # ** Name:          AddTableRow()
    # ** Purpose:       
    # ** Author:        Matthew KELLY
    # ** Date:          
    # ** Revisions:     
    # ******************************************************************
    def AddTableRow(self, sTableName, lstTD):

        sHTML = ""
        if sTableName in self.__dictTables.keys():
            sHTML += "<TR>"
            for each in lstTD:
                sHTML += "<TD>" + each + "</TD>"
            self.__dictTables[sTableName] += sHTML + "</TR>"
        else:
            # table name does not exist! Throw error and/or log?
            print("Error! Table of that name does not exist.")


    # ******************************************************************    
    # ** Name:          sReturnHTMLString()
    # ** Purpose:       
    # ** Author:        Matthew KELLY
    # ** Date:          
    # ** Revisions:     
    # ******************************************************************
    def sReturnHTMLString(self):

        sHTML = "<HTML>"
        sHTML += self.__sHeading1
        if self.__sHeading2 != "<H2></H2>":
            sHTML += self.__sHeading2
        
        for eachTable in self.__dictTables:
            sHTML += "<H3>" + eachTable + "</H3>"
            sHTML += self.__dictTables[eachTable]
            sHTML += "</TABLE>"

        return sHTML