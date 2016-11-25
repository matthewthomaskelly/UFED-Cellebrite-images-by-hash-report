# *******************************************************************
# ** Name:          UFED create report from HASH values
# ** Version:       v2.2
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and create a report with images located.
#     09/11/2016     - 2.0 - First working release to HTCU
#     09/11/2016     - 2.1 - Amended Form to inlude checkbox to separate reports.
#                          - Changed HTMLWriter accordingly 
#     10/11/2016     - 2.2 - Changed resizeImage and added coding to count number of images
# ** Returns:       None - file located and not-located or duplicates will be logged.
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          06/05/2015
# ** Revisions:     none
# ** WishList:		Add functionality to form to request file-data information for report.
# **				Error logging - try/catch in main()?
# **                Export clsHTMLWriter to separate module for generic use.
# ******************************************************************

# # # Imports # # #
import os
import hashlib
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *
from System.Drawing import *
from System import IntPtr

# # # function definitions # # # 

# *******************************************************************
# ** Name:          main()
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and export those images located.
#                   These exported files will be placed into a report with thumbnails created, linking to original.
# ** Returns:       None - file located and not-located or duplicates will be logged.
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          06/05/2015
# ** Revisions:     none
# ******************************************************************
def main():

    # Get location of CSV file, path for report and report file name
    frmCSVFolder = IForm()
    Application.Run( frmCSVFolder )
    sCSVFileLoc = frmCSVFolder.sCSVFilePathname
    sExportReportLoc = frmCSVFolder.sReportFolderName
    sReportName = frmCSVFolder.sReportFileName
    bSeparateReports = frmCSVFolder.bSeparateReports
    
    sThumbRelLoc = '\\Thumbs'
    os.mkdir(sExportReportLoc + sThumbRelLoc)

    lstDataFiles = ['Image', 'Video']

    # loop through each specified data files (will probably remain at Images and Videos only!)
    for eachDataType in lstDataFiles:

        # Open CSV file and locate column linked to MD5 values
        objCSVFile = open( sCSVFileLoc )
        sReadLine = objCSVFile.readline()
        sReadLineSplit = sReadLine.split(',')
        iLen = len(sReadLineSplit)
        sReadLineSplit[iLen-1] = sReadLineSplit[iLen-1].strip()
        iHASHIndex = sReadLineSplit.index('Hash Value')
        iCategoryIndex = sReadLineSplit.index('Category')

        objDataFiles = ds.DataFiles[eachDataType]
        sFilesRelLoc = sExportReportLoc + '\\' + eachDataType
        os.mkdir(sFilesRelLoc)
        
        lstFiles = []
        
        while True:

            # Class to store details of each MD5 match located
            objFilesDetails = ImageDetails()

            sReadLine = objCSVFile.readline()
            if not sReadLine:
                break

            sReadLineSplit = sReadLine.split(',')    

            # convert HASH value to lowercase for match in UFED reader
            sReadLineSplit[iHASHIndex] = sReadLineSplit[iHASHIndex].lower()

            # Iterate through each image and locate matching MD5 values
            for eachFile in objDataFiles:

                sMD5 = eachFile.Md5
                # calculate HASH value if not in Cellebrite UFED
                if sMD5 == '':
                    sMD5 = getMd5HashValue(eachFile)

                if sMD5  == sReadLineSplit[iHASHIndex].strip():

                    # save image to images location
                    try:
                        exportUFEDFile(eachFile, sFilesRelLoc)
                    except:
                        print('Error writing file!')

                    objFilesDetails.sCategory = sReadLineSplit[iCategoryIndex]
                    objFilesDetails.sMD5 = sReadLineSplit[iHASHIndex]
                    objFilesDetails.sFileName = eachFile.Name
                    objFilesDetails.sFolderName = eachFile.Folder
                    objFilesDetails.sCreationDate = str(eachFile.CreationTime)
                    objFilesDetails.sRelSavedPathFileName = sFilesRelLoc + '\\'  + eachFile.Name
                    objFilesDetails.sRelSavedPathThumbName  = sExportReportLoc + sThumbRelLoc + '\\' + eachFile.Name + '.png'
                    os.system("c:\\ffmpeg -i " + objFilesDetails.sRelSavedPathFileName + " -vf scale=100:-1 " + objFilesDetails.sRelSavedPathThumbName) 
                    
                    lstFiles.append(objFilesDetails)

                # end of sMD5 match

        for each in lstFiles:
            print(each.sFileName) 

            # end of eachFile in DataFiles
       
        # end of read line CSV files
        # close CSV file
        objCSVFile.close()

    # Write built HTML stream to file location
    #print(sExportReportLoc + '\\' +  sReportName)
    #objHTMLWrite.WriteHTMLtoFile(sExportReportLoc + '\\' + sReportName, bSeparateReports, 4)
    

# *******************************************************************
# ** Name:          getMd5HashValue
# ** Purpose:       
# ** Author:        Matthew KELLY
# ** Date:          
# ** Revisions:     none
# ****************************************************************** 
def getMd5HashValue (r_objImageFile):

    hash = hashlib.md5()
    try:
        rd = r_objImageFile.read()
        hash.update(rd)
        hexMD5 = hash.hexdigest()
        return hexMD5.upper
    except:
        return ''

class ImageDetails():
    
    def __init__(self):
        self.__sFileName = ''
        self.__sFolderName = ''
        self.__sCreationDate = ''
        self.__sMD5 = ''
        self.__sCategory = ''
        self.__sRelSavedPathFileName = ''
        self.__sRelSavedPathThumbName = ''

    def sFileName(self, v_sData):
        self.__sFileName = v_sData
    def sFileName(self):
        sFileName = self.__sFileName

    def sFolderName(self, v_sData):
        self.__sFolderName= v_sData
    def sFolderName(self):
        sFolderName = self.__sFolderName

    def sCreationDate(self, v_sData):
        self.__sCreationDate = v_sData
    def sCreationDate(self):
        sCreationDate = self.__sCreationDate

    def sMD5(self, v_sData):
        self.__sMD5 = v_sData
    def sMD5(self):
        sMD5 = self.__sMD5

    def sCategory(self, v_sData):
        self.__sCategory = v_sData
    def sCategory(self):
        sCategory = self.__sCategory

    def sRelSavedPathFileName(self, v_sData):
        self.__sRelSavedPathFileName = v_sData
    def sRelSavedPathFileName(self):
        sRelSavedPathFileName = self.__sRelSavedPathFileName

    def sRelSavedPathThumbName(self, v_sData):
        self.__sRelSavedPathThumbName = v_sData
    def sRelSavedPathThumbName(self):
        sRelSavedPathThumbName = self.__sRelSavedPathThumbName


# *******************************************************************
# ** Name:          IForm
# ** Purpose:       
# ** Author:        Unknown - MET Police
# ** Date:          
# ** Revisions:     06/05/2016 - removed hash library reference
#                   08/11/2016 - added further text box for CSV file and report folder
# ****************************************************************** 
class IForm(Form):

        def __init__(self):
                self.Text = "Select CSV file and report folder locations"
                self.Height = 175
                self.Width = 500

                #add button
                self.btnOk = Button()
                self.btnOk.Text = "&OK"
                self.btnOk.Location = Point(10, 85)
                self.btnOk.Click += self.OKPressed

                #add textbox for CSV file
                self.txtCSVFileName = TextBox()
                self.txtCSVFileName.Text = "CSV file location goes here"
                self.txtCSVFileName.Location = Point(10,10)
                self.txtCSVFileName.Width = 450

                #add textbox for report folder location
                self.txtReportFolderLocation = TextBox()
                self.txtReportFolderLocation.Text = "Proposed report folder Path goes here"
                self.txtReportFolderLocation.Location = Point(10,35)
                self.txtReportFolderLocation.Width = 450

                #add textbox for report folder location
                self.txtReportFileName = TextBox()
                self.txtReportFileName.Text = "Proposed report file name. (No file extensions, please!)"
                self.txtReportFileName.Location = Point(10,60)
                self.txtReportFileName.Width = 300

                # add a tick box to indicate whether to separate reports
                self.chkSeparateReports = CheckBox()
                self.chkSeparateReports.Text = "Separate Reports by Category"
                self.chkSeparateReports.Location = Point(300, 85)
                self.chkSeparateReports.Width = 200
                self.chkSeparateReports.Checked = False

                self.Controls.Add(self.txtCSVFileName)
                self.Controls.Add(self.txtReportFolderLocation)
                self.Controls.Add(self.txtReportFileName)
                self.Controls.Add(self.btnOk)
                self.Controls.Add(self.chkSeparateReports)
                self.CenterToScreen()

                self.sCSVFilePathname = ""   
                self.sReportFolderName = ""
                self.sReportFileName = ""
                self.bSeparateReports = False

        def OKPressed(self, sender, args):

                sCSVFile = self.txtCSVFileName.Text
                sReportFolder = self.txtReportFolderLocation.Text
                sReportFile = self.txtReportFileName.Text
                bSeparateReports = self.chkSeparateReports.Checked

                if ( os.path.isfile( sCSVFile ) == False ):
                        MessageBox.Show( "The specified CSV file does not exist, please choose another." , "Invalid Directory" )
                elif ( os.path.isdir( sReportFolder ) == False ):
                        r = MessageBox.Show( "Folder path for report location does not exist. Would you like to create it?", "Invalid Directory", MessageBoxButtons.YesNo, MessageBoxIcon.Question )
                        if r == DialogResult.Yes:
                                os.mkdir(sReportFolder)
                                self.sCSVFilePathname = sCSVFile
                                self.sReportFolderName = sReportFolder
                                self.sReportFileName = sReportFile
                                self.bSeparateReports = bSeparateReports
                                self.Close()
                        else:
                            pass  
                else:
                    MessageBox.Show( "The specified report folder already exists, please choose another." , "Invalid Directory" )
                    pass


# *******************************************************************
# ** Name:          exportUFEDFile
# ** Purpose:       Takes an Image from ds in UFED Cellebrite and exports to file-path specified
# ** Author:        Unknown - MET Police
# ** Date:          
# ** Revisions:     06/05/2016 - removed hash library reference
# ****************************************************************** 
def exportUFEDFile(pic,path):
    fileDataReadsize = 2**25
    fileSize = pic.Size
    if (fileSize > 2113929216):
        MessageBox.Show("%s is greater than 2GB, please review manually. Filename stored in trace window" % (pic.Name),"Error")
        print ("File %s is over 2gb in size, review manually" % (pic.Name))
        return "", ""
    # mtk 06/05/2016 
    # m = hashlib.md5()
    filename = pic.Name 
    filePath = os.path.join(path,filename)
    ext = os.path.splitext(pic.Name)[1]
    locateInvalidChar = ext.find("?")
    if (locateInvalidChar != -1):
        ext = ext[:locateInvalidChar]
    try:
        f = open(filePath,'wb')
        pic.seek(0)
        filedata = pic.read(fileDataReadsize)
        while len(filedata) > 0:
        # mtk 06/05/2016
        # m.update(filedata)
            f.write(filedata)
            filedata = pic.read(fileDataReadsize)
        pic.seek(0)
        f.close()
    except:
        return ""


# # # class definitions # # # 

# *******************************************************************
# ** Name:          clsHTMLWriter
# ** Purpose:       A class to store HTML data in tables by Category stored in a dictionary for each Category.
#                   Includes a function to write HTML page at conclusion to specified location for report.
# ** Author:        Matthew KELLY
# ** Date:          11/05/2015
# ** Revisions:     19/07/2016 - amended functions AddTableContentByKeyAsLists() and AddImageLocationReference() to include private
#                    function call __AddToDicCategories() that checks whether dictionary key exists before adding to Category dictionary
#                   07-08/11/2016 - amended AddTableContentByKeyAsLists() to only create TD data HTML and add to dictionary as list
#                   08/11/2016 - amended WriteHTMLtoFile() to write HTML TD stored in dictionary as lists in columns as specified.
#                                 The intention will be to add this variable to the form for user specification, 
#                                 Will also change functionality to make it possible for separate reports to be created
# ******************************************************************
class clsHTMLWriter:

    def __init__(self):
        self.__sHeading = 'South Yorkshire Police Case Report'
        self.__dicCategories = {}

    def AddHeadingTitle(self, v_sHeading):
        self.__sHeading = v_sHeading

    def AddTableContentByKeyAsLists(self, v_sKey, v_sThumbRelativeLocation, v_sImageRelativeLocation, v_lstTableContent):
        # nested dictionary for each Category image
        sARefString = self.__GetImageHTMLReference(v_sThumbRelativeLocation, v_sImageRelativeLocation)
        lstTemp = self.__sBuildHTMLTableLst(sARefString, v_lstTableContent)
        self.__AddToDicCategories(v_sKey, lstTemp)
     
    def WriteHTMLtoFile(self, v_sFileLocation, v_bSeparateReports, v_iTableColumns=3):
        
        if v_bSeparateReports == True:
            #separate report for each category
            for eachCategory in self.__dicCategories:

                filestream = open(v_sFileLocation + ' ' + eachCategory + '.html', 'w')

                sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'
                sHTML += self.__sBuildHTMLTableStringForCategory(eachCategory, v_iTableColumns)
                sHTML += '</HTML>'

                filestream.write(sHTML)
                filestream.close()
        else:
            # one report for each category
            filestream = open(v_sFileLocation + '.html', 'w')  

            sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'

            for eachCategory in self.__dicCategories:
                sHTML += self.__sBuildHTMLTableStringForCategory(eachCategory, v_iTableColumns)
            sHTML += '</HTML>'

            filestream.write(sHTML)
            filestream.close()
        

    # private functions
    def __sBuildHTMLTableLst(self, v_sARefString, v_lstTableContent):
        lstTemp = []
        sHTMLBuiltString = '<TD><BR>' + v_sARefString + '<BR>'
        for sTableContent in v_lstTableContent:
            sHTMLBuiltString += sTableContent + '<BR>'
        sHTMLBuiltString += '</TD>'  
        lstTemp = [sHTMLBuiltString]
        return (lstTemp)

    def __sBuildHTMLTableStringForCategory(self, r_CurrentCategory, v_iTableColumns):

        if self.__dicCategories[r_CurrentCategory] != '':
            sHTML = '<H2>' + r_CurrentCategory + '</H2>'
            sHTML += '<TABLE>' + '<TR>'
            iCount = 0
            for eachSubLst in self.__dicCategories[r_CurrentCategory]:
                iCount += 1
                for eachListValue in eachSubLst:
                    # 10/11/2016 - added coding to append count of images per category into HTML. Assumes that first lst value will be image </A>
                    iIndex = eachListValue.find('</A>')
                    eachListValue = eachListValue[:iIndex+4] + '<BR>' + str(iCount) + eachListValue[iIndex+4:]                                    
                    sHTML += eachListValue
                if iCount % v_iTableColumns == 0:
                    sHTML += '</TR><TR>'
            sHTML += '</TR></TABLE>'
        else:
            sHTML = ''
        return sHTML

    def __AddToDicCategories(self, v_sKey, v_sHTMLBuiltString):
        lstTemp = [v_sHTMLBuiltString]
        if v_sKey in self.__dicCategories:
            self.__dicCategories[v_sKey] += lstTemp
        else:  
            self.__dicCategories[v_sKey] = lstTemp

    def __GetImageHTMLReference(self, v_sThumbRelativeLocation, v_sImageRelativeLocation):
        sHTMLBuiltString = ''
        if v_sImageRelativeLocation != '':
            sHTMLBuiltString += '<A href=.' + v_sImageRelativeLocation + '>'
        else:
            sHTMLBuiltString += '<A href=.' + v_sThumbRelativeLocation + '>', 
        sHTMLBuiltString += '<IMG src=.' + v_sThumbRelativeLocation + '>'
        sHTMLBuiltString += '</A>'
        return ( sHTMLBuiltString )

# # # Start of script  # # #
main()