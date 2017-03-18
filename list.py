#!/usr/bin/python
import MySQLdb
from Tkinter import *

class DatabaseManager(object):
	__inst = None
	__connection = None

	@staticmethod
	def inst():
		if DatabaseManager.__inst == None:
			DatabaseManager.__inst = DatabaseManager()
		return DatabaseManager.__inst

	def __init__(self):
		self.__connection = MySQLdb.connect(host="localhost", user="root", passwd="fishkiller", db="todolist", autocommit = True)
	
	def read_all(self, table):
		cur = self.__connection.cursor()
		cur.execute('Select * from ' + table + ';')
		return cur.fetchall()
			

	def read_columns(self, table, cols):
		fields = ','.join(map(str, cols))

		cur = self.__connection.cursor()
		cur.execute('select ' + fields + ' from ' + table + ';')
		return cur.fetchall()
			
	def update(self, table, id, cols, values):
		query = 'update ' + table + ' set '
		for i in range(len(cols)):
			s = cols[i] + '=' + values[i] + ','
			query += s
		query = query[: -1]
		query += ' where id=' + id + ';'
		cur = self.__connection.cursor()
		cur.execute(query)

	def insert(self, table, cols, values):
		query = 'insert into ' + table +'('
		query += ", ".join(cols) + ') values('
		for i in range(len(values)):
			values[i] = "'" + values[i] + "'"
		query += ", ".join(values) + ');'
		cur = self.__connection.cursor()
		cur.execute(query)
		return cur.lastrowid


	def remove(self, table, cols, values):
		query = 'delete from ' + table + ' where '
		for i in range(len(cols)):
			s = str(cols[i]) + ' = ' + str(values[i]) + ' and '
			query += s
		query = query[:-5]
		query += ';'
		cur = self.__connection.cursor()
		cur.execute(query)

class EntryModel:
	__id = None
	__text = None
	__state = None
	__tableName = None
	__database = None
	def __init__(self, tableName, entry):
		self.__id = entry[0]
		self.__text = entry[1]
		self.__state = entry[2]
		self.__tableName = tableName

	def getData(self):
		return [self.__id, self.__text, self.__state]

	def getId(self):
		return self.__id

	def getText(self):
		return self.__text

	def getState(self):
		return self.__state

	def setText(self, text):
		self.__database = DatabaseManager.inst()
		self.__database.update(self.__tableName, self.__id, ['text'], [text])
	
	def changeState(self):
		self.__database = DatabaseManager.inst()
		if self.__state == 1:
			self.__database.update(self.__tableName, self.__id, ['state'], [0])
		else:
			self.__database.update(self.__tableName, self.__id, ['state'], [1])


class ListModel:
	__database = None
	__tableName = None
	__elements = []
	
	def __init__(self, tableName):
		self.__database = DatabaseManager.inst()
		self.__tableName = tableName
		records = self.__database.read_all(self.__tableName)
		for e in records:
			self.__elements.append(EntryModel(self.__tableName, e))

	def getList(self):
		return self.__elements

	
	def createEntry(self, text):
		id = self.__database.insert(self.__tableName, ['text'], [text])
		self.__elements.append(EntryModel(self.__tableName, [id, text, 0]))
	
	def removeEntry(self, id):
		self.__database.remove(self.__tableName, ['id'], [id])
		for e in self.__elements:
			if e.getId() == id:
				self.__elements.remove(e)
				return True
		return False	

	def setText(self, id, text):
		self.__database.update(self.__tableName, id, ['text'], [text])
		for e in self.__elements:
			if e.getId() == id:
				e.setText(text)
				return True
		return False

	def changeState(self, id):
		new_state = 0
		for e in self.__elements:
			if e.getId() == id:
				self.__database.update(self.__tableName, id, ['state'], [e.changeState()])
				return True
		return False	

class EntryFrame(object):
	__root = None
	__entry = None
	__list = None
	__state = 0

	def saveEntry(self):
		return True
	
	def changeState(self):
		return True

	def removeEntry(self):
		return True			

	def getEntry(self):
		return self.__entry

	def __init__(self, root, listM, e):
		self.__root = root
		self.__list = listM
		self.__entry = e

		eF = Frame(self.__root, bg='white')
		eCheck = Checkbutton(eF, variable=self.__state, onvalue=1, offvalue=0)
		eText = Text(eF, height=1,width=20,font='Ubuntu 14',wrap=WORD)
		eText.insert(0.0, self.__entry.getText())
		eRemoveBtn = Button(eF, text=u'Remove')

		eF.pack() 
		eCheck.pack()
		eText.pack()
		eRemoveBtn.pack()
		eF.pack()

class ListModelFrame(object):
	__root = None
	__dataModel = None
	__entrysRoot = None

	def render(self):
		for e in self.__dataModel.getList():
			eF = EntryFrame(self.__entrysRoot, self.__dataModel, e)
		self.__entrysRoot.pack()	

	def __init__(self, root, dataModel):
		self.__root = root
		self.__dataModel = dataModel

		listMF = Frame(self.__root, bg='white')

		self.__entrysRoot = Frame(listMF, bg='white')
		self.render()

		buttonsFrame = Frame(listMF, bg='white')
		addButton = Button(buttonsFrame, text=u'Add')

		listMF.pack()
		buttonsFrame.pack()
		addButton.pack()


window = Tk()
dataModel = ListModel('list')
dataObject = ListModelFrame(window, dataModel)
window.mainloop()