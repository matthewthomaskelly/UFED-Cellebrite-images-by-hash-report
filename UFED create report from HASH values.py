# *******************************************************************
# ** Name:          UFED create report from HASH values
# ** Version:       v3.3
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and create a report with images located.
# ** Returns:       None 
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          25/11/2015
# ** Revisions:     v 3.0 - adds Class to store each file match data to later write information to HTML report
#                         - uses ffmpeg to create thumbnails for Images and Videos.
#                   v 3.1 - amend error caused with '\' within specified file name i.e Case \ Force specific
#                         - sort out logic for multiple instances of MD5 or Images
#                         - continually update comments  
#                   v 3.2 - look at coding for building HTML and separate Accessible and Incaccessable
#                   v 3.3 - Small amendment with Hash Value category heading. Put this back to prior version and changed heading to MD5 as everyone should be using Griffeye in SYP
# ** WishList:		Add functionality to form to request file-data information for report.
# **				Error logging - try/catch in main()?
# **                file located and not-located or duplicates will be logged.
# **                Export clsHTMLWriter to separate module for generic use.
# ******************************************************************

                                # # # Imports # # #
import os
import hashlib
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *
from System.Drawing import *
import sys
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
# ** Revisions:     11/2016 - major revision in program logic removing dependency on HTML write for storage of images data.
#                           - added further loop for Images AND Videos in UFED ds object
#                           - function uses ffmpeg for thumbnail creation. Added check for ffmpeg existence and alternative calls for Pictures and Videos
# ******************************************************************

def main():

    # this variable will be passed to DOS shell. Beware literals! i.e spaces in file/folder names
    sFFMPEGLocation = 'C:\\FFMPEG.EXE'
    bCheck = bCheckFFMPEGExists( sFFMPEGLocation )
    if bCheck != True:
        MessageBox.Show ("Program cannot find the executable ffmpeg.exe in the root of C: and will terminate prematurely. Sorry!", "ffmpeg.exe dependency!", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        sys.exit()

    # Get location of CSV file, path for report and report file name
    frmCSVFolder = IForm()
    Application.Run( frmCSVFolder )
    sCSVFileLoc = frmCSVFolder.sCSVFilePathname
    sExportReportLoc = frmCSVFolder.sReportFolderName
    sReportName = frmCSVFolder.sReportFileName
    bSeparateReports = frmCSVFolder.bSeparateReports
    
    sThumbRelLoc = '\\Thumbs'
    os.mkdir(sExportReportLoc + sThumbRelLoc)

    # specified Cellebrite data files
    lstDataFiles = ['Image', 'Video']

    # loop through each specified data files (will probably remain at Images and Videos only!)
    iCount = 0
    for eachDataType in lstDataFiles:

        # Open CSV file and locate column linked to MD5 values
        objCSVFile = open( sCSVFileLoc )
        sReadLine = objCSVFile.readline()
        asReadLineSplit = sReadLine.split(',')
        iLen = len(asReadLineSplit)
        asReadLineSplit[iLen-1] = asReadLineSplit[iLen-1].strip()
        iHASHIndex = asReadLineSplit.index('MD5')
        iCategoryIndex = asReadLineSplit.index('Category')


        # 02/12/2016 Tag added at request AT
        try:
            iTagIndex = asReadLineSplit.index('Tags')
        except:
            iTagIndex = -1

        # assign Images or Video to DataFiles object for MD5 comparison
        objDataFiles = ds.DataFiles[eachDataType]
        # These will be stored in the relevant (relative) directory...
        sFilesRelLoc =   '\\' + eachDataType
        # ... and created
        os.mkdir(sExportReportLoc + sFilesRelLoc)
        
        # store the matching DataFiles in a lst of Objects
        lstFiles = []

        # read the CSV file sequentially line by line until no more data
        while True:

            # When the last line is read this loop will break
            sReadLine = objCSVFile.readline()
            if not sReadLine:
                break

            # Class to store details of each MD5 match located
            objFilesDetails = clsImageDetails()
            asReadLineSplit = sReadLine.split(',')    

            # convert HASH value to lowercase for match in UFED reader
            asReadLineSplit[iHASHIndex] = asReadLineSplit[iHASHIndex].lower()
            asReadLineSplit[iHASHIndex] = asReadLineSplit[iHASHIndex].strip()

            # Iterate through each image and locate matching MD5 values
            for eachFileObj in objDataFiles:

                # check whether or not the MD5 value has already been searched for. If so, break loop
                if bCheckIfMD5Exists( lstFiles, asReadLineSplit[iHASHIndex] ):
                    break

                sMD5 = eachFileObj.Md5
                # calculate HASH value if not in Cellebrite UFED
                if sMD5 == '':
                    sMD5 = getMd5HashValue(eachFileObj)

                
                if sMD5  == asReadLineSplit[iHASHIndex]:

                    # save image to images location
                    iCount += 1
                    try:
                        sSavedFileName = ''
                        sSavedFileName = exportUFEDFile ( eachFileObj, sExportReportLoc + sFilesRelLoc, str(iCount) )
                    except:
                        print('Error writing file!')

                    objFilesDetails.sCategory = asReadLineSplit[iCategoryIndex]
                    objFilesDetails.sMD5 = asReadLineSplit[iHASHIndex]
                    objFilesDetails.sFileName = str(eachFileObj.Name)
                    objFilesDetails.sFolderName = eachFileObj.Folder
                    objFilesDetails.sCreationDate = str(eachFileObj.CreationTime)
                    objFilesDetails.sRelSavedPathFileName = sFilesRelLoc + '\\'  + sSavedFileName
                    objFilesDetails.sRelSavedPathThumbName  =  sThumbRelLoc + '\\' + sSavedFileName + '.png'
                    if iTagIndex > 0:
                        objFilesDetails.sTagsNotes = asReadLineSplit[iTagIndex]
                    else:
                        objFilesDetails.sTagsNotes = '' 
                    
                    if eachDataType == 'Video':
                        os.system( sFFMPEGLocation + " -i \"" + sExportReportLoc  + objFilesDetails.sRelSavedPathFileName + "\" -ss 00:00:01.0 -vframes 1 -vf scale=100:-1 \"" + sExportReportLoc + objFilesDetails.sRelSavedPathThumbName + "\"")
                    else:
                        os.system( sFFMPEGLocation + " -i \"" + sExportReportLoc  + objFilesDetails.sRelSavedPathFileName + "\" -vf scale=100:-1 \"" + sExportReportLoc + objFilesDetails.sRelSavedPathThumbName + "\"") 
                    
                    lstFiles.append(objFilesDetails)

                # end of sMD5 match

            # end of eachFileObj in DataFiles
              
        # Write built HTML stream to file location
        objHTMLWrite = clsHTMLWriter()      
        objHTMLWrite.WriteHTMLtoFile( lstFiles, sExportReportLoc + '\\' + sReportName + ' ' + eachDataType, bSeparateReports, 4)
        
        sAppSpecificFolders = ""
        sAccessibleFolders = ""
        sNonAccessibleFolders = ""
        bLoop = True
        while bLoop:

            r = MessageBox.Show( "Would you like to specifiy folder locations for Accessible, Non-Accessible and Application specific files?", "Recompile reports", MessageBoxButtons.YesNo, MessageBoxIcon.Question )
            if r == DialogResult.Yes:
                frmSpecify = JForm()
                frmSpecify.sAppSpecificFolders = sAppSpecificFolders
                frmSpecify.sAccessibleFolders = sAccessibleFolders
                frmSpecify.sNonAccessibleFolders = sNonAccessibleFolders
                Application.Run( frmSpecify )
                sAppSpecificFolders = frmSpecify.sAppSpecificFolders
                sAccessibleFolders = frmSpecify.sAccessibleFolders
                sNonAccessibleFolders = frmSpecify.sNonAccessibleFolders
                # form causes UFED to crash. Is this due to garbage disposal as arguably this form is not the main API!?
                frmSpecify.Dispose()
                objHTMLWrite.setSearchTermFolders( sAppSpecificFolders.split(','), sAccessibleFolders.split(','), sNonAccessibleFolders.split(',') )
                objHTMLWrite.WriteHTMLtoFile( lstFiles, sExportReportLoc + '\\' + sReportName + ' ' + eachDataType, bSeparateReports, 4)
            else:
                bLoop = False

        # end of read line CSV files
       
        # close CSV file
        objCSVFile.close()

# end of main()


# *******************************************************************
# ** Name:          bCheckFFMPEGExists
# ** Purpose:       to check is ffmpeg.exe exists in specified location
# ** Author:        Matthew KELLY
# ** Date:          30/11/2016
# ** Revisions:     none
# ****************************************************************** 
def bCheckFFMPEGExists(v_sLocationToCheck):

    if os.path.isfile( v_sLocationToCheck ):
        return True
    else:
        return False

def bCheckIfMD5Exists(v_lstFileDetails, v_sMD5ToCheck):
    bReturnValue = False
    for eachFile in v_lstFileDetails:
        if eachFile.sMD5 == v_sMD5ToCheck:
            bReturnValue = True
            break
    return bReturnValue

# *******************************************************************
# ** Name:          getMd5HashValue
# ** Purpose:       as above
# ** Author:        Matthew KELLY
# ** Date:          August 2016
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

# *******************************************************************
# ** Name:          exportUFEDFile
# ** Purpose:       Takes an Image from ds in UFED Cellebrite and exports to file-path specified
# ** Author:        Unknown - MET Police
# ** Date:          
# ** Revisions:     06/05/2016 - removed hash library reference
#                   30/11/2016 - added optional function argument to specify savename or use exisiting Image object name.
#                              - Changed variables names to be more meaningful for ease of reading
# ****************************************************************** 
def exportUFEDFile( v_objImage, v_sFolderPathToSave, r_sFileNameToSaveLessExt='' ):
    
    # check size of ImageObject for successfull write operation
    if ( v_objImage.Size > 2113929216 ):
        MessageBox.Show("%s is greater than 2GB, please review manually. Filename stored in trace window" % (v_objImage.Name),"Error")
        print ("File %s is over 2gb in size, review manually" % (v_objImage.Name))
        return "", ""
    
    # check extention of object passed
    sExt = os.path.splitext( v_objImage.Name )[1]
    intLocateInvalidChar = sExt.find("?")
    if ( intLocateInvalidChar != -1 ):
        sExt = sExt[ :intLocateInvalidChar ]

    # save filename as exisiting if none specified
    if r_sFileNameToSaveLessExt == '':
        r_sFileNameToSaveLessExt = v_objImage.Name 
    else:
        r_sFileNameToSaveLessExt = r_sFileNameToSaveLessExt + sExt

    # specifiy size of data to read on each copy and full file-path name from folder and file specified
    intFileDataReadSize = 2**25
    sFullSaveFilePath = os.path.join( v_sFolderPathToSave, r_sFileNameToSaveLessExt )

    # attempt to open file for write and copy data at size specified. (this will be while data read is greater than 0)
    try:
        objFileStream = open( sFullSaveFilePath, 'wb' )
        v_objImage.seek(0)
        binFileDataRead = v_objImage.read( intFileDataReadSize )
        while len( binFileDataRead ) > 0:
            objFileStream.write( binFileDataRead )
            binFileDataRead = v_objImage.read( intFileDataReadSize )
        # set object back to start and close filestream  
        v_objImage.seek(0)
        objFileStream.close()
        return r_sFileNameToSaveLessExt
    except:
        return ""


                                # # # class definitions # # # 

# *******************************************************************
# ** Name:          IForm
# ** Purpose:       Displays a form to specify CSV file, Report Folder and Report Name
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
                self.txtAppSpecificFolders = TextBox()
                self.txtAppSpecificFolders.Text = "Proposed report folder Path goes here"
                self.txtAppSpecificFolders.Location = Point(10,35)
                self.txtAppSpecificFolders.Width = 450

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
                self.Controls.Add(self.txtAppSpecificFolders)
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
                sReportFolder = self.txtAppSpecificFolders.Text
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
# ** Name:          JForm
# ** Purpose:       Displays a form to specify known folder locations for Accessible, Application related, 
#                    and Non-accessible files
# ** Author:        Matthew KELLY
# ** Date:          07/12/2016
# ** Revisions:     Amended JForm as interface
# ****************************************************************** 
class JForm(Form):

        def __init__(self):
                self.Text = "Folder Locations. "
                self.Height = 210
                self.Width = 650

                #add button
                self.btnOk = Button()
                self.btnOk.Text = "&OK"
                self.btnOk.Location = Point(10, 140)
                self.btnOk.Click += self.OKPressed

                # overarching label
                self.lblInstructions = Label()
                self.lblInstructions.Text = "Please specify folder locations from known Accessible, Application specific and Non-Accessible files. Remainder will be classified as Unknown. \
 Please separate the individual folder locations with a single comma. \
 Partial folder name contents will suffice."
                self.lblInstructions.Width = 600
                self.lblInstructions.Height = 40
                self.lblInstructions.Location = Point(10,10)
                
                # label for Accessible folders
                self.lblAccessibleFolders = Label()
                self.lblAccessibleFolders.Text = "Accessible folders: "
                self.lblAccessibleFolders.Width = 150
                self.lblAccessibleFolders.Location = Point(10,60)

                #add textbox for Accessible folders
                self.txtAccessibleFolders = TextBox()
                self.txtAccessibleFolders.Text = ""
                self.txtAccessibleFolders.Location = Point(160,60)
                self.txtAccessibleFolders.Width = 450

                # label for Application specific folders
                self.lblAppSpecificFolders = Label()
                self.lblAppSpecificFolders.Text = "Application specific folders: "
                self.lblAppSpecificFolders.Width = 150
                self.lblAppSpecificFolders.Location = Point(10,85)

                #add textbox for Application specific folders
                self.txtAppSpecificFolders = TextBox()
                self.txtAppSpecificFolders.Text = ""
                self.txtAppSpecificFolders.Location = Point(160,85)
                self.txtAppSpecificFolders.Width = 450

                # label for Non-Accessible folders
                self.lblNonAccessibleFolders = Label()
                self.lblNonAccessibleFolders.Text = "Non-Accessible folders: "
                self.lblNonAccessibleFolders.Width = 150
                self.lblNonAccessibleFolders.Location = Point(10,110)

                #add textbox for Non-Accessible folders
                self.txtNonAccessibleFolders = TextBox()
                self.txtNonAccessibleFolders.Text = ""
                self.txtNonAccessibleFolders.Location = Point(160,110)
                self.txtNonAccessibleFolders.Width = 450

                self.Controls.Add(self.lblInstructions)
                self.Controls.Add(self.lblAccessibleFolders)
                self.Controls.Add(self.txtAccessibleFolders)
                self.Controls.Add(self.lblAppSpecificFolders)
                self.Controls.Add(self.txtAppSpecificFolders)
                self.Controls.Add(self.lblNonAccessibleFolders)
                self.Controls.Add(self.txtNonAccessibleFolders)
                self.Controls.Add(self.btnOk)
                self.CenterToScreen()

                self.sAccessibleFolders = ""
                self.sAppSpecificFolders = ""  
                self.sNonAccessibleFolders = ""
   
        def OnLoad(self, sender):
                self.txtAccessibleFolders.Text = self.sAccessibleFolders
                self.txtAppSpecificFolders.Text = self.sAppSpecificFolders
                self.txtNonAccessibleFolders.Text = self.sNonAccessibleFolders

        def OKPressed(self, sender, args):

                self.sAppSpecificFolders = self.txtAppSpecificFolders.Text
                self.sAccessibleFolders = self.txtAccessibleFolders.Text
                self.sNonAccessibleFolders = self.txtNonAccessibleFolders.Text
                self.Close()


# *******************************************************************
# ** Name:          clsImageDetails
# ** Purpose:       A class to store data regarding Image and Video recognised as a match through MD5 comparison.
# ** Author:        Matthew KELLY
# ** Date:          22/11/2016
# ** Revisions:     
# ******************************************************************
class clsImageDetails():
    
    def __init__(self):
        self.__sFileName = ''
        self.__sFolderName = ''
        self.__sCreationDate = ''
        self.__sMD5 = ''
        self.__sCategory = ''
        self.__sRelSavedPathFileName = ''
        self.__sRelSavedPathThumbName = ''
        self.__sTagsNotes = ''

    # Set and Get sFileName
    def sFileName(self, v_sData):
        self.__sFileName = v_sData
    def sFileName(self):
        sFileName = self.__sFileName

    # Set and Get sFolderName
    def sFolderName(self, v_sData):
        self.__sFolderName= v_sData
    def sFolderName(self):
        sFolderName = self.__sFolderName

    # Set and Get sCreationDate
    def sCreationDate(self, v_sData):
        self.__sCreationDate = v_sData
    def sCreationDate(self):
        sCreationDate = self.__sCreationDate

    # Set and Get sMD5
    def sMD5(self, v_sData):
        self.__sMD5 = v_sData
    def sMD5(self):
        sMD5 = self.__sMD5

    # Set and Get sCategory
    def sCategory(self, v_sData):
        self.__sCategory = v_sData
    def sCategory(self):
        sCategory = self.__sCategory

    # Set and Get sRelSavedPathFileName
    def sRelSavedPathFileName(self, v_sData):
        self.__sRelSavedPathFileName = v_sData
    def sRelSavedPathFileName(self):
        sRelSavedPathFileName = self.__sRelSavedPathFileName

    # Set and Get sRelSavedPathThumbName
    def sRelSavedPathThumbName(self, v_sData):
        self.__sRelSavedPathThumbName = v_sData
    def sRelSavedPathThumbName(self):
        sRelSavedPathThumbName = self.__sRelSavedPathThumbName

    # Set and Get sTags text
    def sTagsNotes(self, v_sData):
        self.__sTagsNotes = v_sData
    def sTagsNotes(self):
        sTagsNotes = self.__sTagsNotes

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
        self.__lstAccessibleSearchTerms = []
        self.__lstNonAccessibleSearchTerms = []
        self.__lstAppSpecificSearchTerms = []


    def AddHeadingTitle(self, v_sHeading):
        self.__sHeading = v_sHeading


    def setSearchTermFolders(self, lstAppSpecific, lstAccessibleSpecific, lstNonAccessible):
        self.__lstAppSpecificSearchTerms = lstAppSpecific
        self.__lstAccessibleSearchTerms = lstAccessibleSpecific
        self.__lstNonAccessibleSearchTerms = lstNonAccessible


    def __BuildDicCategories(self, v_lstFiles):

        self.__dicCategories = {}

        for eachFileObj in v_lstFiles:
            sCategory = eachFileObj.sCategory
            sARefString = self.__GetImageHTMLReference( eachFileObj.sRelSavedPathThumbName, eachFileObj.sRelSavedPathFileName )
            lstTableContent = [ 'File name: ' + eachFileObj.sFileName, 'In Folder: ' + eachFileObj.sFolderName, 'Creation Date: ' + eachFileObj.sCreationDate, 'MD5: ' + eachFileObj.sMD5 ]
            # added at request of AT 02/12/2016
            if eachFileObj.sTagsNotes != '':
                lstTableContent.append ( 'Tag notes: ' + eachFileObj.sTagsNotes )
            lstTemp = self.__sBuildHTMLTableLst( sARefString, lstTableContent )
            self.__AddToDicCategories( sCategory, lstTemp )


    def WriteHTMLtoFile(self, r_lstFilesObj, v_sFileLocation, v_bSeparateReports, v_iTableColumns=3):
        
        self.__BuildDicCategories(r_lstFilesObj)


        if v_bSeparateReports == True:
            #separate report for each category
            for eachCategory in self.__dicCategories:

                sReportFileName = v_sFileLocation + ' ' + self.__sPurgeFileName( eachCategory + '.html')

                # 01/12/2016 - issues creating report when Case \ Force specific. Need to parse eachCategory text to cater for special characters.
                filestream = open(sReportFileName, 'w')

                sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'
                sHTML += self.__sBuildHTMLTableStringForCategory(eachCategory, v_iTableColumns)
                sHTML += '</HTML>'

                filestream.write(sHTML)
                filestream.close()
        else:
            
            sReportFileName = v_sFileLocation + '.html'
            
            # one report for each category
            filestream = open(sReportFileName, 'w')  

            sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'
            for eachCategory in self.__dicCategories:
                sHTML += self.__sBuildHTMLTableStringForCategory(eachCategory, v_iTableColumns)

            sHTML += '</HTML>'

            filestream.write(sHTML)
            filestream.close()
        

    # private functions
    def __sBuildHTMLTableLst( self, v_sARefString, v_lstTableContent):
        lstTemp = []
        sHTMLBuiltString = '<TD><BR>' + v_sARefString + '<BR>'
        for sTableContent in v_lstTableContent:
            sHTMLBuiltString += sTableContent + '<BR>'
        sHTMLBuiltString += '</TD>'  
        lstTemp = [sHTMLBuiltString]
        return (lstTemp)


    def __sBuildHTMLTableStringForCategory( self, r_CurrentCategory, v_iTableColumns):

        if self.__dicCategories[r_CurrentCategory] != '':
            # main HTML string for inclusion in report
            sHTML = '<H2>' + r_CurrentCategory + '</H2>'
            
            # Counters for number of inaccessible or accessible files
            iCountAccessible = 0
            iCountAppSpecific = 0
            iCountNonAccessible = 0
            iCountUnknown = 0
            # temporary HTML fields for accessible or Inaccessible HTML strings to be added to sHTML at end of loop
            sHTMLAccessible = '<H3> Known Accessible </H3> <TABLE><TR>'
            sHTMLAppSpecific = '<H3> Application Specific </H3> <TABLE><TR>'
            sHTMLNonAccessible = '<H3> Non-Accessible </H3> <TABLE><TR>'
            sHTMLUnknown = '<H3> Unknown </H3> <TABLE><TR>'

            # dic Categories contains a dic of lists for each image
            for eachSubLst in self.__dicCategories[r_CurrentCategory]:
                for eachListValue in eachSubLst:
                    
                    bAccessible = False
                    bApplicationSpecific = False
                    bNonAccessible = False
                    
                    for eachSearchTerm in self.__lstAppSpecificSearchTerms:
                            # check for all search terms specified in accessible fields
                            if eachListValue.find( eachSearchTerm.strip() ) > 0:
                                print ('true')
                                bApplicationSpecific = True
                                break

                    if bApplicationSpecific == False:
                        for eachSearchTerm in self.__lstNonAccessibleSearchTerms:
                            # check for all search terms specified in accessible fields
                            if eachListValue.find( eachSearchTerm.strip() ) > 0:
                                bNonAccessible = True
                                break

                    if bApplicationSpecific == False and bNonAccessible == False:
                        for eachSearchTerm in self.__lstAccessibleSearchTerms:
                            # check for all search terms specified in accessible fields
                            if eachListValue.find( eachSearchTerm.strip() ) > 0:
                                bAccessible = True
                                break

                    if bApplicationSpecific:
                        iCountAppSpecific += 1
                        # coding to append count of images per category into HTML. Assumes that first lst value will be image </A>
                        iIndex = eachListValue.find('</A>')
                        eachListValue = eachListValue[:iIndex+4] + '<BR>' + str(iCountAppSpecific) + eachListValue[iIndex+4:]                                    
                        sHTMLAppSpecific += eachListValue
                        if iCountAppSpecific % v_iTableColumns == 0:
                            sHTMLAppSpecific += '</TR><TR>'
                    elif bAccessible:
                        iCountAccessible += 1
                        # coding to append count of images per category into HTML. Assumes that first lst value will be image </A>
                        iIndex = eachListValue.find('</A>')
                        eachListValue = eachListValue[:iIndex+4] + '<BR>' + str(iCountAccessible) + eachListValue[iIndex+4:]                                    
                        sHTMLAccessible += eachListValue
                        if iCountAccessible % v_iTableColumns == 0:
                            sHTMLAccessible += '</TR><TR>'
                    elif bNonAccessible:
                        iCountNonAccessible += 1
                        # coding to append count of images per category into HTML. Assumes that first lst value will be image </A>
                        iIndex = eachListValue.find('</A>')
                        eachListValue = eachListValue[:iIndex+4] + '<BR>' + str(iCountNonAccessible) + eachListValue[iIndex+4:]                                    
                        sHTMLNonAccessible += eachListValue
                        if iCountNonAccessible % v_iTableColumns == 0:
                            sHTMLNonAccessible += '</TR><TR>'
                    else:
                        iCountUnknown += 1
                        # coding to append count of images per category into HTML. Assumes that first lst value will be image </A>
                        iIndex = eachListValue.find('</A>')
                        eachListValue = eachListValue[:iIndex+4] + '<BR>' + str(iCountUnknown) + eachListValue[iIndex+4:]                                    
                        sHTMLUnknown += eachListValue
                        if iCountUnknown % v_iTableColumns == 0:
                            sHTMLUnknown += '</TR><TR>'
        
            sHTML += sHTMLAccessible + '</TR></TABLE>' + sHTMLAppSpecific + '</TR></TABLE>' + sHTMLNonAccessible + '</TR></TABLE>' + sHTMLUnknown + '</TR></TABLE>' 
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


    def __sPurgeFileName(self, v_sFileName):
        sTempString = v_sFileName
        sTempString = sTempString.replace("\\", "")
        sTempString = sTempString.replace("/", "")
        return sTempString

                        # # # Start of script  # # #

main()