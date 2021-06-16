#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BSD 2-Clause License

Copyright (c) 2020-2021, The FreeBSD Project
Copyright (c) 2020-2021, Sergio Carlavilla <carlavilla@FreeBSD.org>

This script will generate the Table of Contents of any [example]s in the
books.
"""

import sys, getopt
import re
import os.path

languages = []

"""
To determine if a chapter is a chapter we are going to check if it is
anything else, an appendix, a part, the preface ... and if it is not
any of those, it will be a chapter.

It may not be the best option, but it works :)
"""
def checkIsChapter(chapter, chapterContent):
  if "part" in chapter:
    return False
  elif "[preface]" in chapterContent:
    return False
  elif "[appendix]" in chapterContent:
    return False
  else:
    return True

def setTOCTitle(language):
  languages = {
    'en': 'List of Examples',
    'de': 'Liste der Beispiele',
    'el': 'Κατάλογος Παραδειγμάτων',
    'es': 'Lista de ejemplos',
    'fr': 'Liste des exemples',
    'hu': 'A példák listája',
    'it': 'Lista delle tabelle',
    'ja': '例の一覧',
    'mn': 'Жишээний жагсаалт',
    'nl': 'Lijst van voorbeelden',
    'pl': 'Spis przykładów',
    'pt-br': 'Lista de Exemplos',
    'ru': 'Список примеров',
    'zh-cn': '范例清单',
    'zh-tw': '範例目錄'
  }

  return languages.get(language)

def main(argv):

  justPrintOutput = False
  langargs = []
  try:
    opts, args = getopt.gnu_getopt(argv,"hl:o",["language="])
  except getopt.GetoptError:
    print('books-toc-examples-creator.py [-o] -l <language>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('books-toc-examples-creator.py [-o] -l <language>')
      sys.exit()
    if opt == '-o':
      justPrintOutput = True
    elif opt in ("-l", "--language"):
      langargs = arg.replace(" ",",").split(',')

  # treat additional arguments as languages, but check if they
  #  contain ','
  for l in args:
    langargs.extend(l.replace(" ",",").split(','))

  for language in langargs:

    if not os.path.exists('./content/{}/books/books.adoc'.format(language)):
      if not justPrintOutput:
        print('Warning: no books found for language "{0}"'.format(language))
      continue

    with open('./content/{}/books/books.adoc'.format(language), 'r', encoding = 'utf-8') as booksFile:
      books = [line.strip() for line in booksFile]

      for book in books:
        with open('./content/{0}/books/{1}/chapters-order.adoc'.format(language, book), 'r', encoding = 'utf-8') as chaptersFile:
          chapters = [line.strip() for line in chaptersFile]

        toc =  "// Code @" + "generated by the FreeBSD Documentation toolchain. DO NOT EDIT.\n"
        toc += "// Please don't change this file manually but run `make` to update it.\n"
        toc += "// For more information, please read the FreeBSD Documentation Project Primer\n\n"
        toc += "[.toc]\n"
        toc += "--\n"
        toc += '[.toc-title]\n'
        toc += setTOCTitle(language) + '\n\n'

        chapterCounter = 1
        exampleCounter = 1
        for chapter in chapters:
          with open('./content/{0}/books/{1}/{2}'.format(language, book, chapter), 'r', encoding = 'utf-8') as chapterFile:
            chapterContent = chapterFile.read().splitlines()
            chapterFile.close()
            chapter = chapter.replace("/_index.adoc", "").replace(".adoc", "").replace("/chapter.adoc", "")

            exampleId = ""
            exampleTitle = ""
            for lineNumber, chapterLine in enumerate(chapterContent, 1):
              if re.match(r"^\[example\]+", chapterLine) and re.match(r"^[.]{1}[^\n]+", chapterContent[lineNumber-2]) and re.match(r"^\[\[[^\n]+\]\]", chapterContent[lineNumber-3]):
                  exampleTitle = chapterContent[lineNumber-2]
                  exampleId = chapterContent[lineNumber-3]

                  if book == "handbook":
                    toc += "* {0}.{1}  link:{2}#{3}[{4}]\n".format(chapterCounter, exampleCounter, chapter, exampleId.replace("[[", "").replace("]]", ""), exampleTitle[1:])
                  else:
                    toc += "* {0}.{1}  link:{2}#{3}[{4}]\n".format(chapterCounter, exampleCounter, "", exampleId.replace("[[", "").replace("]]", ""), exampleTitle[1:])


                  exampleCounter += 1
              else:
                exampleId = ""
                exampleTitle = ""

            if checkIsChapter(chapter, chapterContent):
              chapterCounter += 1
            exampleCounter = 1 # Reset example counter

        toc += "--\n"

        if justPrintOutput == False:
          with open('./content/{0}/books/{1}/toc-examples.adoc'.format(language, book), 'w', encoding = 'utf-8') as tocFile:
            tocFile.write(toc)
        else:
          print('./content/{0}/books/{1}/toc-examples.adoc'.format(language, book))

if __name__ == "__main__":
  main(sys.argv[1:])
