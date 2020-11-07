class Repository:

  def __init__(self, name, url, forks, contributors):
    self.name = name
    self.url = url
    self.forks = forks
    self.contributors = contributors


class Contributor:
	
  def __init__(self, name, url, commits):
    self.name = name
    self.url = url
    self.commits = commits