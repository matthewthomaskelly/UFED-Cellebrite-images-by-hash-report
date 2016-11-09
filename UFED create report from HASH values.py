# *******************************************************************
# ** Name:          UFED create report from HASH values
# ** Version:       v2.0
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and create a report with images located.
#     09/11/2016     - 2.0 - First working release to HTCU
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

    # Get location of CSV file and path for log file
    frmCSVFolder = IForm()
    Application.Run( frmCSVFolder )
    sCSVFileLoc = frmCSVFolder.CSVfilepathname
    sExportReportLoc = frmCSVFolder.folderpathname
    
    sImagesRelLoc = '\\Images'
    sThumbRelLoc = '\\Thumbs'
    sReportName = 'report.html'

    # class 'Images' of Data Files
    objImageFiles = ds.DataFiles['Image']
    # HTML parser attempt, could do with some work!
    objHTMLWrite = clsHTMLWriter()

    # Open specified CSV file
    # Open CSV file and locate column linked to MD5 values
    objCSVFile = open( sCSVFileLoc )
    
    # first line is the headings
    iLineCount = 1
    for eachLine in objCSVFile:

        # split the contents of eachline using ',' deliminator. 
        eachLineSplit = eachLine.split(',')

        # read first line and locate at what index the HASH value is stored for comparison
        if iLineCount == 1:
            iLen = len(eachLineSplit)
            eachLineSplit[iLen-1] = eachLineSplit[iLen-1].strip()
            iHASHIndex = eachLineSplit.index('Hash Value')
            iCategoryIndex = eachLineSplit.index('Category')
        else:
            # convert HASH value to lowercase for match in UFED reader
            eachLineSplit[iHASHIndex] = eachLineSplit[iHASHIndex].lower()

            # Iterate through each image and locate matching MD5 values
            for eachImage in objImageFiles:

                strMD5 = eachImage.Md5
                # calculate HASH value if not in Cellebrite UFED
                if strMD5 == '':
                    strMD5 = getMd5HashValue(eachImage)

                if strMD5  == eachLineSplit[iHASHIndex].strip():

                    # save image to images location
                    try:
                        exportUFEDFile(eachImage, sExportReportLoc + sImagesRelLoc)
                    except:
                        print('Error writing file!')

                    # shrink image to specified size and then display this thumbnail in report and reference full sized image
                    objImageFile = Image.FromFile(sExportReportLoc + sImagesRelLoc + '\\' + eachImage.Name)
                    objThumbImage = resizeImage(objImageFile)
                    sThumbName = eachImage.Name + '.png'
                    try:
                        objThumbImage.Save(sExportReportLoc + sThumbRelLoc + '\\' + sThumbName)
                    except:
                         print('error creating thumbnail')
                         
                    objThumbImage.Dispose
                    objImageFile.Dispose

                    # add relative path to HTML
                    sFullThumbPath = sThumbRelLoc + '\\' + sThumbName
                    sFullImagePath = sImagesRelLoc  + '\\' + eachImage.Name

                    # add file information to table content
                    lstDetails = ['Name: ' + eachImage.Name, 'Path@ ' + eachImage.Folder, 'Creation date: ' + str(eachImage.CreationTime), 'MD5: ' + eachImage.Md5 ]
                    objHTMLWrite.AddTableContentByKeyAsLists( eachLineSplit[iCategoryIndex], sFullThumbPath, sFullImagePath, lstDetails )

        iLineCount += 1
        # No match - log?
       
    # close CSV file
    objCSVFile.close()

    # Write built HTML stream to file location
    print(sExportReportLoc + '\\' +  sReportName)
    objHTMLWrite.WriteHTMLtoFile(sExportReportLoc + '\\' + sReportName, 4)


# *******************************************************************
# ** Name:          resizeImage
# ** Purpose:       
# ** Author:        Matthew KELLY
# ** Date:          
# ** Revisions:     Originally used PIL, but incompatible with IronPython.
#                   Used CLR instead
# ****************************************************************** 
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

# *******************************************************************
# ** Name:          ThumbnailCallBack
# ** Purpose:       Used by Resize Image to return false
# ** Author:        Matthew KELLY
# ****************************************************************** 
def ThumbnailCallBack():
    return False

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
                self.Height = 150
                self.Width = 500

                #add button
                self.button1 = Button()
                self.button1.Text = "&OK"
                self.button1.Location = Point(10, 60)
                self.button1.Click += self.OKPressed

                #add textbox for CSV file
                self.textboxfile = TextBox()
                self.textboxfile.Text = "CSV file location goes here"
                self.textboxfile.Location = Point(10,10)
                self.textboxfile.Width = 450

                #add textbox for report folder location
                self.textboxfolder = TextBox()
                self.textboxfolder.Text = "Proposed report folder Path goes here"
                self.textboxfolder.Location = Point(10,35)
                self.textboxfolder.Width = 450

                self.Controls.Add(self.textboxfile)
                self.Controls.Add(self.textboxfolder)
                self.Controls.Add(self.button1)
                self.CenterToScreen()

                self.folderpathname = ""
                self.CSVfilepathname = ""     

        def OKPressed(self, sender, args):
                strCSVFile = self.textboxfile.Text
                strReport = self.textboxfolder.Text
                if ( os.path.isfile( strCSVFile ) == False ):
                        MessageBox.Show( "The specified CSV file does not exist, please choose another." , "Invalid Directory" )
                elif ( os.path.isdir( strReport ) == False ):
                        r = MessageBox.Show( "Folder path for report location does not exist. Would you like to create it?", "Invalid Directory", MessageBoxButtons.YesNo, MessageBoxIcon.Question )
                        if r == DialogResult.Yes:
                                os.mkdir(strReport)
                                os.mkdir(strReport + "\Images")
                                os.mkdir(strReport + "\Thumbs")
                                self.folderpathname = strReport
                                self.CSVfilepathname = strCSVFile
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
     
    def WriteHTMLtoFile(self, v_sFileLocation, v_iTableColumns=3):)
        filestream = open(v_sFileLocation, 'w')
        sHTML = '<HTML><H1>' + self.__sHeading + '</H1>'
        for eachCategory in self.__dicCategories:
            if self.__dicCategories[eachCategory] != '':
                sHTML += '<H2>' + eachCategory + '</H2>'
                sHTML += '<TABLE>' + '<TR>'
                iCount = 0
                for eachSubLst in self.__dicCategories[eachCategory]:
                    iCount += 1
                    for eachListValue in eachSubLst:
                        sHTML += eachListValue
                    if iCount % v_iTableColumns == 0:
                        sHTML += '</TR><TR>'
                sHTML += '</TR></TABLE>'
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