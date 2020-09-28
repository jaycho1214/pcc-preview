from bs4 import BeautifulSoup
import re
import requests
import json
from pathlib import Path

class searchbot:
  '''
  Pasadena City College's Class Searching Bot
  Made by Jaeyoung Cho / Travis Cho

  Attributes
  ----------
  html: str
    File location of html file
  file_name: str, optional
    File location of form data file(json only) (Default: form_data.json)
  year: int, str, optional
    Year you are searching for (Default: 2021)
  term: str, optional
    Term you are searching for (Default: winter)
  init: bool, optional
    Initialize at the beginning or not

  Methods
  --------
  initialize(html=None)
    Fetch html file from url
  setData(year, term, file_name="form_data.json"
    Get form data from json
  getTable(crn):
    Search <tr> tags by crn
  getSeats(tr=None):
    Get available seats
  getProf()
    Get name of the professor
  saveHtml(file_name="pcc_semester.html")
    Save Html file to the drive

  Note
  -----
  The program does not always detect the wrong crns.
  Do not change Dummy value in Json file
  '''

  def __init__(self, html=None, file_name=None, year=None, term=None, init=True):
    # URL
    self._url = 'https://selfservice.pasadena.edu/prod/pw_psearch_sched.p_listthislist'
    self.form_data = None
    self.html = None
    self.tr = None
    self.dir = str(Path(__file__).parent.absolute())

    if init:
      # FORM DATA
      if file_name is None:
        self.setData(year, term) #Saved to self.form_data
      else:
        self.setData(year, term, file_name=file_name) #Saved to self.form_data

      # Initialize HTML if not assigned
      self.initialize(html=html) #Saved to self.html

  @property
  def url(self):
    return self._url

  def setData(self, year, term, file_name="/data/form_data.json"):
    '''Convert Json file to 2d-array
    form_data.json is a form data used for specifying your search

    Parameters
    -----------
    file_name: str, optional
      The file name of json. Default: 'form_data.json'
    year: int, str
      Year you are looking for
    term: str
      Term you are looking for
      Should be spring, summer, fall, winter (Case-insensitive)

    Raises
    ------
    ValueError
      If wrong semester is set
    FileNotFoundError
      If no json file found
    '''
    try:
      self.form_data = [
        ['TERM', str(year) + str(['winter', 'spring', 'summer', 'fall'].index(term.lower().strip()) * 2 + 1) + '0'],
        ['TERM_DESC', term.strip().lower().capitalize() + ' ' + str(year)],
      ]
    except ValueError:
      raise ValueError("Wrong Semester Input")

    try:
      with open(self.dir + file_name) as f:
        data = json.load(f)
    except FileNotFoundError:
      raise FileNotFoundError(self.dir + file_name + " file not found!")

    for key, value in data["data"].items():
      if(type(value) is str):
        self.form_data.append([key, value])
      else:
        for value1 in value:
          self.form_data.append([key, value1])

  def initialize(self, html=None):
    '''Assign user's html or request new html from server

    Parameters
    ----------
    html: str, optional
      File name of html file
      if not assign, fetch the file from self.url with form data
    '''
    if html is None:
      self.html = requests.post(self.url, data=self.form_data)
      self.html.raise_for_status() #RAISE ERROR IF 404 or 500
      self.html = self.html.text
    else:
      html_ = BeautifulSoup(html, 'html.parser')
      self.html = html_.prettify()

  def saveHtml(self, file_name="pcc_semester.html"):
    '''Save fetched html as a file

    Parameters
    ----------
    file_name: str, optional
      Name of the file as stored

    Raises
    --------
    NotImplementedError
      If html file is not set or initialized

    Returns
    --------
    Location of html file
    '''
    if self.html is None:
      raise NotImplementedError("No html found or initialize")
    html = open(self.dir + '/templates/' + file_name, 'w')
    html.write(self.html)
    html.close()
