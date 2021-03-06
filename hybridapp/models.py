from django.db import models
import requests
import json

import proselint
from enchant.checker import SpellChecker
import language_check
import execjs
import os
import sys
import math

# Create your models here.
class Bid(object):
    def __init__(self, text):
        self.text = text

    @staticmethod
    def get_quality_score(text):
        n_characters = len(text)
        n_errors = Bid.get_total_errors(text)[0]
        return math.atan(n_characters / ((n_errors ** 1.7) * 1.0)) / math.pi * 200
        
    @staticmethod
    def get_total_errors(text):
        n_errors = 0
        a = LanguageCheck.get_error_count(text)
        b = ProseLint.get_error_count(text)
        c = PyEnchant.get_error_count(text)
        d = Pedant.get_error_count(text)
        n_errors = a+b+c+d
        return n_errors, a, b, c, d
    
# Checks grammar and spelling
class LanguageCheck():
    @staticmethod
    def get_error_count(text):
        tool = language_check.LanguageTool('en-AU')
        matches = tool.check(text)
        return len(matches)
    
    @staticmethod
    def fix(text):
        tool = language_check.LanguageTool('en-AU')
        matches = tool.check(text)
        return language_check.correct(text, matches)
    
# Checks grammar
class ProseLint():
    @staticmethod
    def get_suggestions(text):
        suggestions = proselint.tools.lint(text)
        return suggestions

    @staticmethod
    def get_error_count(text):
        suggestions = proselint.tools.lint(text)
        return(len(suggestions))

        
# Checks spelling
# You need to install some dependecies for PyEnchant to work
# https://stackoverflow.com/questions/21083059/enchant-c-library-not-found-while-installing-pyenchant-using-pip-on-osx
# Reference for PyEnchant: http://pythonhosted.org/pyenchant/tutorial.html
class PyEnchant():
    @staticmethod
    def get_errors(text):
        checker = SpellChecker("en_AU")
        checker.set_text(text)
        return checker

    @staticmethod
    def get_error_count(text):
        checker = SpellChecker("en_AU")
        checker.set_text(text)
        return len(list(checker))
        
# Checks punctuation
# https://github.com/Decagon/Pedant 
# You need to:
# make init-js
# Uses this as reference: https://www.codementor.io/jstacoder/integrating-nodejs-python-how-to-write-cross-language-modules-pyexecjs-du107xfep
class Pedant():
    @staticmethod
    def get_error_count(lines):
        runtime = execjs.get('Node')
        context = runtime.compile('''
            module.paths.push('%s');
            var pedant = require('pedantjs');
            function validate(lines) {
                return pedant.validate(lines);
            }
        ''' % os.path.join(os.path.dirname(__file__),'node_modules'))

        result = context.call("validate", lines)
        return result

class Project(object):
    def __init__(self, title, description, budget, jobs):
        self._title = title
        self._description = description
        self._budget = budget
        self._jobs = jobs

    # Title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty")
        self._title = value

    # Description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if not value:
            raise ValueError("Description cannot be empty")
        if len(value) < 5:
            data = json.dumps(data)
        self._description = value

    # Budget
    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value


    # Jobs
    @property
    def jobs(self):
        return self._jobs

    @jobs.setter
    def jobs(self, value):
        self._jobs = value



class Budget(object):
    def __init__(self, minimum, maximum):
        self._max = maximum
        self._min = minimum

    # Maximum
    @property
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, value):
        if value < self.minimum:
            raise ValueError("maximum cannot be less than minimum")
        self._max = value

    # Minimum
    @property
    def minimum(self):
        return self._min

    @minimum.setter
    def minimum(self, value):
        if value > self.minimum:
            raise ValueError("minimum cannot be greater than maximum")
        self._min = value


class DBProject(models.Model):
    object_id = models.IntegerField(primary_key=True)

class DBProjectStore(object):
    def add_project(self, project):
        project.save()

    def get_project_ids(self):
        return [x.object_id for x in DBProject.objects.all()]

class ProjectStore(object):

    def post_project(self, project):
        headers = {
            'content-type': 'application/json',
            'freelancer-oauth-v1': employer_access_token,
        }

        params = (
            ('compact', ''),
        )

        data = {
            "title": project.title,
            "description": project.description,
            "currency": {
                "code": "AUD",
                "id": 3,
                "sign": "$"
            },
            "budget": {
                "minimum": project.budget.minimum,
                "maximum": project.budget.maximum
            },
            "jobs": [{"id": job_id} for job_id in project.jobs]
        }

        data = json.dumps(data)

        r = requests.post('https://www.freelancer-sandbox.com/api/projects/0.1/projects/',
                  headers=headers, params=params, data=data)

        project_id = r.json()["result"]["id"]

        # Print response
        print(r.json())

        return project_id



if __name__ == "__main__":
    budget = Budget(100, 200)
    project = Project("Matt Test", "Description test", budget, [3,17])
    store = ProjectStore()
    project_id = store.post_project(project)

    db_project = DBProject(project_id)
    db_project_store = DBProjectStore()
    db_project_store.add_project(db_project)
        


