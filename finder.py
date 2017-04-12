#coding=utf-8
'''
该程序用于对本地的文献建立索引，从而易于依据关键字进行查询
'''
import sys,os,sqlite3

dbName = 'files.db'
#本地文件列表
filesList = []

#查询所有的数据
def  queryAllFiles():
    allFilesInDb = []
    sqDbConn = sqlite3.connect(dbName)
    try:
        #createTabel = 'SELECT * FROM FILES WHERE FILENAME='
        selectCmd = 'SELECT * FROM FILES'
        cur = sqDbConn.cursor()
        allFilesInDb = (cur.execute(selectCmd)).fetchall()
    except Exception as e:
        print('查询数据库失败, ', e)
    sqDbConn.close()
    return allFilesInDb

#数据库初始化函数
def init():
    #数据库不存在则创建数据库
    sqDbConn = sqlite3.connect(dbName)
    try:
        createTabel = 'CREATE TABLE IF NOT EXISTS FILES  \
(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,filename VARCHAR(256) NOT NULL,\
keywords VARCHAR(256) ,\
abstract VARCHAR(512) )'
        #表不存在的时候则创建新表
        sqDbConn.execute(createTabel)
        sqDbConn.close()
        #print('初始化数据库成功')
    except Exception as e:
        print('初始化数据库失败, ', e)
        #创建表失败则删除数据库文件
        sqDbConn.close()
        os.remove(dbName)
        return False
    return True

#检查文件是否存在函数
def existFreeFile():
    freeFileList = []
    fileList = os.listdir()
    fileList.remove((sys.argv[0].split('\\'))[-1])
    fileList.remove(dbName)
    #print(fileList)
    sqDbConn = sqlite3.connect(dbName)
    filesInDb = [filename[1]  for filename in queryAllFiles()]
    #print(filesInDb)
    freeFileList = [file for file in fileList  if file not in filesInDb]

    return freeFileList

#打印操作命令函数
def printCmd():
    comm = '''0: 索引查询(在文件名、关键字或摘要中进行模糊查询)
1: 插入新文件索引
2: 删除文件索引(按照索引号或文件名完全匹配删除，仅支持单个删除)
3: 修改文件索引
4: 查询数据库中所有文件
q/Q: 退出'''
    freeFileList = existFreeFile()
    if  freeFileList:
        comm +=  '\n提示，目录中有新文件:'
    print(comm)
    for file in freeFileList:
        print( '    ' + file)
    inp = input('请输入命令:')
    return inp

#插入文件索引
def addNewFile():
    freeFileList = existFreeFile()
    filename  = input('请输入文件名:')
    if filename not in freeFileList:
        print('该文件在本地文件夹未找到')
        return False
    ###if filename  in queryAllFiles()
    keywords  = input('请输入文件关键字:')
    abstract = input('请输入文件摘要:')
    dbConn = sqlite3.connect(dbName)
    dbCursor = dbConn.cursor()
    strInsertSql = 'INSERT INTO FILES(filename, keywords, abstract) VALUES (\'' + filename + '\',\'' + keywords + '\',\'' + abstract + '\')'
    print(strInsertSql)
    try:
        dbCursor.execute(strInsertSql)
        print('插入新文件索引成功')
        dbConn.commit()
    except Exception as e:
        print('插入新文件索引失败,', e)
    dbConn.close()

#格式化打印文件内容
def  printFiles(fileList):
    print('ID','\t文件名','\t\t关键字','\t\t\t\t\t\t摘要')
    for file in fileList:
        print('{0}\t{1}\t\t{2}\t\t\t\t\t\t{3}'.format(*file))

#显示数据库中所有文件
def printAllFilesInDb():
    allFilesInDb = queryAllFiles()
    if allFilesInDb:
        printFiles(allFilesInDb)
    else:
        print('数据库中尚未有数据')

#按关键字索引查询
def queryWithKeyWord():
    inp = input('请输入关键字(以空格分隔):')
    strKeywords = [key.strip() for key in inp.split(' ')]
    dbConn = sqlite3.connect(dbName)
    dbCur = dbConn.cursor()
    selSql = ['SELECT  * FROM FILES WHERE filename like \'%{0}%\'',
              'SELECT  * FROM FILES WHERE keywords like \'%{0}%\'',
              'SELECT  * FROM FILES WHERE abstract like \'%{0}%\'']
    matchFilesDict = {}
    try:
        for kw in strKeywords:
            for sql in selSql:
                dbCur.execute(sql.format(kw))
                d = { file[0] : file for file in dbCur.fetchall() }
                matchFilesDict.update(d)
        print('关键字"', inp, '"的搜索结果：')
        printFiles(matchFilesDict.values())
    except Exception as e:
        print('数据库操作失败，', e)

#修改指定文件
def modifyFile():
    inp = input('输入要删除的文件索引号或文件名:')
    isID = True
    if not inp.isdigit():
        isID = False
    try:
        #查询该文件是否在数据库中
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()
        querySql = []
        querySql.append('SELECT * FROM FILES WHERE  filename=\'' + inp + '\'')
        queryFiles = []
        file = ()
        if isID:
            querySql.append('SELECT * FROM FILES WHERE id=' + inp)
        for sql in querySql:
            file = (dbCursor.execute(sql)).fetchone()
            if  file:
                break
        else:
                dbConn.close()
                print('要修改的文件不在数据库中')
                return None
        fileID = file[0]
        while(True):
            confirm = input('确定要修改该文件， Y/N？？？')
            if 'Y' == confirm or 'y' == confirm:
                break
            elif 'N' == confirm or 'n' == confirm:
                dbConn.close()
                return None
        filelist = []
        filelist.append(file)
        print('要修改的文件内容:')
        printFiles(filelist)
        strFileName = input('修改后的文件名(输入空默认不修改):')
        strKeyWords = input('修改后的关键字(输入空默认不修改， 输入\'!clear\'清空):')
        strAbstract = input('修改后的摘要(输入空默认不修改， 输入\'!clear\'清空):')
        if strFileName == '' and strKeyWords == '' and strAbstract == '':
            print('未输入修改信息')
        if strFileName == '':
            strFileName = file[1]
        if strKeyWords == '!clear':
            strKeyWords = ''
        elif strKeyWords == '':
            strKeyWords = file[2]
        if strAbstract == '!clear':
            strAbstract = ''
        elif strAbstract == '':
            strAbstract = file[3]
        updateSql = 'UPDATE files SET filename=\'' + strFileName + '\',' \
                            + ' keywords=\'' + strKeyWords + '\','\
                            + ' abstract=\'' + strAbstract + '\'  where id=' + str(fileID)
        dbCursor.execute(updateSql)
        dbConn.commit()
        print('更新成功')
    except Exception as e:
         print('数据库查询或更新失败  ',  e)
    dbConn.close()

#删除指定文件
def deleteFile():
    inp = input('输入要删除的文件索引号或文件名:')
    isID = True
    if not inp.isdigit():
        isID = False
    try:
        #查询该文件是否在数据库中
        dbConn = sqlite3.connect(dbName)
        dbCursor = dbConn.cursor()
        querySql = ''
        if isID:
            querySql = 'SELECT * FROM FILES WHERE id=' + inp
        else:
            querySql = 'SELECT * FROM FILES WHERE  filename=\'' + inp + '\''
        file = (dbCursor.execute(querySql)).fetchone()
        if not file:
            dbConn.close()
            print('删除的文件不在数据库中')
            return None

        fileID = file[0]
        while(True):
            confirm = input('确定要删除该文件， Y/N？？？')
            if 'Y' == confirm or 'y' == confirm:
                break
            elif 'N' == confirm or 'n' == confirm:
                dbConn.close()
                return None
        deleteSql = 'DELETE FROM FILES WHERE id=' + str(fileID)
        dbCursor.execute(deleteSql)
        dbConn.commit()
        dbConn.close()
        print(' 文件已被删除')
    except Exception as e:
        print('数据库操作失败,' , e)

if __name__ == '__main__':
    if  init():
        #查询本地是否有尚未在数据库中建立索引的文件
        #inp = printCmd()
        while (True ):
            inp = printCmd()
            if  '0' == inp:
                queryWithKeyWord()
            elif  '1' == inp:
                addNewFile()
            elif '2' == inp:
                deleteFile()
            elif  '3' == inp:
                modifyFile()
            elif  '4' == inp:
                printAllFilesInDb()
            elif 'q' == inp or 'Q' == inp:
                break
    else:
         input('数据库不存在并初始化失败，按任意键退出')

