#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from subprocess import call
import sqlite3 
import sys

# sqlite queries return annoying utf-8 lists [u'foo, u'bar]
def utf2str(x):
	return map(str, x)

# print lists of strings nicely 
def printer(a):
	# a is a list, fx [["giraffe", "africa"], ["wolf", "germany"]]
	# max col length for that list would return [7, 7]
	# because giraffe is 7 letters and germany is 7
	max_col_lengths = map(lambda y: max(map(lambda x: len(x[y]), a)), range(0,len(a[0])))
	max_col_lengths = map(lambda x: x+2, max_col_lengths)

	# create the right format
	formatted = map(lambda x: '{:>' + str(x) + '}', max_col_lengths)
	print ''
	for i in a:
		l = map(lambda x: formatted[x].format(i[x]), range(0,len(i)))
		print ''.join(l) 

# connect to database
def connect_to_gitty():
	# magic to get homedirectory
	home_dir = expanduser("~")

	conn = sqlite3.connect(home_dir + "/.two_giraffes.db")
	cursor = conn.cursor()
	return conn, cursor
	
# create database
def create_gitty_db(x):
	tablename = 'create table if not exists gitty('
	name = 'repo_name varchar(20),'
	link = 'repo_link varchar(100),'
	location = 'location varchar(100),'
	status = 'status varchar(100));'
	conn, cursor = connect_to_gitty()
	with conn: 
		cursor.execute(tablename + name + link + location + status)

# view repos in database
def repos(x):
	header = []
	query = ''

	# check for arguments in call
	if any('n' in s for s in x):
		query += ' repo_name,'
		header = header + ["Repo"]
	if any('l' in s for s in x):
		query += ' repo_link,'
		header = header + ["URL"]
	if any('d' in s for s in x):
		header = header + ["Location"]
		query += ' location'
	if any('s' in s for s in x):
		header = header + ["Status"]
		query += ' status,'

	if len(query) == 0:
		query = ' * '
		header = ["Repo", "URL", "Location", "Status"]
	else:
		# remove trailing comma
		query = query[0:len(query)-1] + ' '

	conn, cursor = connect_to_gitty()
	with conn:
		cursor.execute('SELECT %s FROM gitty;' % query)
		r = cursor.fetchall()
		r = map(utf2str, r)
		r = [header] + r
		printer(r)

# clone a repo
def clone(x):
	if len(x) != 3:
		print 'repo_name '
		name = raw_input(' ')
		print 'repo_link '
		link = raw_input(' ')
		print 'destination '
		destination = raw_input(' ')
	else: 
		name = str(x[0])
		link = str(x[1])
		destination = str(x[2])

	status = 'ok'

	conn, cursor = connect_to_gitty()
	with conn:
		cursor.execute('INSERT INTO gitty values(?,?,?,?);', (name, link, destination, status))

	if not os.path.exists(destination):
		os.makedirs(destination)

	os.chdir(destination)
	os.system('git clone ' + link + ' ' + destination)

def push(x):
	if len(x) != 1:
		name = raw_input('Repo name: ')
	else: 
		name = x[0]

	print name
	conn, cursor = connect_to_gitty()
	with conn:
		cursor.execute("SELECT repo_name, repo_link, destination FROM gitty where repo_name is '%s'" % name )
		r = cursor.fetchall()
		r = map(utf2str, r)
		if len(r) == 0:
			cursor.execute("SELECT repo_name FROM gitty;")
			r = cursor.fetchall()
			r = map(utf2str, r)
			print "Repo does not exist in database"
			print "Repos are"
			printer(r)
			return 

	print "Commiting"
	printer([["Repo", "URL", "Location"]] + r)
	print ""
	commit = raw_input("Commit message? ")

	r = r[0]
	repo_link = r[1]
	destination = r[2]
	
	os.chdir(destination)
	os.system('git init')
	os.system('git add .')
	os.system('git commit -m "'+ commit + '"')
	os.system('git push origin master')


	#os.system('clear')

# start the command line version
def cli(x):
	print 'Welcome to GITTY, my dude'
	print 'What do you want to do?'
	print '(1)	Check Repos'
	print '(2)	Clone repo'
	print '(3)	Push'
	print '(4)	Exit'
	x = int(raw_input(' '))

	if x == 1:
		repos([])
	elif x == 2:
		clone([])
	elif x == 3:
		push([])



func = {'push':push, 'repos':repos,'clone':clone, 'cli':cli, 'create_gitty_db':create_gitty_db}

if __name__ == "__main__":
	cli([]) if len(sys.argv) == 1 else func[sys.argv[1]](sys.argv[2:])
	



# operations:
# cli
# list repos  n = name, l = link,  location status
# pull optional repo name
# push  optional repo name commit message
# checkout
# reset
# clone optional repo_name url folder
# log optional number_of_commits view_diff
