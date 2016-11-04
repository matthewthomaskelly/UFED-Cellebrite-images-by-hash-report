# *******************************************************************
# ** Name:          UFED tag images by hash
# ** Version:       v1.4
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and tag those images located.
#    11/05/2016      - Amended purpose to include writing HTML report.
#    20/05/2016		 - Amended coding to include PIL and to produce thumbs rather than original images in report 
#    30/08/2016      - 1.3 - Changed reference to PIL to CLR Image as UFED Python uses IronPython 2.6 and PIL not supported.
#    21/09/2016      - 1.4 - Form function to select report location and CSV file location
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
#import json

# from physical import *
import os
import hashlib
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *
from System.Drawing import *

# contains IntPtr type
from System import IntPtr

# # # function definitions # # # 

# *******************************************************************
# ** Name:          main()
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and tag those images located.
# ** Returns:       None - file located and not-located or duplicates will be logged.
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          06/05/2015
# ** Revisions:     none
# ******************************************************************
def main():

    # Get location of CSV file and path for log file
    # 06/05/2016 hard coded at this point
    #sCSVFileLoc = strSelectFile()
    #sExportReportLoc = strSelectFolder()
    frmMain = IForm()
    Application.Run(frmMain)
    sCSVFileLoc = frmMain.FolderPath

    #sExportReportLoc = strSelectFolder()
    sImagesRelLoc = '\\Images'
    sThumbRelLoc = '\\Thumbs'
    sReportName = 'report.html'

    # class 'Images' of Data Files
    objImageFiles = ds.DataFiles['Image']
    # Open specified CSV file
    # Open CSV file and locate column linked to MD5 values
    objCSVFile = open(sCSVFileLoc)
    objHTMLWrite = clsHTMLWriter()
    iLineCount = 1
    for eachLine in objCSVFile:
        # split the contents of eachline using ',' deliminator. 
        eachLineSplit = eachLine.split(',')
        # read first line and locate at what index the HASH value is stored for comparison
        if iLineCount == 1:
            print( 'Getting Index Values' )
            iLen = len(eachLineSplit)
            eachLineSplit[iLen-1] = eachLineSplit[iLen-1].strip()
            iHASHIndex = eachLineSplit.index('Hash Value')
            iCategoryIndex = eachLineSplit.index('Category')
        else:
            print( 'Getting matching Hashes Index' )
            # Iterate through each image and locate matching MD5 values
            eachLineSplit[iHASHIndex] = eachLineSplit[iHASHIndex].lower()
            for eachImage in objImageFiles:
                strMD5 = eachImage.Md5
                if strMD5 == '':
                    strMD5 = getMd5HashValue(eachImage)
                if strMD5  == eachLineSplit[iHASHIndex].strip():
                    print( 'Match!' + strMD5 )
                    # save image to images location
                    try:
                        exportUFEDFile(eachImage, sExportReportLoc + sImagesRelLoc)
                    except:
                        print('Error writing file!')
                    # 19/07/2016 - code for PIL indescrepencies.
                    # objImageFile = PIL.Image.open( sExportReportLoc + sImagesRelLoc + '/' + eachImage.Name )
                    # objImageFile.open(sExportReportLoc + sImagesRelLoc + '/' + eachImage.Name)
                    # shrink image to specified size and then display this thumbnail in report and reference full sized image
                    # 30/08/2016 PIL will not work as UFED uses IronPython. Use CLR Image instead
                    objImageFile = Image.FromFile(sExportReportLoc + sImagesRelLoc + '\\' + eachImage.Name)
                    objThumbImage = resizeImage(objImageFile)
                    print (sExportReportLoc + sThumbRelLoc + '\\' + eachImage.Name)
                    
                    try:
                        objThumbImage.Save(sExportReportLoc + sThumbRelLoc + '\\' + eachImage.Name)
                    except:
                         print('error creating thumbnail')
                         
                    objThumbImage.Dispose
                    objImageFile.Dispose

                    sThumbName = eachImage.Name
                    # add relative path to HTML
                    objHTMLWrite.AddImageLocationReference(eachLineSplit[iCategoryIndex], sImagesRelLoc + '\\' + sThumbName, sImagesRelLoc + '\\' + eachImage.Name)
                    # add file information to table content
                    lstDetails = [eachImage.Name, eachImage.Md5]
                    objHTMLWrite.AddTableContentByKeyAsLists( eachLineSplit[iCategoryIndex], lstDetails )

        print( str(iLineCount) + ' ' + eachLineSplit[iHASHIndex] )
        iLineCount += 1
        # No match - log?
       
    # close CSV file
    objCSVFile.close()

    # Write built HTML stream to file location
    print(sExportReportLoc + '\\' +  sReportName)
    objHTMLWrite.WriteHTMLtoFile(sExportReportLoc + '\\' + sReportName)

def resizeImage (r_objImage):
    xTo, yTo = 100, 100
    xNow, yNow = r_objImage.Width, r_objImage.Height
    if xNow <= xTo and yNow <= yTo:
        objResizeImage = r_objImage
        return objResizeImage
    else:
        pX = xNow / xTo
        pY = yNow / yTo
        objThumnailImageAbort = r_objImage.GetThumbnailImageAbort(ThumbnailCallBack)
        if pX > pY:
            objResizeImage = r_objImage.GetThumbnailImage ( int(xNow / pX), int(yNow / pX), objThumnailImageAbort, IntPtr(0))
        else:
            objResizeImage = r_objImage.GetThumbnailImage ( int(xNow / pY), int(yNow / pY), objThumnailImageAbort, IntPtr(0) )
        return objResizeImage 

def ThumbnailCallBack():
    return False

def getMd5HashValue (r_objImageFile):

    #print (objImageFile.ToString())
    hash = hashlib.md5()
    try:
        rd = r_objImageFile.read()
        hash.update(rd)
        hexMD5 = hash.hexdigest()
        return hexMD5.upper
    except:
        return ''
    
def strSelectFolder():
    dialog = FolderBrowserDialog()
    if ( dialog.ShowDialog() == DialogResult.OK):
        return dialog.SelectedPath

def strSelectFile():
    dialog = OpenFileDialog()
    dialog.Filter = "CSV files (*.csv)|*.csv"
    if ( dialog.ShowDialog() == DialogResult.OK ):
        return dialog.FileName

class IForm(Form):
        def __init__(self):
                dialog = FolderBrowserDialog()
                if ( dialog.ShowDialog() == DialogResult.OK):
                    self.FolderPath = dialog.SelectedPath
                pass


# *******************************************************************
# ** Name:          exportUFEDFile
# ** Purpose:       Takes an Image from ds in UFED Cellebrite and exports to file-path specified
# ** Author:        Unknown - MET Police
# ** Date:          
# ** Revisions:     06/05/2016 - removed hash library reference
# ****************************************************************** 
def exportUFEDFile(pic,path):
        print(path)
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
        print(filePath)
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



# # # class definitions # # # 

# *******************************************************************
# ** Name:          clsHTMLWriter
# ** Purpose:       A class to store HTML data in tables by Category stored in a dictionary for each Category.
#                   Includes a function to write HTML page at conclusion to specified location for report.
# ** Author:        Matthew KELLY
# ** Date:          11/05/2015
# ** Revisions:     19/07/2016 - amended functions AddTableContentByKeyAsLists() and AddImageLocationReference() to include private
#                    function call __AddToDicCategories() that checks whether dictionary key exists before adding to Category dictionary
# ******************************************************************
class clsHTMLWriter:

    def __init__(self):
        self.__sHeading = 'South Yorkshire Police Case Report'
        self.__dicCategories = {'Category A':'', 'Category B':'', 'Category C':''}

    def AddHeadingTitle(self, v_sHeading):
        self.__sHeading = v_sHeading

    def AddTableContentByKeyAsLists(self, v_sKey, v_sTableContent):
        # nested dictionary for each Category image
        # 19/07/2016 - added code for if v_sKey does not exist
        sHTMLBuiltString = self.__sBuildHTMLTableRowString(v_sTableContent)
        self.__AddToDicCategories(v_sKey, sHTMLBuiltString)
     
    def AddImageLocationReference(self, v_sKey, v_sThumbRelativeLocation, v_sImageRelativeLocation = ''):
        sHTMLBuiltString = '<TR><TD><A href=.' + v_sImageRelativeLocation
        if v_sImageRelativeLocation != '':
            sHTMLBuiltString += '<A href=.' + v_sImageRelativeLocation
        sHTMLBuiltString += '<IMAGE src=.' + v_sThumbRelativeLocation + '>'
        sHTMLBuiltString += '</A></TD></TR>'
        self.__AddToDicCategories(v_sKey, sHTMLBuiltString)
    
    def WriteHTMLtoFile(self, v_sFileLocation):
        #print(v_sFileLocation)
        filestream = open(v_sFileLocation, 'w')
        sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'
        for eachCategory in self.__dicCategories:
            if self.__dicCategories[eachCategory] != '':
                sHTML += '<H2>' + eachCategory + '</H2>'
                sHTML += '<TABLE>'
                sHTML += self.__dicCategories[eachCategory]
                sHTML += '</TABLE>'
        sHTML += '</HTML>'
        filestream.write(sHTML)
        filestream.close()

    # private functions
    def __sBuildHTMLTableRowString(self, v_sTableContent):
        sHTMLBuiltString = '<TR>'
        for sTableContent in v_sTableContent:
            print(sTableContent)
            sTableContent = '<TD>' + str(sTableContent) + '</TD>'
            sHTMLBuiltString += str(sTableContent)
            sHTMLBuiltString += '</TR>'
        return (sHTMLBuiltString)

    def __AddToDicCategories(self, v_sKey, v_sHTMLBuiltString):
        if v_sKey in self.__dicCategories:
            self.__dicCategories[v_sKey] += v_sHTMLBuiltString
        else:
            self.__dicCategories[v_sKey] = v_sHTMLBuiltString


# # # Start of script  # # #
main()