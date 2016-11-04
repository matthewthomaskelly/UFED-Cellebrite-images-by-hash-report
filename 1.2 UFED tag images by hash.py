# *******************************************************************
# ** Name:          UFED tag images by hash
# ** Version:       v1.2
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and tag those images located.
#    11/05/2016      - Amended purpose to include writing HTML report.
#    20/05/2016		 - Amended coding to include PIL and to produce thumbs rather than original images in report 
# ** Returns:       None - file located and not-located or duplicates will be logged.
# ** Variables:     N/A
# ** Author:        Matthew KELLY
# ** Date:          06/05/2015
# ** Revisions:     none
# ******************************************************************

# Imports
import os
from PIL import Image

# # # Start of script  # # #
main()

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
    sCSVFileLoc = 'C:\\mtk\\DFU-184-2016 RM-1 Illegal Files 10052016.csv'
    sExportReportLoc = 'C:\\mtk\\Report'
    sImagesRelLoc = '.\Images'
    sThumbRelLoc = '.\Thumbs'
    sReportName = 'report.html'

    # class 'Images' of Data Files
    objImageFiles = ds.DataFiles['Image']
    # Open specified CSV file
    # Open CSV file and locate column linked to MD5 values
    objCSVFile = open(sCSVFileLoc)
    objHTMLWrite = clsHTMLWriter()

    for eachLine in objCSVFile:
        # split the contents of eachline using ',' deliminator. Category is first, MD5 second.
        eachLineSplit = eachLine.split(',')
        #print(eachLineSplit[0] + ' ' + eachLineSplit[1])
        # Iterate through each image and locate matching MD5 values
        for eachImage in objImageFiles:
            eachLineSplit[1] = eachLineSplit[1].lower()
            if eachImage.Md5  == eachLineSplit[1].strip():
                # save image to images location
                exportUFEDFile(eachImage, sExportReportLoc + sImagesRelLoc)
                objImageFile = Image
                objImageFile.open(sExportReportLoc + sImagesRelLoc + '/' + eachImage.Name)
                # shrink image to specified size and then display this thumbnail in report and reference full sized image
                objThumbImage = resizeImage(objImageFile)
                objThumbImage.save(sExportReportLoc + sThumbRelLoc + '/' + objImage.Name)
                objThumbImage.close
                objImageFile.Close
                # add relative path to HTML
                objHTMLWrite.AddImageLocationReference(eachLineSplit[0], sThumbRelLoc + '\\' + sThumbName, sImagesRelLoc + '\\' + eachImage.Name)
                # add file information to table content
                lstDetails = [eachImage.Name, eachImage.Md5]
                objHTMLWrite.AddTableContentByKeyAsLists( eachLineSplit[0], lstDetails )
        # No match - log?
       
    # close CSV file
    objCSVFile.close()

    # Write built HTML stream to file location
    print(sExportReportLoc + sReportName)
    objHTMLWrite.WriteHTMLtoFile(sExportReportLoc + '\\' + sReportName)

def resizeImage(r_objImage):
    xTo, yTo = 300, 400
    xNow, yNow = r_objImage.Width, r_objNow.Height
    if xNow <= xTo and yNow <= yTo:
        return ''
    else:
        pX = xNow / xTo
        pY = yNow / yTo
        if pX > pY:
            objResizeImage = r_objImage.resize((int(xNow / pX)), int(yNow / pX))
        else:
            objResizeImage = r_objImage.resize((int(xNow / pY)), int(yNow / pY)
        return objResizeImage
            
def exportUFEDFile(pic,path):
        fileDataReadsize = 2**25
        fileSize = pic.Size
        if (fileSize > 2113929216):
                MessageBox.Show("%s is greater than 2GB, please review manually. Filename stored in trace window" % (pic.Name),"Error")
                print ("File %s is over 2gb in size, review manually" % (pic.Name))
                return "", ""
       # m = hashlib.md5()
        filename = pic.Name 
        filePath = os.path.join(path,filename)
        ext = os.path.splitext(pic.Name)[1]
        locateInvalidChar = ext.find("?")
        if (locateInvalidChar != -1):
                ext = ext[:locateInvalidChar]
        f = open(filePath,'wb')
        pic.seek(0)
        filedata = pic.read(fileDataReadsize)
        while len(filedata) > 0:
                #m.update(filedata)
                f.write(filedata)
                filedata = pic.read(fileDataReadsize)
        pic.seek(0)
        f.close()




# # # class definitions # # # 
# *******************************************************************
# ** Name:          clsHTMLWriter
# ** Purpose:       A short script to open exported CSV separated export from NetClean of categorised images including MD5 value.
#					The script will iterate through each image file witin an extraction and tag those images located.
#    11/05/2016      - Amended purpose to include writing HTML report.
# ** Author:        Matthew KELLY
# ** Date:          11/05/2015
# ** Revisions:     none
# ******************************************************************
class clsHTMLWriter:

    def __init__(self):
        self.__sHeading = 'South Yorkshire Police Case Report'
        self.__dicCategories = {'Category A':'', 'Category B':'', 'Category C':''}

    def AddHeadingTitle(self, v_sHeading):
        self.__sHeading = v_sHeading

    def AddTableContentByKeyAsLists(self, v_sKey, *v_sTableContent):
        # nested dictionary for each Category image
        sHTMLBuiltString = self.__sBuildHTMLTableRowString(v_sTableContent)
        self.__dicCategories[v_sKey] += sHTMLBuiltString
     

    def AddImageLocationReference(self, v_sKey, v_sThumbRelativeLocation, v_sImageRelativeLocation = ''):
        sHTMLBuiltString = '<TR><TD>'
        sHTMLBuiltString += '<IMAGE src="' + v_sThumbRelativeLocation + ' href:=' + v_sImageRelativeLocation + '>')
        sHTMLBuiltString += '</TD></TR>'
        self.__dicCategories[v_sKey] += sHTMLBuiltString

            
    # private function
    def __sBuildHTMLTableRowString(self, *v_sTableContent):
        sHTMLBuiltString = '<TR>'
        for sTableContent in v_sTableContent:
            sTableContent = '<TD>' + str(sTableContent) + '</TD>'
            sHTMLBuiltString += str(sTableContent)
            sHTMLBuiltString += '</TR>'
        return (sHTMLBuiltString)

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
